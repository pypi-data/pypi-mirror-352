import pydicom
import os
import csv
from copy import deepcopy
from abc import ABC, abstractmethod
from typing import Dict, Optional, Union
from pathlib import Path
from idiscore.core import Core, Profile
from idiscore.defaults import get_dicom_rule_sets


class Pseudonymizer(ABC):
    @abstractmethod
    def pseudonimize(self, ds: pydicom.Dataset) -> pydicom.Dataset:
        """Pseudonymize a DICOM dataset.

        Args
        ----
        dataset
            The DICOM dataset to pseudonymize

        Returns
        -------
        Dataset
            The pseudonymized dataset
        """
        pass


class InferredPseudonymizer(Pseudonymizer):
    def __init__(
        self, mapping: Dict[str, Union[str, Path]], output_dir: Optional[str] = None
    ):
        """Pseudonymizer that infers rules from examples.

        Args
        ----
        mapping: Dict[str, Union[str, Path]]
            Mapping of original DICOM identifiers (e.g., SOPInstanceUID) to file paths
            of their corresponding pseudonymized DICOM files
        output_dir: str, optional
            Base directory containing pseudonymized files. If provided and mapping values
            are relative paths, they will be joined with this directory
        """
        self.mapping = mapping
        self.output_dir = output_dir

    def pseudonimize(self, ds: pydicom.Dataset) -> pydicom.Dataset:
        """Return the pre-pseudonymized version of the dataset based on the mapping.

        Args
        ----
        ds: pydicom.Dataset
            Original DICOM dataset

        Returns
        -------
        pydicom.Dataset
            Pre-pseudonymized DICOM dataset from the mapped file
        """
        # Get the SOPInstanceUID from the dataset
        try:
            sop_instance_uid = ds.SOPInstanceUID
        except AttributeError as err:
            raise ValueError("Dataset does not contain SOPInstanceUID tag") from err

        if sop_instance_uid not in self.mapping:
            raise ValueError(
                f"SOPInstanceUID {sop_instance_uid} not found in pseudonymizer mapping"
            )

        target_path = self.mapping[sop_instance_uid]

        # If output_dir is provided and target_path is relative, join them
        if self.output_dir and not os.path.isabs(target_path):
            target_path = os.path.join(self.output_dir, target_path)

        if not os.path.exists(target_path):
            raise FileNotFoundError(
                f"Mapped pseudonymized file does not exist: {target_path}. "
                f"Check if the output_dir parameter is set correctly: {self.output_dir}"
            )

        return pydicom.dcmread(target_path)

    @classmethod
    def from_csv(
        cls,
        csv_path: str,
        output_dir: Optional[str] = None,
        id_col: str = "SOPInstanceUID",
        target_col: str = "path_deidentified",
    ) -> "InferredPseudonymizer":
        """Create pseudonymizer from a CSV mapping file.

        Args
        ----
        csv_path: str
            Path to CSV file containing mappings from original DICOM identifiers
            to pseudonymized file paths
        output_dir: str, optional
            Base directory containing pseudonymized files. If provided and CSV
            contains relative paths, they will be joined with this directory
        id_col: str, default "SOPInstanceUID"
            Column name in CSV containing original DICOM identifiers
        target_col: str, default "path_deidentified"
            Column name in CSV containing paths to pseudonymized DICOM files

        Returns
        -------
        InferredPseudonymizer
            New pseudonymizer instance with mapping loaded from CSV
        """
        mapping = {}

        with open(csv_path, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                sop_instance_uid = row[id_col].strip()
                target_path = row[target_col].strip()
                mapping[sop_instance_uid] = target_path

        return cls(mapping, output_dir)


class IDISPseudonymizer(Pseudonymizer):

    def pseudonimize(self, ds: pydicom.Dataset) -> pydicom.Dataset:
        """Implementation of the IDIS pseudonymization algorithm.

        Attributes
        ----------
        uid_map: Dict
            Mapping of original UIDs to pseudonymized UIDs
        """
        sets = get_dicom_rule_sets()
        profile = Profile(rule_sets=[sets.basic_profile])
        core = Core(profile)
        ds_copy = deepcopy(ds)
        pseudonymized_ds = core.deidentify(ds_copy)
        return pseudonymized_ds
