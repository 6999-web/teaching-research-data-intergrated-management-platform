"""
感悟总结生成服务

基于综合考核指标自动生成感悟总结，分析各教研室得分高低和指标达标情况。
需求: 15.1, 15.2, 15.3, 15.4, 15.5, 15.6
"""

from typing import Dict, List, Tuple
from sqlalchemy.orm import Session
from uuid import UUID

from app.models.self_evaluation import SelfEvaluation
from app.models.ai_score import AIScore
from app.models.manual_score import ManualScore
from app.models.final_score import FinalScore
from app.models.insight_summary import InsightSummary


class InsightGenerationService:
    """感悟总结生成服务类"""
    
    # 考核指标权重配置（可根据实际情况调整）
    INDICATOR_WEIGHTS = {
        "teaching_process_management": 0.20,  # 教学过程管理
        "course_construction": 0.15,  # 课程建设
        "teaching_reform_projects": 0.25,  # 教学改革项目
        "honorary_awards": 0.20,  # 荣誉表彰
        "teaching_quality": 0.20,  # 教学质量
    }
    
    # 得分等级阈值
    EXCELLENT_THRESHOLD = 85.0  # 优秀
    GOOD_THRESHOLD = 75.0  # 良好
    AVERAGE_THRESHOLD = 60.0  # 及格
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_insight_summary(self, evaluation_id: UUID) -> str:
        """
        生成感悟总结
        
        需求 15.1: 基于综合考核指标自动生成感悟总结
        需求 15.2: 分析各教研室得分高低
        需求 15.3: 分析各教研室指标达标情况
        需求 15.4: 包含突出指标说明
        需求 15.5: 包含待提升指标说明
        需求 15.6: 禁止人工填写感悟总结
        
        Args:
            evaluation_id: 自评表ID
            
        Returns:
            生成的感悟总结文本
        """
        # 获取评分数据
        evaluation = self._get_evaluation(evaluation_id)
        ai_score = self._get_ai_score(evaluation_id)
        manual_scores = self._get_manual_scores(evaluation_id)
        final_score = self._get_final_score(evaluation_id)
        
        if not final_score:
            raise ValueError(f"Final score not found for evaluation {evaluation_id}")
        
        # 分析指标得分情况
        indicator_analysis = self._analyze_indicators(ai_score, manual_scores)
        
        # 识别突出指标和待提升指标
        strong_indicators, weak_indicators = self._identify_strong_weak_indicators(
            indicator_analysis
        )
        
        # 生成总结文本
        summary = self._build_summary_text(
            final_score.final_score,
            strong_indicators,
            weak_indicators,
            indicator_analysis
        )
        
        return summary
    
    def save_insight_summary(self, evaluation_id: UUID, summary: str) -> InsightSummary:
        """
        保存感悟总结到数据库
        
        Args:
            evaluation_id: 自评表ID
            summary: 感悟总结文本
            
        Returns:
            InsightSummary对象
        """
        # 检查是否已存在
        existing = self.db.query(InsightSummary).filter(
            InsightSummary.evaluation_id == evaluation_id
        ).first()
        
        if existing:
            # 更新现有记录
            existing.summary = summary
            self.db.commit()
            self.db.refresh(existing)
            return existing
        
        # 创建新记录
        insight = InsightSummary(
            evaluation_id=evaluation_id,
            summary=summary
        )
        self.db.add(insight)
        self.db.commit()
        self.db.refresh(insight)
        
        return insight
    
    def generate_and_save(self, evaluation_id: UUID) -> InsightSummary:
        """
        生成并保存感悟总结
        
        Args:
            evaluation_id: 自评表ID
            
        Returns:
            InsightSummary对象
        """
        summary = self.generate_insight_summary(evaluation_id)
        return self.save_insight_summary(evaluation_id, summary)
    
    def _get_evaluation(self, evaluation_id: UUID) -> SelfEvaluation:
        """获取自评表"""
        evaluation = self.db.query(SelfEvaluation).filter(
            SelfEvaluation.id == evaluation_id
        ).first()
        
        if not evaluation:
            raise ValueError(f"Evaluation {evaluation_id} not found")
        
        return evaluation
    
    def _get_ai_score(self, evaluation_id: UUID) -> AIScore:
        """获取AI评分"""
        ai_score = self.db.query(AIScore).filter(
            AIScore.evaluation_id == evaluation_id
        ).first()
        
        return ai_score
    
    def _get_manual_scores(self, evaluation_id: UUID) -> List[ManualScore]:
        """获取所有手动评分"""
        manual_scores = self.db.query(ManualScore).filter(
            ManualScore.evaluation_id == evaluation_id
        ).all()
        
        return manual_scores
    
    def _get_final_score(self, evaluation_id: UUID) -> FinalScore:
        """获取最终得分"""
        final_score = self.db.query(FinalScore).filter(
            FinalScore.evaluation_id == evaluation_id
        ).first()
        
        return final_score
    
    def _analyze_indicators(
        self,
        ai_score: AIScore,
        manual_scores: List[ManualScore]
    ) -> Dict[str, float]:
        """
        分析各指标得分情况
        
        需求 15.2, 15.3: 分析各教研室得分高低和指标达标情况
        
        Args:
            ai_score: AI评分结果
            manual_scores: 手动评分列表
            
        Returns:
            指标名称到平均得分的映射
        """
        indicator_scores: Dict[str, List[float]] = {}
        
        # 收集AI评分的指标得分
        if ai_score and ai_score.indicator_scores:
            for item in ai_score.indicator_scores:
                indicator = item.get("indicator", "")
                score = float(item.get("score", 0))
                if indicator:
                    if indicator not in indicator_scores:
                        indicator_scores[indicator] = []
                    indicator_scores[indicator].append(score)
        
        # 收集手动评分的指标得分
        for manual_score in manual_scores:
            if manual_score.scores:
                for item in manual_score.scores:
                    indicator = item.get("indicator", "")
                    score = float(item.get("score", 0))
                    if indicator:
                        if indicator not in indicator_scores:
                            indicator_scores[indicator] = []
                        indicator_scores[indicator].append(score)
        
        # 计算每个指标的平均得分
        indicator_averages = {}
        for indicator, scores in indicator_scores.items():
            if scores:
                indicator_averages[indicator] = sum(scores) / len(scores)
        
        return indicator_averages
    
    def _identify_strong_weak_indicators(
        self,
        indicator_analysis: Dict[str, float]
    ) -> Tuple[List[Tuple[str, float]], List[Tuple[str, float]]]:
        """
        识别突出指标和待提升指标
        
        需求 15.4: 包含突出指标说明
        需求 15.5: 包含待提升指标说明
        
        Args:
            indicator_analysis: 指标分析结果
            
        Returns:
            (突出指标列表, 待提升指标列表)，每个元素为(指标名, 得分)元组
        """
        if not indicator_analysis:
            return [], []
        
        # 按得分排序
        sorted_indicators = sorted(
            indicator_analysis.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # 识别突出指标（得分>=良好阈值）
        strong_indicators = [
            (indicator, score)
            for indicator, score in sorted_indicators
            if score >= self.GOOD_THRESHOLD
        ]
        
        # 识别待提升指标（得分<及格阈值）
        weak_indicators = [
            (indicator, score)
            for indicator, score in sorted_indicators
            if score < self.AVERAGE_THRESHOLD
        ]
        
        # 如果没有明显的弱项，选择得分最低的指标
        if not weak_indicators and sorted_indicators:
            # 取得分最低的1-2个指标作为待提升项
            weak_indicators = sorted_indicators[-min(2, len(sorted_indicators)):]
        
        return strong_indicators, weak_indicators
    
    def _build_summary_text(
        self,
        final_score: float,
        strong_indicators: List[Tuple[str, float]],
        weak_indicators: List[Tuple[str, float]],
        indicator_analysis: Dict[str, float]
    ) -> str:
        """
        构建感悟总结文本
        
        需求 15.1, 15.4, 15.5: 生成包含突出指标和待提升指标的总结
        
        Args:
            final_score: 最终得分
            strong_indicators: 突出指标列表
            weak_indicators: 待提升指标列表
            indicator_analysis: 指标分析结果
            
        Returns:
            感悟总结文本
        """
        # 确定总体评价
        if final_score >= self.EXCELLENT_THRESHOLD:
            overall_assessment = "优秀"
            overall_comment = "在本次考评中表现突出，各项工作成效显著。"
        elif final_score >= self.GOOD_THRESHOLD:
            overall_assessment = "良好"
            overall_comment = "在本次考评中表现良好，整体工作扎实有效。"
        elif final_score >= self.AVERAGE_THRESHOLD:
            overall_assessment = "合格"
            overall_comment = "在本次考评中达到基本要求，但仍有较大提升空间。"
        else:
            overall_assessment = "待改进"
            overall_comment = "在本次考评中存在明显不足，需要重点改进。"
        
        # 构建总结文本
        summary_parts = []
        
        # 1. 总体评价
        summary_parts.append(
            f"本教研室在本年度工作考评中获得{overall_assessment}等级（{final_score:.2f}分），{overall_comment}"
        )
        
        # 2. 突出指标
        if strong_indicators:
            strong_names = [self._translate_indicator_name(ind) for ind, _ in strong_indicators[:3]]
            strong_scores = [f"{score:.2f}分" for _, score in strong_indicators[:3]]
            
            if len(strong_indicators) == 1:
                summary_parts.append(
                    f"在{strong_names[0]}方面表现突出，得分为{strong_scores[0]}，"
                    f"体现了教研室在该领域的扎实工作和显著成效。"
                )
            else:
                summary_parts.append(
                    f"在{self._join_chinese(strong_names)}等方面表现突出，"
                    f"分别获得{self._join_chinese(strong_scores)}，"
                    f"体现了教研室在这些领域的扎实工作和显著成效。"
                )
        
        # 3. 待提升指标
        if weak_indicators:
            weak_names = [self._translate_indicator_name(ind) for ind, _ in weak_indicators[:3]]
            weak_scores = [f"{score:.2f}分" for _, score in weak_indicators[:3]]
            
            if len(weak_indicators) == 1:
                summary_parts.append(
                    f"但在{weak_names[0]}方面有待提升，得分为{weak_scores[0]}，"
                    f"建议在今后工作中加强该方面的建设和投入。"
                )
            else:
                summary_parts.append(
                    f"但在{self._join_chinese(weak_names)}等方面有待提升，"
                    f"分别获得{self._join_chinese(weak_scores)}，"
                    f"建议在今后工作中加强这些方面的建设和投入。"
                )
        
        # 4. 改进建议
        if weak_indicators:
            suggestions = self._generate_suggestions(weak_indicators)
            if suggestions:
                summary_parts.append(
                    f"具体建议：{suggestions}"
                )
        
        # 5. 总结展望
        if final_score >= self.GOOD_THRESHOLD:
            summary_parts.append(
                "希望教研室继续保持优势，不断创新发展，为学院教学工作做出更大贡献。"
            )
        else:
            summary_parts.append(
                "希望教研室认真总结经验教训，针对薄弱环节制定改进措施，"
                "不断提升教学质量和管理水平。"
            )
        
        return "".join(summary_parts)
    
    def _translate_indicator_name(self, indicator: str) -> str:
        """
        将指标英文名称翻译为中文
        
        Args:
            indicator: 指标英文名称
            
        Returns:
            指标中文名称
        """
        translations = {
            "teaching_process_management": "教学过程管理",
            "course_construction": "课程建设",
            "teaching_reform_projects": "教学改革项目",
            "honorary_awards": "荣誉表彰",
            "teaching_quality": "教学质量",
            "scientific_research": "科研工作",
            "team_building": "团队建设",
            "student_guidance": "学生指导",
        }
        
        return translations.get(indicator, indicator)
    
    def _join_chinese(self, items: List[str]) -> str:
        """
        用中文顿号连接列表项
        
        Args:
            items: 字符串列表
            
        Returns:
            连接后的字符串
        """
        if not items:
            return ""
        if len(items) == 1:
            return items[0]
        if len(items) == 2:
            return f"{items[0]}和{items[1]}"
        
        return "、".join(items[:-1]) + f"和{items[-1]}"
    
    def _generate_suggestions(self, weak_indicators: List[Tuple[str, float]]) -> str:
        """
        根据待提升指标生成改进建议
        
        Args:
            weak_indicators: 待提升指标列表
            
        Returns:
            改进建议文本
        """
        suggestions_map = {
            "teaching_process_management": "加强教学过程的规范化管理，完善教学文档和记录",
            "course_construction": "推进课程改革和建设，提升课程质量和特色",
            "teaching_reform_projects": "积极申报和参与教学改革项目，推动教学创新",
            "honorary_awards": "鼓励教师参加各类教学竞赛，争取更多荣誉",
            "teaching_quality": "强化教学质量监控，提高学生满意度",
            "scientific_research": "加强科研工作，提升科研产出质量和数量",
            "team_building": "加强师资队伍建设，提升团队整体水平",
            "student_guidance": "加强对学生的指导和关怀，提高育人质量",
        }
        
        suggestions = []
        for indicator, _ in weak_indicators[:3]:
            suggestion = suggestions_map.get(indicator)
            if suggestion:
                suggestions.append(suggestion)
        
        if not suggestions:
            return "针对薄弱环节制定具体改进计划，明确责任人和时间节点。"
        
        return "；".join(suggestions) + "。"


def generate_insight_for_evaluation(db: Session, evaluation_id: UUID) -> InsightSummary:
    """
    为指定评估生成感悟总结的便捷函数
    
    Args:
        db: 数据库会话
        evaluation_id: 自评表ID
        
    Returns:
        InsightSummary对象
    """
    service = InsightGenerationService(db)
    return service.generate_and_save(evaluation_id)
