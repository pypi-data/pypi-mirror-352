from dataclasses import dataclass, field
from typing import Dict


@dataclass
class ComparisonConfig:
    """Configuration for pseudonymization comparison behavior.

    Attributes
    ----------
    strictness_levels: Dict
        Dict mapping status names to strictness levels
    phrases: Dict
        Dict of comparison result phrases
    """

    strictness_levels: Dict[str, int] = field(
        default_factory=lambda: {
            "Removed": 4,
            "Not Present": 3,
            "Changed": 2,
            "Created": 1,
            "Unchanged": 0,
        }
    )

    phrases: Dict[str, str] = field(
        default_factory=lambda: {
            "stricter": "{} is stricter",
            "more_lenient": "{} is more lenient",
            "both_equal": "Both methods are equal",
            "both_unchanged": "Both Unchanged",
            "both_not_present": "Both Not Present",
        }
    )

    def get_comparison_result(
        self, status_a: str, status_b: str, pseudo_b_name: str
    ) -> str:
        """Compare two pseudonymization statuses and return a description.

        Args
        ----
        status_a: str
            Status from first pseudonymizer
        status_b: str
            Status from second pseudonymizer
        pseudo_b_name: str
            Name of the second pseudonymizer

        Returns
        -------
        str
            String describing the comparison result
        """
        # Handle None values
        status_a_val = status_a if status_a else "Not Present"
        status_b_val = status_b if status_b else "Not Present"

        # Check for special cases
        if status_a_val == "Not Present" and status_b_val == "Not Present":
            return self.phrases["both_not_present"]

        if status_a_val == "Unchanged" and status_b_val == "Unchanged":
            return self.phrases["both_unchanged"]

        # Get strictness levels
        m1_strict = self.strictness_levels.get(status_a_val, 0)
        m2_strict = self.strictness_levels.get(status_b_val, 0)

        # Special cases for Not Present vs Unchanged
        if status_a_val == "Not Present" and status_b_val == "Unchanged":
            return self.phrases["stricter"].format(pseudo_b_name)
        if status_a_val == "Unchanged" and status_b_val == "Not Present":
            return self.phrases["more_lenient"].format(pseudo_b_name)

        # Compare strictness levels
        if m1_strict == m2_strict:
            return self.phrases["both_equal"]
        elif m1_strict > m2_strict:
            return self.phrases["more_lenient"].format(pseudo_b_name)
        else:
            return self.phrases["stricter"].format(pseudo_b_name)
