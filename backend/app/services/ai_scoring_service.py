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
        构建评分提示词（支持新评分表结构）
        
        Args:
            evaluation: 自评表
            attachments: 附件列表
            
        Returns:
            str: 评分提示词
        """
        content = evaluation.content
        
        # 提取常规教学工作内容
        regular_teaching = content.get('regularTeaching', {})
        
        # 提取特色与亮点项目
        highlights = content.get('highlights', {})
        reform_projects = highlights.get('teachingReformProjects', {}).get('items', [])
        honors = highlights.get('teachingHonors', {}).get('items', [])
        competitions = highlights.get('teachingCompetitions', {}).get('items', [])
        innovations = highlights.get('innovationCompetitions', {}).get('items', [])
        
        # 提取负面清单
        negative_list = content.get('negativeList', {})
        
        prompt = f"""你是教研室工作考评专家，请根据以下自评表内容和附件信息进行评分。

一、常规教学工作（每项满分10分，共80分）

1. 教学过程管理（自评分：{regular_teaching.get('teachingProcessManagement', {}).get('selfScore', 0)}分）
   内容：{regular_teaching.get('teachingProcessManagement', {}).get('content', '')}

2. 教学质量管理（自评分：{regular_teaching.get('teachingQualityManagement', {}).get('selfScore', 0)}分）
   内容：{regular_teaching.get('teachingQualityManagement', {}).get('content', '')}

3. 课程考核（自评分：{regular_teaching.get('courseAssessment', {}).get('selfScore', 0)}分）
   内容：{regular_teaching.get('courseAssessment', {}).get('content', '')}

4. 教育教学科研工作（自评分：{regular_teaching.get('educationResearch', {}).get('selfScore', 0)}分）
   内容：{regular_teaching.get('educationResearch', {}).get('content', '')}

5. 课程建设（自评分：{regular_teaching.get('courseConstruction', {}).get('selfScore', 0)}分）
   内容：{regular_teaching.get('courseConstruction', {}).get('content', '')}

6. 教师队伍建设（自评分：{regular_teaching.get('teacherTeamBuilding', {}).get('selfScore', 0)}分）
   内容：{regular_teaching.get('teacherTeamBuilding', {}).get('content', '')}

7. 科学研究与学术交流（自评分：{regular_teaching.get('researchAndExchange', {}).get('selfScore', 0)}分）
   内容：{regular_teaching.get('researchAndExchange', {}).get('content', '')}

8. 教学档案室管理与建设（自评分：{regular_teaching.get('archiveManagement', {}).get('selfScore', 0)}分）
   内容：{regular_teaching.get('archiveManagement', {}).get('content', '')}

二、特色与亮点项目

1. 教学改革项目（自评填写{len(reform_projects)}项）：
"""
        
        for i, project in enumerate(reform_projects, 1):
            prompt += f"   {i}. {project.get('name', '')} - {project.get('level', '')} - 自评{project.get('score', 0)}分\n"
        
        prompt += f"\n2. 年度获得教学相关荣誉表彰（自评填写{len(honors)}项）：\n"
        for i, honor in enumerate(honors, 1):
            prompt += f"   {i}. {honor.get('name', '')} - {honor.get('level', '')} - 自评{honor.get('score', 0)}分\n"
        
        prompt += f"\n3. 教学比赛（自评填写{len(competitions)}项）：\n"
        for i, comp in enumerate(competitions, 1):
            prompt += f"   {i}. {comp.get('name', '')} - {comp.get('levelPrize', '')} - 自评{comp.get('score', 0)}分\n"
        
        prompt += f"\n4. 指导创新创业比赛获奖情况（自评填写{len(innovations)}项）：\n"
        for i, innov in enumerate(innovations, 1):
            prompt += f"   {i}. {innov.get('name', '')} - {innov.get('levelPrize', '')} - 自评{innov.get('score', 0)}分\n"
        
        prompt += f"""
三、负面清单

1. 师德师风违规：{negative_list.get('ethicsViolations', {}).get('count', 0)}起，扣{negative_list.get('ethicsViolations', {}).get('deduction', 0)}分
2. 教学事故：{negative_list.get('teachingAccidents', {}).get('count', 0)}起，扣{negative_list.get('teachingAccidents', {}).get('deduction', 0)}分
3. 意识形态问题：{negative_list.get('ideologyIssues', {}).get('count', 0)}起，扣{negative_list.get('ideologyIssues', {}).get('deduction', 0)}分
4. 工作量未完成：{negative_list.get('workloadIncomplete', {}).get('percentage', 0)}%，扣{negative_list.get('workloadIncomplete', {}).get('deduction', 0)}分

