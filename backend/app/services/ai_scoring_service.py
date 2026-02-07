"""
AI评分服务模块

负责处理AI自动评分的核心逻辑，包括：
- 调用DeepSeek API进行评分
- 异常数据检测
- 附件分类
"""

import httpx
import json
from typing import Dict, List, Any, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from datetime import datetime
import logging
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)

from app.models.self_evaluation import SelfEvaluation
from app.models.attachment import Attachment
from app.models.ai_score import AIScore
from app.models.anomaly import Anomaly
from app.core.config import settings

logger = logging.getLogger(__name__)


class AIScoringService:
    """AI评分服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.api_key = settings.DEEPSEEK_API_KEY
        self.api_url = settings.DEEPSEEK_API_URL
    
    async def execute_ai_scoring(self, evaluation_id: UUID) -> AIScore:
        """
        执行AI评分主流程
        
        Args:
            evaluation_id: 自评表ID
            
        Returns:
            AIScore: AI评分结果
            
        Raises:
            ValueError: 如果自评表不存在或状态不正确
            Exception: 如果API调用失败
        """
        logger.info(f"开始执行AI评分，evaluation_id: {evaluation_id}")
        
        # 1. 获取自评表和附件
        evaluation = self.db.query(SelfEvaluation).filter(
            SelfEvaluation.id == evaluation_id
        ).first()
        
        if not evaluation:
            raise ValueError(f"自评表不存在: {evaluation_id}")
        
        if evaluation.status != "locked":
            raise ValueError(f"自评表状态不正确，当前状态: {evaluation.status}，需要状态: locked")
        
        attachments = self.db.query(Attachment).filter(
            Attachment.evaluation_id == evaluation_id
        ).all()
        
        if not attachments:
            raise ValueError(f"自评表没有附件: {evaluation_id}")
        
        # 2. 调用DeepSeek API进行评分
        logger.info(f"调用DeepSeek API进行评分")
        prompt = self._build_scoring_prompt(evaluation, attachments)
        ai_response = await self._call_deepseek_api(prompt)
        
        # 3. 解析AI响应
        logger.info(f"解析AI响应")
        score_data = self._parse_ai_response(ai_response)
        
        # 4. 保存AI评分结果
        ai_score = AIScore(
            evaluation_id=evaluation_id,
            total_score=score_data["total_score"],
            indicator_scores=score_data["indicator_scores"],
            parsed_reform_projects=score_data["parsed_reform_projects"],
            parsed_honorary_awards=score_data["parsed_honorary_awards"],
            scored_at=datetime.utcnow()
        )
        
        self.db.add(ai_score)
        
        # 5. 检测异常数据
        logger.info(f"检测异常数据")
        anomalies = self._detect_anomalies(evaluation, score_data)
        
        if anomalies:
            for anomaly in anomalies:
                self.db.add(anomaly)
            logger.warning(f"检测到 {len(anomalies)} 个异常数据")
        
        # 6. 分类附件 (需求 5.1, 5.2, 5.3, 5.5, 5.6)
        logger.info(f"开始分类附件")
        classified_count = self._classify_attachments(attachments, score_data)
        logger.info(f"附件分类完成，共分类 {classified_count} 个附件")
        
        # 7. 更新自评表状态
        evaluation.status = "ai_scored"
        evaluation.updated_at = datetime.utcnow()
        
        # 8. 提交事务
        self.db.commit()
        self.db.refresh(ai_score)
        
        logger.info(f"AI评分完成，score_id: {ai_score.id}, total_score: {ai_score.total_score}")
        
        return ai_score
    
    def _build_scoring_prompt(self, evaluation: SelfEvaluation, attachments: List[Attachment]) -> str:
        """
        构建评分提示词
        
        Args:
            evaluation: 自评表
            attachments: 附件列表
            
        Returns:
            str: 评分提示词
        """
        content = evaluation.content
        
        prompt = f"""你是教研室工作考评专家，请根据以下自评表内容和附件信息进行评分。

