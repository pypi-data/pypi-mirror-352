from enum import Enum
from dataclasses import dataclass
from typing import Any, Union, Dict


class ChangeType(Enum):
    """Types of changes that can occur to DICOM tags."""

    CHANGED = "Changed"
    CREATED = "Created"
    REMOVED = "Removed"


@dataclass
class DicomDifference:
    """Represents a difference between two DICOM datasets for a specific tag.

    Attributes
    ----------
    tag: Union[str, int]
        The DICOM tag in either string format (e.g. "0010,0010") or hexadecimal integer
    name: str
        The name of the DICOM element
    dataset_a_value: Any
        The value in the first dataset (or "Not Present in Dataset A")
    dataset_b_value: Any
        The value in the second dataset (or "Not Present in Dataset B")
    change_type: Union[ChangeType, str]
        Type of change (Changed, Created, or Removed)
    """

    tag: Union[str, int]
    name: str
    dataset_a_value: Any
    dataset_b_value: Any
    change_type: Union[ChangeType, str]

    def __post_init__(self):
        """Validate and convert types after initialization."""
        if isinstance(self.change_type, str):
            try:
                self.change_type = ChangeType[self.change_type]
            except KeyError as err:
                # Try to match value
                for change in ChangeType:
                    if change.value == self.change_type:
                        self.change_type = change
                        break
                else:
                    raise ValueError(
                        f"Invalid change type: {self.change_type}"
                    ) from err

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "tag": self.tag,
            "name": self.name,
            "dataset_a_value": self.dataset_a_value,
            "dataset_b_value": self.dataset_b_value,
            "change_type": (
                self.change_type.value
                if isinstance(self.change_type, ChangeType)
                else self.change_type
            ),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DicomDifference":
        """Create DicomDifference from dictionary representation."""
        return cls(
            tag=data["tag"],
            name=data["name"],
            dataset_a_value=data["dataset_a_value"],
            dataset_b_value=data["dataset_b_value"],
            change_type=data["change_type"],
        )

    def get_status_for_dataset(self, dataset_identifier: str) -> str:
        """Get the status for a specific dataset."""
        if dataset_identifier.lower() == "a":
            if self.dataset_a_value == "Not Present in Dataset A":
                return "Not Present"
            elif self.change_type == ChangeType.CREATED:
                return "Created"
            elif self.change_type == ChangeType.REMOVED:
                return "Unchanged"  # It exists in A but was removed in B
            else:
                return (
                    "Unchanged"
                    if self.dataset_b_value == "Not Present in Dataset B"
                    else "Changed"
                )
        elif dataset_identifier.lower() == "b":
            if self.dataset_b_value == "Not Present in Dataset B":
                return "Removed"
            elif self.change_type == ChangeType.CREATED:
                return "Created"
            elif self.change_type == ChangeType.REMOVED:
                return "Not Present"  # It was removed in B
            else:
                return "Changed"
        else:
            raise ValueError(f"Invalid dataset identifier: {dataset_identifier}")


def normalize_change_type(change_type: Union[ChangeType, str]) -> str:
    """Normalize change type to string representation."""
    if isinstance(change_type, ChangeType):
        return change_type.value
    elif change_type in [ct.value for ct in ChangeType]:
        return change_type
    elif change_type in [ct.name for ct in ChangeType]:
        return ChangeType[change_type].value
    else:
        raise ValueError(f"Invalid change type: {change_type}")