附件信息（共{len(attachments)}个）：
"""
        
        for i, attachment in enumerate(attachments, 1):
            prompt += f"{i}. 文件名：{attachment.file_name}，考核指标：{attachment.indicator}\n"
        
        prompt += """
评分任务：

1. 对8个常规教学指标进行AI评分（每项0-10分）
2. 验证特色亮点项目的附件支撑材料是否充分
3. 检测自评填写的项目数量与附件数量是否一致
4. 对附件进行分类（教学改革项目/荣誉表彰/教学比赛/创新创业比赛/其他）

请按照以下JSON格式返回评分结果：
{
    "total_score": AI评定的总分（数字，包含负面清单扣分），
    "indicator_scores": [
        {
            "indicator": "教学过程管理",
            "score": AI评分（0-10），
            "reasoning": "评分理由，需要对比自评分和AI评分的差异"
        },
        {
            "indicator": "教学质量管理",
            "score": AI评分（0-10），
            "reasoning": "评分理由"
        },
        {
            "indicator": "课程考核",
            "score": AI评分（0-10），
            "reasoning": "评分理由"
        },
        {
            "indicator": "教育教学科研工作",
            "score": AI评分（0-10），
            "reasoning": "评分理由"
        },
        {
            "indicator": "课程建设",
            "score": AI评分（0-10），
            "reasoning": "评分理由"
        },
        {
            "indicator": "教师队伍建设",
            "score": AI评分（0-10），
            "reasoning": "评分理由"
        },
        {
            "indicator": "科学研究与学术交流",
            "score": AI评分（0-10），
            "reasoning": "评分理由"
        },
        {
            "indicator": "教学档案室管理与建设",
            "score": AI评分（0-10），
            "reasoning": "评分理由"
        }
    ],
    "parsed_reform_projects": 从附件中解析出的教学改革项目个数（数字），
    "parsed_honors": 从附件中解析出的荣誉表彰个数（数字），
    "parsed_competitions": 从附件中解析出的教学比赛个数（数字），
    "parsed_innovations": 从附件中解析出的创新创业比赛个数（数字），
    "attachment_classifications": [
        {
            "file_name": "附件文件名",
            "classified_indicator": "teaching_reform_projects 或 teaching_honors 或 teaching_competitions 或 innovation_competitions 或 other"
        }
    ]
}