自评表内容：
- 教学过程管理：{content.get('teaching_process_management', '')}
- 课程建设：{content.get('course_construction', '')}
- 教学改革项目个数（自评填写）：{content.get('teaching_reform_projects', 0)}
- 荣誉表彰个数（自评填写）：{content.get('honorary_awards', 0)}

附件信息：
"""
        
        for i, attachment in enumerate(attachments, 1):
            prompt += f"{i}. 文件名：{attachment.file_name}，考核指标：{attachment.indicator}\n"
        
        prompt += """
预设分值标准（满分100分）：
1. 教学过程管理（25分）：
   - 优秀（22-25分）：教学文档齐全、管理规范、有创新举措
   - 良好（18-21分）：教学文档完整、管理规范
   - 合格（15-17分）：教学文档基本完整、管理基本规范
   - 不合格（0-14分）：教学文档不完整或管理不规范

2. 课程建设（25分）：
   - 优秀（22-25分）：课程体系完善、有特色课程、建设成效显著
   - 良好（18-21分）：课程体系完整、建设成效良好
   - 合格（15-17分）：课程体系基本完整、有一定建设成效
   - 不合格（0-14分）：课程体系不完整或建设成效不明显

3. 教学改革项目（25分）：
   - 每个项目5分，最多25分
   - 需要有附件证明材料支撑
   - 项目级别越高分值可适当上浮

4. 荣誉表彰（25分）：
   - 每个荣誉5分，最多25分
   - 需要有附件证明材料支撑
   - 荣誉级别越高分值可适当上浮

请按照以下格式返回评分结果（JSON格式）：
{
    "total_score": 总分（数字），
    "indicator_scores": [
        {
            "indicator": "考核指标名称",
            "score": 分数（数字），
            "reasoning": "评分理由"
        }
    ],
    "parsed_reform_projects": 从附件中解析出的教学改革项目个数（数字），
    "parsed_honorary_awards": 从附件中解析出的荣誉表彰个数（数字），
    "attachment_classifications": [
        {
            "file_name": "附件文件名",
            "classified_indicator": "teaching_reform_projects 或 honorary_awards 或 other"
        }
    ]
}

