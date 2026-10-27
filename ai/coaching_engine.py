"""Public coaching interface for AR Sports Coach."""

from typing import Any, Dict, Optional

from .feedback_rules import FeedbackRuleEngine


class CoachingEngine:
    """Convert analysis metrics into understandable coaching feedback."""

    def __init__(
        self,
        rules: Optional[FeedbackRuleEngine] = None,
    ):
        self.rules = rules or FeedbackRuleEngine()

    def generate_feedback(
        self,
        metrics: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate feedback for one analysis result."""
        return self.rules.evaluate(metrics)

    def generate(
        self,
        metrics: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Convenience alias for generate_feedback()."""
        return self.generate_feedback(metrics)