注意事项：
1. 常规教学工作每项满分10分，请根据内容质量客观评分
2. 如果自评分明显偏高或偏低，请在reasoning中说明
3. 特色亮点项目需要有附件支撑，请仔细核对数量
4. 负面清单扣分已在自评表中计算，AI评分时需要考虑
5. 附件分类要准确，便于后续管理和审核
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
            "total_score": 78.5,
            "indicator_scores": [
                {
                    "indicator": "教学过程管理",
                    "score": 8.5,
                    "reasoning": "教学文档齐全、管理规范，自评分9分略高，AI评定8.5分"
                },
                {
                    "indicator": "教学质量管理",
                    "score": 9.0,
                    "reasoning": "教学质量管理制度完善，执行到位，符合优秀标准"
                },
                {
                    "indicator": "课程考核",
                    "score": 8.0,
                    "reasoning": "课程考核规范，试题库建设良好"
                },
                {
                    "indicator": "教育教学科研工作",
                    "score": 9.5,
                    "reasoning": "教研活动丰富，成效显著"
                },
                {
                    "indicator": "课程建设",
                    "score": 9.0,
                    "reasoning": "课程体系完善，有特色课程"
                },
                {
                    "indicator": "教师队伍建设",
                    "score": 8.5,
                    "reasoning": "教师培养规划清晰，执行良好"
                },
                {
                    "indicator": "科学研究与学术交流",
                    "score": 8.0,
                    "reasoning": "科研项目和学术交流活动较为活跃"
                },
                {
                    "indicator": "教学档案室管理与建设",
                    "score": 9.0,
                    "reasoning": "档案管理规范，归档及时"
                }
            ],
            "parsed_reform_projects": 3,
            "parsed_honors": 2,
            "parsed_competitions": 1,
            "parsed_innovations": 2,
            "attachment_classifications": []
        }
        return json.dumps(mock_data, ensure_ascii=False)
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """
        解析AI响应（支持新评分表结构）
        
        Args:
            response: AI响应内容
            
        Returns:
            Dict: 解析后的评分数据
        """
        try:
            # 尝试直接解析JSON
            data = json.loads(response)
            
            # 验证必需字段
            required_fields = [
                "total_score", 
                "indicator_scores", 
                "parsed_reform_projects", 
                "parsed_honors",
                "parsed_competitions",
                "parsed_innovations"
            ]
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
        检测异常数据（支持新评分表结构）
        
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
        highlights = content.get('highlights', {})
        
        # 检测教学改革项目数量不一致
        declared_reform = len(highlights.get('teachingReformProjects', {}).get('items', []))
        parsed_reform = score_data.get('parsed_reform_projects', 0)
        
        if declared_reform != parsed_reform:
            description = self._generate_anomaly_description(
                indicator_name="教学改革项目",
                declared_count=declared_reform,
                parsed_count=parsed_reform
            )
            
            anomaly = Anomaly(
                evaluation_id=evaluation.id,
                type="count_mismatch",
                indicator="teaching_reform_projects",
                declared_count=declared_reform,
                parsed_count=parsed_reform,
                description=description,
                status="pending"
            )
            anomalies.append(anomaly)
            logger.warning(f"检测到异常: {description}")
        
        # 检测荣誉表彰数量不一致
        declared_honors = len(highlights.get('teachingHonors', {}).get('items', []))
        parsed_honors = score_data.get('parsed_honors', 0)
        
        if declared_honors != parsed_honors:
            description = self._generate_anomaly_description(
                indicator_name="荣誉表彰",
                declared_count=declared_honors,
                parsed_count=parsed_honors
            )
            
            anomaly = Anomaly(
                evaluation_id=evaluation.id,
                type="count_mismatch",
                indicator="teaching_honors",
                declared_count=declared_honors,
                parsed_count=parsed_honors,
                description=description,
                status="pending"
            )
            anomalies.append(anomaly)
            logger.warning(f"检测到异常: {description}")
        
        # 检测教学比赛数量不一致
        declared_competitions = len(highlights.get('teachingCompetitions', {}).get('items', []))
        parsed_competitions = score_data.get('parsed_competitions', 0)
        
        if declared_competitions != parsed_competitions:
            description = self._generate_anomaly_description(
                indicator_name="教学比赛",
                declared_count=declared_competitions,
                parsed_count=parsed_competitions
            )
            
            anomaly = Anomaly(
                evaluation_id=evaluation.id,
                type="count_mismatch",
                indicator="teaching_competitions",
                declared_count=declared_competitions,
                parsed_count=parsed_competitions,
                description=description,
                status="pending"
            )
            anomalies.append(anomaly)
            logger.warning(f"检测到异常: {description}")
        
        # 检测创新创业比赛数量不一致
        declared_innovations = len(highlights.get('innovationCompetitions', {}).get('items', []))
        parsed_innovations = score_data.get('parsed_innovations', 0)
        
        if declared_innovations != parsed_innovations:
            description = self._generate_anomaly_description(
                indicator_name="创新创业比赛",
                declared_count=declared_innovations,
                parsed_count=parsed_innovations
            )
            
            anomaly = Anomaly(
                evaluation_id=evaluation.id,
                type="count_mismatch",
                indicator="innovation_competitions",
                declared_count=declared_innovations,
                parsed_count=parsed_innovations,
                description=description,
                status="pending"
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
        根据AI评分结果自动分类附件（支持新评分表结构）
        
        实现需求:
        - 5.1: 按考核指标自动分类附件
        - 5.2: 支持按"教学改革项目"指标分类附件
        - 5.3: 支持按"荣誉表彰"指标分类附件
        - 5.4: 支持按"教学比赛"指标分类附件
        - 5.5: 支持按"创新创业比赛"指标分类附件
        - 5.6: 关联附件与对应教研室（已通过evaluation_id关联）
        - 5.7: 关联附件与对应考核指标（通过indicator字段）
        
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
        
        # 有效的分类指标
        valid_indicators = [
            'teaching_reform_projects',
            'teaching_honors', 
            'teaching_competitions',
            'innovation_competitions',
            'other'
        ]
        
        # 更新每个附件的分类
        for attachment in attachments:
            # 查找该附件的AI分类结果
            ai_indicator = classification_map.get(attachment.file_name)
            
            if ai_indicator:
                # 只更新有效的分类指标
                if ai_indicator in valid_indicators:
                    # 更新附件的考核指标
                    attachment.indicator = ai_indicator
                    # 标记为AI分类
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
        
        # 附件已通过evaluation_id与教研室关联
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