注意：
1. 请严格按照预设分值标准进行评分
2. 请仔细对比自评表填写的项目个数与附件中实际的项目个数
3. 如果个数不一致，请在parsed_reform_projects和parsed_honorary_awards中如实反映附件中的实际个数
4. 总分应该是所有指标分数的加权总和，不超过100分
5. 请根据附件文件名和内容，将每个附件分类到对应的考核指标（teaching_reform_projects、honorary_awards或other）
6. attachment_classifications数组中应包含所有附件的分类结果
"""
        
        return prompt
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    async def _call_deepseek_api(self, prompt: str) -> str:
        """
        调用DeepSeek API（使用tenacity实现重试机制）
        
        Args:
            prompt: 提示词
            
        Returns:
            str: API响应内容
            
        Raises:
            Exception: 如果API调用失败（重试3次后）
        """
        if not self.api_key:
            # 如果没有配置API密钥，返回模拟数据用于测试
            logger.warning("未配置DeepSeek API密钥，返回模拟数据")
            return self._get_mock_response()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": "你是教研室工作考评专家，负责根据自评表和附件进行客观公正的评分。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                logger.info(f"DeepSeek API调用成功")
                return content
                
        except (httpx.HTTPError, httpx.TimeoutException) as e:
            logger.error(f"DeepSeek API调用失败: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"DeepSeek API调用发生未预期错误: {str(e)}")
            raise Exception(f"DeepSeek API调用失败: {str(e)}")
    
    def _get_mock_response(self) -> str:
        """获取模拟响应数据（用于测试）"""
        mock_data = {
            "total_score": 85.5,
            "indicator_scores": [
                {
                    "indicator": "教学过程管理",
                    "score": 22.0,
                    "reasoning": "教学文档齐全、管理规范，符合优秀标准"
                },
                {
                    "indicator": "课程建设",
                    "score": 23.5,
                    "reasoning": "课程体系完善、有特色课程、建设成效显著，符合优秀标准"
                },
                {
                    "indicator": "教学改革项目",
                    "score": 15.0,
                    "reasoning": "根据附件解析出3个教学改革项目，每个5分"
                },
                {
                    "indicator": "荣誉表彰",
                    "score": 10.0,
                    "reasoning": "根据附件解析出2个荣誉表彰，每个5分"
                }
            ],
            "parsed_reform_projects": 3,
            "parsed_honorary_awards": 2,
            "attachment_classifications": []
        }
        return json.dumps(mock_data, ensure_ascii=False)
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """
        解析AI响应
        
        Args:
            response: AI响应内容
            
        Returns:
            Dict: 解析后的评分数据
        """
        try:
            # 尝试直接解析JSON
            data = json.loads(response)
            
            # 验证必需字段
            required_fields = ["total_score", "indicator_scores", "parsed_reform_projects", "parsed_honorary_awards"]
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"AI响应缺少必需字段: {field}")
            
            return data
            
        except json.JSONDecodeError:
            # 如果不是纯JSON，尝试提取JSON部分
            logger.warning("AI响应不是纯JSON格式，尝试提取JSON部分")
            
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group())
                    return data
                except:
                    pass
            
            raise ValueError(f"无法解析AI响应: {response}")
    
    def _detect_anomalies(self, evaluation: SelfEvaluation, score_data: Dict[str, Any]) -> List[Anomaly]:
        """
        检测异常数据
        
        实现需求 4.7, 4.8, 4.9, 4.10:
        - 4.7: 自动标记填写个数与附件解析个数不一致的数据
        - 4.8: 生成清晰的对比说明
        - 4.9: 异常信息保存到数据库，同步至管理端
        - 4.10: 设置status="pending"，转人工复核流程
        
        Args:
            evaluation: 自评表
            score_data: AI评分数据
            
        Returns:
            List[Anomaly]: 异常数据列表
        """
        anomalies = []
        content = evaluation.content
        
        # 检测教学改革项目数量不一致 (需求 4.4, 4.7, 4.8)
        declared_reform = content.get('teaching_reform_projects', 0)
        parsed_reform = score_data.get('parsed_reform_projects', 0)
        
        if declared_reform != parsed_reform:
            # 生成清晰的对比说明 (需求 4.8)
            description = self._generate_anomaly_description(
                indicator_name="教学改革项目",
                declared_count=declared_reform,
                parsed_count=parsed_reform
            )
            
            # 创建异常记录，status="pending"表示需要人工复核 (需求 4.7, 4.10)
            anomaly = Anomaly(
                evaluation_id=evaluation.id,
                type="count_mismatch",
                indicator="teaching_reform_projects",
                declared_count=declared_reform,
                parsed_count=parsed_reform,
                description=description,
                status="pending"  # 需求 4.10: 转人工复核流程
            )
            anomalies.append(anomaly)
            logger.warning(f"检测到异常: {description}")
        
        # 检测荣誉表彰数量不一致 (需求 4.5, 4.7, 4.8)
        declared_awards = content.get('honorary_awards', 0)
        parsed_awards = score_data.get('parsed_honorary_awards', 0)
        
        if declared_awards != parsed_awards:
            # 生成清晰的对比说明 (需求 4.8)
            description = self._generate_anomaly_description(
                indicator_name="荣誉表彰",
                declared_count=declared_awards,
                parsed_count=parsed_awards
            )
            
            # 创建异常记录，status="pending"表示需要人工复核 (需求 4.7, 4.10)
            anomaly = Anomaly(
                evaluation_id=evaluation.id,
                type="count_mismatch",
                indicator="honorary_awards",
                declared_count=declared_awards,
                parsed_count=parsed_awards,
                description=description,
                status="pending"  # 需求 4.10: 转人工复核流程
            )
            anomalies.append(anomaly)
            logger.warning(f"检测到异常: {description}")
        
        return anomalies
    
    def _generate_anomaly_description(
        self, 
        indicator_name: str, 
        declared_count: int, 
        parsed_count: int
    ) -> str:
        """
        生成清晰的异常对比说明 (需求 4.8)
        
        Args:
            indicator_name: 考核指标名称
            declared_count: 自评表声明的数量
            parsed_count: AI从附件解析出的数量
            
        Returns:
            str: 清晰的对比说明
        """
        diff = abs(declared_count - parsed_count)
        
        if declared_count > parsed_count:
            return (
                f"自评表填写{declared_count}项{indicator_name}，"
                f"但附件仅解析出{parsed_count}份证书，"
                f"缺少{diff}份支撑材料。"
                f"请核实是否存在遗漏上传或填写错误。"
            )
        else:
            return (
                f"自评表填写{declared_count}项{indicator_name}，"
                f"但附件解析出{parsed_count}份证书，"
                f"多出{diff}份材料。"
                f"请核实是否存在重复上传或分类错误。"
            )
    
    def _classify_attachments(self, attachments: List[Attachment], score_data: Dict[str, Any]) -> int:
        """
        根据AI评分结果自动分类附件 (需求 5.1, 5.2, 5.3, 5.5, 5.6)
        
        实现需求:
        - 5.1: 按考核指标自动分类附件
        - 5.2: 支持按"教学改革项目"指标分类附件
        - 5.3: 支持按"荣誉表彰"指标分类附件
        - 5.5: 关联附件与对应教研室（已通过evaluation_id关联）
        - 5.6: 关联附件与对应考核指标（通过indicator字段）
        
        Args:
            attachments: 附件列表
            score_data: AI评分数据，包含attachment_classifications字段
            
        Returns:
            int: 成功分类的附件数量
        """
        # 获取AI返回的附件分类结果
        classifications = score_data.get('attachment_classifications', [])
        
        if not classifications:
            logger.warning("AI响应中没有附件分类信息，跳过自动分类")
            return 0
        
        # 创建文件名到分类的映射
        classification_map = {
            item['file_name']: item['classified_indicator']
            for item in classifications
        }
        
        classified_count = 0
        
        # 更新每个附件的分类 (需求 5.1, 5.2, 5.3, 5.6)
        for attachment in attachments:
            # 查找该附件的AI分类结果
            ai_indicator = classification_map.get(attachment.file_name)
            
            if ai_indicator:
                # 只更新有效的分类指标 (需求 5.2, 5.3)
                if ai_indicator in ['teaching_reform_projects', 'honorary_awards', 'other']:
                    # 更新附件的考核指标 (需求 5.6)
                    attachment.indicator = ai_indicator
                    # 标记为AI分类 (需求 5.1)
                    attachment.classified_by = 'ai'
                    # 标记对象为已修改，确保SQLAlchemy跟踪变更
                    self.db.add(attachment)
                    classified_count += 1
                    
                    logger.info(
                        f"附件 {attachment.file_name} 已分类为 {ai_indicator} "
                        f"(evaluation_id: {attachment.evaluation_id})"
                    )
                else:
                    logger.warning(
                        f"附件 {attachment.file_name} 的分类指标无效: {ai_indicator}，"
                        f"保持原分类: {attachment.indicator}"
                    )
            else:
                logger.warning(
                    f"附件 {attachment.file_name} 未在AI分类结果中找到，"
                    f"保持原分类: {attachment.indicator}"
                )
        
        # 附件已通过evaluation_id与教研室关联 (需求 5.5)
        # evaluation_id -> SelfEvaluation -> teaching_office_id
        
        return classified_count
    
    def get_pending_anomalies(self, evaluation_id: Optional[UUID] = None) -> List[Anomaly]:
        """
        获取待处理的异常数据 (需求 4.9, 4.10)
        
        管理端可以调用此方法查询需要人工复核的异常数据
        
        Args:
            evaluation_id: 可选，指定自评表ID。如果不指定，返回所有待处理异常
            
        Returns:
            List[Anomaly]: 待处理的异常数据列表
        """
        query = self.db.query(Anomaly).filter(Anomaly.status == "pending")
        
        if evaluation_id:
            query = query.filter(Anomaly.evaluation_id == evaluation_id)
        
        return query.all()
