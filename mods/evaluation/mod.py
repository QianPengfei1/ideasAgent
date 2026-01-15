"""
Research Ideas Evaluation Mod for OpenAgents.

This mod provides comprehensive research idea evaluation including:
- Multi-criteria evaluation of research ideas
- Scoring based on technical feasibility, impact, novelty, and relevance
- Ranking and selection of top ideas
- Detailed evaluation reports
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from openagents.core.base_mod import BaseMod, mod_event_handler
from openagents.models.event import Event, EventVisibility
from openagents.models.event_response import EventResponse

logger = logging.getLogger(__name__)


class EvaluationNetworkMod(BaseMod):
    """Network-level mod for research ideas evaluation functionality."""

    def __init__(self, mod_name: str = "demos.09_research_ideas_network.mods.evaluation"):
        """Initialize the evaluation mod."""
        super().__init__(mod_name=mod_name)

        # Evaluation storage
        self.evaluations: Dict[str, Dict[str, Any]] = {}
        self.idea_scores: Dict[str, Dict[str, float]] = {}
        
        # Configuration
        self.evaluation_criteria = {
            "technical_feasibility": {"weight": 0.25, "description": "Technical feasibility and implementation difficulty"},
            "impact": {"weight": 0.30, "description": "Potential impact on the field and society"},
            "novelty": {"weight": 0.20, "description": "Novelty and innovation level"},
            "relevance": {"weight": 0.15, "description": "Relevance to current research trends"},
            "clarity": {"weight": 0.10, "description": "Clarity and articulation of the idea"}
        }
        
        logger.info(f"Initializing Research Ideas Evaluation mod")

    def initialize(self) -> bool:
        """Initialize the mod.

        Returns:
            bool: True if initialization was successful
        """
        logger.info("Research Ideas Evaluation mod initialized successfully")
        return True

    def shutdown(self) -> bool:
        """Shutdown the mod gracefully.

        Returns:
            bool: True if shutdown was successful
        """
        # Clear all state
        self.evaluations.clear()
        self.idea_scores.clear()
        
        logger.info("Research Ideas Evaluation mod shut down successfully")
        return True

    @mod_event_handler("idea.evaluate")
    async def handle_idea_evaluation(self, event: Event) -> Optional[EventResponse]:
        """Handle idea evaluation request from leader agent.

        Args:
            event: The evaluation request event

        Returns:
            EventResponse with evaluation results
        """
        try:
            ideas = event.payload.get("ideas", [])
            top_k = event.payload.get("top_k", 5)
            
            if not ideas:
                return EventResponse(
                    success=False,
                    message="No ideas provided for evaluation",
                    data={"error": "empty_ideas_list"}
                )
            
            # Rank ideas
            ranked_ideas = self.rank_ideas(ideas, top_k)
            
            # Extract scored ideas for response
            scored_ideas = []
            for item in ranked_ideas:
                scored_ideas.append({
                    "idea": item["idea"],
                    "evaluation": item["evaluation"]
                })
            
            logger.info(f"Evaluated {len(ideas)} ideas, returning top {len(scored_ideas)}")
            
            # Send event back to leader with evaluation results
            result_event = Event(
                event_name="idea.evaluated",
                source_id=self.mod_name,
                payload={
                    "scored_ideas": scored_ideas,
                    "total_evaluated": len(ideas),
                    "top_k_returned": len(scored_ideas)
                },
                relevant_mod=self.mod_name,
                visibility=EventVisibility.MOD_ONLY,
                target_agent_id=event.source_id
            )
            
            if self.network:
                await self.network.broadcast_event(result_event)
            
            return EventResponse(
                success=True,
                message=f"Successfully evaluated {len(ideas)} ideas",
                data={
                    "scored_ideas": scored_ideas,
                    "total_evaluated": len(ideas),
                    "top_k_returned": len(scored_ideas)
                }
            )
            
        except Exception as e:
            logger.error(f"Error evaluating ideas: {e}")
            return EventResponse(
                success=False,
                message=f"Error evaluating ideas: {str(e)}",
                data={"error": str(e)}
            )

    def evaluate_idea(self, idea: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a single research idea.

        Args:
            idea: The research idea to evaluate

        Returns:
            Dictionary containing evaluation results
        """
        idea_id = idea.get("id", "unknown")
        
        # Extract scores from reviews if available
        reviews = idea.get("reviews", [])
        technical_score = self._extract_score(reviews, "technical", 7.0)
        impact_score = self._extract_score(reviews, "impact", 7.0)
        
        # Calculate individual criterion scores
        scores = {
            "technical_feasibility": technical_score,
            "impact": impact_score,
            "novelty": self._assess_novelty(idea),
            "relevance": self._assess_relevance(idea),
            "clarity": self._assess_clarity(idea)
        }
        
        # Calculate weighted total score
        total_score = sum(
            scores[criterion] * self.evaluation_criteria[criterion]["weight"]
            for criterion in self.evaluation_criteria
        )
        
        # Store evaluation
        evaluation = {
            "idea_id": idea_id,
            "idea_title": idea.get("title", "Untitled"),
            "scores": scores,
            "total_score": round(total_score, 2),
            "criteria": self.evaluation_criteria,
            "strengths": self._identify_strengths(scores),
            "weaknesses": self._identify_weaknesses(scores),
            "recommendations": self._generate_recommendations(scores, idea)
        }
        
        self.evaluations[idea_id] = evaluation
        self.idea_scores[idea_id] = {"total": total_score, "individual": scores}
        
        return evaluation

    def rank_ideas(self, ideas: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        """Evaluate and rank a list of research ideas.

        Args:
            ideas: List of research ideas to evaluate
            top_k: Number of top ideas to return

        Returns:
            List of ranked ideas with evaluation results
        """
        # Evaluate all ideas
        evaluated_ideas = []
        for idea in ideas:
            evaluation = self.evaluate_idea(idea)
            evaluated_ideas.append({
                "idea": idea,
                "evaluation": evaluation
            })
        
        # Sort by total score (descending)
        ranked_ideas = sorted(
            evaluated_ideas,
            key=lambda x: x["evaluation"]["total_score"],
            reverse=True
        )
        
        # Return top K
        return ranked_ideas[:top_k]

    def generate_evaluation_report(self, ranked_ideas: List[Dict[str, Any]]) -> str:
        """Generate a comprehensive evaluation report.

        Args:
            ranked_ideas: List of ranked ideas with evaluations

        Returns:
            Formatted evaluation report
        """
        report = ["# Research Ideas Evaluation Report\n"]
        
        for idx, item in enumerate(ranked_ideas, 1):
            idea = item["idea"]
            evaluation = item["evaluation"]
            
            report.append(f"## {idx}. {evaluation['idea_title']}")
            report.append(f"**Overall Score:** {evaluation['total_score']}/10\n")
            
            report.append("### Detailed Scores:")
            for criterion, score in evaluation["scores"].items():
                weight = self.evaluation_criteria[criterion]["weight"]
                report.append(f"- **{criterion}:** {score}/10 (weight: {weight*100}%)")
            
            report.append("\n### Strengths:")
            for strength in evaluation["strengths"]:
                report.append(f"- {strength}")
            
            report.append("\n### Areas for Improvement:")
            for weakness in evaluation["weaknesses"]:
                report.append(f"- {weakness}")
            
            report.append("\n### Recommendations:")
            for rec in evaluation["recommendations"]:
                report.append(f"- {rec}")
            
            report.append("\n" + "-" * 80 + "\n")
        
        return "\n".join(report)

    def _extract_score(self, reviews: List[Dict], score_type: str, default: float) -> float:
        """Extract score from reviews.

        Args:
            reviews: List of reviews
            score_type: Type of score to extract (technical/impact)
            default: Default score if not found

        Returns:
            Extracted score
        """
        for review in reviews:
            critic = review.get("critic", "").lower()
            if score_type in critic:
                return review.get("review", {}).get("score", default)
        return default

    def _assess_novelty(self, idea: Dict[str, Any]) -> float:
        """Assess the novelty of an idea.

        Args:
            idea: The research idea

        Returns:
            Novelty score (0-10)
        """
        title = idea.get("title", "").lower()
        description = idea.get("description", "").lower()
        
        novelty_indicators = [
            "novel", "innovative", "breakthrough", "pioneering",
            "first", "new approach", "unprecedented", "groundbreaking"
        ]
        
        score = 5.0  # Base score
        for indicator in novelty_indicators:
            if indicator in title or indicator in description:
                score += 0.5
        
        return min(score, 10.0)

    def _assess_relevance(self, idea: Dict[str, Any]) -> float:
        """Assess the relevance of an idea.

        Args:
            idea: The research idea

        Returns:
            Relevance score (0-10)
        """
        description = idea.get("description", "").lower()
        
        relevance_indicators = [
            "current", "emerging", "trend", "recent", "state-of-the-art",
            "sota", "cutting-edge", "timely", "important"
        ]
        
        score = 5.0  # Base score
        for indicator in relevance_indicators:
            if indicator in description:
                score += 0.5
        
        return min(score, 10.0)

    def _assess_clarity(self, idea: Dict[str, Any]) -> float:
        """Assess the clarity of an idea.

        Args:
            idea: The research idea

        Returns:
            Clarity score (0-10)
        """
        title = idea.get("title", "")
        description = idea.get("description", "")
        
        score = 5.0  # Base score
        
        # Check for clear structure
        if len(title) > 5 and len(title) < 100:
            score += 1.0
        
        if len(description) > 50 and len(description) < 1000:
            score += 1.0
        
        # Check for key components
        if any(keyword in description.lower() for keyword in ["objective", "goal", "approach", "method"]):
            score += 1.0
        
        return min(score, 10.0)

    def _identify_strengths(self, scores: Dict[str, float]) -> List[str]:
        """Identify strengths based on scores.

        Args:
            scores: Dictionary of criterion scores

        Returns:
            List of strength descriptions
        """
        strengths = []
        for criterion, score in scores.items():
            if score >= 8.0:
                strengths.append(f"Excellent {criterion.replace('_', ' ')}")
            elif score >= 6.0:
                strengths.append(f"Good {criterion.replace('_', ' ')}")
        return strengths

    def _identify_weaknesses(self, scores: Dict[str, float]) -> List[str]:
        """Identify weaknesses based on scores.

        Args:
            scores: Dictionary of criterion scores

        Returns:
            List of weakness descriptions
        """
        weaknesses = []
        for criterion, score in scores.items():
            if score < 5.0:
                weaknesses.append(f"Needs improvement in {criterion.replace('_', ' ')}")
            elif score < 6.0:
                weaknesses.append(f"Moderate {criterion.replace('_', ' ')}")
        return weaknesses

    def _generate_recommendations(self, scores: Dict[str, float], idea: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on scores.

        Args:
            scores: Dictionary of criterion scores
            idea: The research idea

        Returns:
            List of recommendations
        """
        recommendations = []
        
        if scores.get("technical_feasibility", 0) < 6.0:
            recommendations.append("Consider simplifying the technical approach or breaking into smaller milestones")
        
        if scores.get("impact", 0) < 6.0:
            recommendations.append("Explore ways to increase potential impact or applications")
        
        if scores.get("novelty", 0) < 6.0:
            recommendations.append("Consider incorporating more innovative elements or novel approaches")
        
        if scores.get("clarity", 0) < 6.0:
            recommendations.append("Improve articulation of the idea with clearer objectives and methodology")
        
        if not recommendations:
            recommendations.append("This is a well-balanced idea with good potential")
        
        return recommendations