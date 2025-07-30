import pandas as pd
import pydicom
from typing import List, Optional, Dict, Set, Tuple, Union
from dicomdiff.pseudonymizer import Pseudonymizer
from dicomdiff.main import compare_dicom_datasets
from dicomdiff.comparison import ComparisonConfig
from dicomdiff.datamodel import DicomDifference, ChangeType


class InconsistentPseudoError(Exception):
    pass


def generate_pseudonymization_summary(
    file_paths: List[str],
    pseudonymizer_a: Pseudonymizer,
    pseudonymizer_b: Pseudonymizer,
    pseudonymizer_a_name: str = "PseudoA",
    pseudonymizer_b_name: str = "PseudoB",
    output_csv: Optional[str] = None,
    check_consistency: bool = True,
    config: Optional[ComparisonConfig] = None,
) -> pd.DataFrame:
    """Generate a summary of pseudonymization differences between two pseudonymizers.

    Args
    ----
    file_paths: List[str]
        List of DICOM file paths to process
    pseudonymizer_a: Pseudonymizer
        First pseudonymizer instance
    pseudonymizer_b: Pseudonymizer
        Second pseudonymizer instance
    pseudonymizer_a_name: str
        Display name for the first pseudonymizer
    pseudonymizer_b_name: str
        Display name for the second pseudonymizer
    output_csv: str, optional
        Path to save CSV output
    check_consistency: bool
        Whether to check for inconsistencies
    config: ComparisonConfig, optional
        Configuration for comparison behavior

    Returns
    -------
    pd.DataFrame
        DataFrame with pseudonymization comparison results
    """
    if config is None:
        config = ComparisonConfig()

    tag_data = initialize_tag_data(
        pseudonymizer_a, pseudonymizer_b, pseudonymizer_a_name, pseudonymizer_b_name
    )
    tag_data = process_dicom_files(file_paths, tag_data, check_consistency)
    results = create_summary_results(tag_data)

    df = pd.DataFrame(results)
    df = df.sort_values("tag")

    if output_csv:
        df.to_csv(output_csv, index=False)
        print(f"Summary saved to {output_csv}")

    return df


def initialize_tag_data(
    pseudonymizer_a: Pseudonymizer,
    pseudonymizer_b: Pseudonymizer,
    pseudonymizer_a_name: str,
    pseudonymizer_b_name: str,
) -> Dict:
    """Initialize data structures for tracking tag information."""
    return {
        "tag_summary": {},
        "tag_methods": {},
        "seen_files": {},
        "all_tags": set(),
        "tag_existence": {},
        "pseudonymizers": {
            "a": pseudonymizer_a,
            "b": pseudonymizer_b,
        },
        "pseudonymizer_names": {
            "a": pseudonymizer_a_name,
            "b": pseudonymizer_b_name,
        },
    }


def process_dicom_files(
    file_paths: List[str], tag_data: Dict, check_consistency: bool
) -> Dict:
    """Process DICOM files and collect tag information."""
    for i, file_path in enumerate(file_paths):
        print(f"Processing file {i+1}/{len(file_paths)}: {file_path}")
        try:
            # Read the source DICOM file
            source_ds = pydicom.dcmread(file_path, force=True)

            process_source_dataset(source_ds, tag_data, file_path)
            process_pseudonymization_a(source_ds, tag_data, file_path)
            process_pseudonymization_b(source_ds, tag_data, file_path)
            track_tag_files(file_path, tag_data)

        except Exception as e:
            print(f"Error processing file {file_path}: {e}")

    tag_data["inconsistent_tags"] = set()

    if check_consistency:
        try:
            inconsistent_tags, error_msg = check_pseudonymization_consistency(
                tag_data["tag_methods"], tag_data["seen_files"]
            )

            if error_msg:
                # Store the inconsistent tags for filtering later
                tag_data["inconsistent_tags"] = inconsistent_tags

                # Log the inconsistency but continue processing
                print("")
                print(f"\033[33;1mWARNING:\033[0m\033[33m {error_msg}\033[0m")
                print(
                    f"\nRemoving {len(inconsistent_tags)} inconsistent tags from results:"
                )
                for tag in inconsistent_tags:
                    tag_name = (
                        tag_data["tag_summary"].get(tag, {}).get("name", "Unknown")
                    )
                    print(f"  - {tag} ({tag_name})")
                print("\nContinuing with analysis despite inconsistencies.")

                tag_data["consistency_warnings"] = error_msg

        except InconsistentPseudoError as e:
            print(
                f"Warning: {str(e)}\nContinuing with analysis despite inconsistencies."
            )
            tag_data["consistency_warnings"] = str(e)

    return tag_data


def process_source_dataset(source_ds, tag_data, file_path):
    tag_existence = tag_data["tag_existence"]
    tag_summary = tag_data["tag_summary"]
    all_tags = tag_data["all_tags"]

    for elem in source_ds:
        tag = format_tag(elem.tag)

        if tag not in tag_existence:
            tag_existence[tag] = {}
        if file_path not in tag_existence[tag]:
            tag_existence[tag][file_path] = {
                "source": False,
                "a": False,
                "b": False,
            }
        tag_existence[tag][file_path]["source"] = True

        all_tags.add(tag)
        if tag not in tag_summary:
            tag_summary[tag] = {"name": elem.name}


def process_pseudonymization_a(source_ds, tag_data, file_path):
    pseudo_a_name = tag_data["pseudonymizer_names"]["a"]
    try:
        pseudo_a = tag_data["pseudonymizers"]["a"]
        pseudo_a_ds = pseudo_a.pseudonimize(source_ds)

        track_tags_in_dataset(pseudo_a_ds, file_path, "a", tag_data)

        pseudo_a_diffs = compare_dicom_datasets(source_ds, pseudo_a_ds)

        process_differences(
            tag_data["tag_summary"],
            pseudo_a_diffs,
            pseudo_a_name,
            tag_data["tag_methods"],
            file_path,
            file_tags=set(),
            all_tags=tag_data["all_tags"],
        )
    except Exception as e:
        print(f"Error with {pseudo_a_name} for file {file_path}: {e}")


def process_pseudonymization_b(source_ds, tag_data, file_path):
    pseudo_b_name = tag_data["pseudonymizer_names"]["b"]
    try:
        pseudo_b = tag_data["pseudonymizers"]["b"]
        # Use copy to avoid modifying the original dataset
        pseudo_b_ds = pseudo_b.pseudonimize(source_ds.copy())

        source_tags = {format_tag(elem.tag) for elem in source_ds}

        track_tags_in_dataset(pseudo_b_ds, file_path, "b", tag_data, source_tags)

        pseudo_b_diffs = compare_dicom_datasets(source_ds, pseudo_b_ds)
        process_differences(
            tag_data["tag_summary"],
            pseudo_b_diffs,
            pseudo_b_name,
            tag_data["tag_methods"],
            file_path,
            file_tags=set(),
            all_tags=tag_data["all_tags"],
        )
    except Exception as e:
        print(f"Error with {pseudo_b_name} for file {file_path}: {e}")


def track_tags_in_dataset(ds, file_path, method, tag_data, source_tags=None):
    tag_existence = tag_data["tag_existence"]
    tag_summary = tag_data["tag_summary"]
    all_tags = tag_data["all_tags"]
    pseudo_name = tag_data["pseudonymizer_names"].get(method, method.upper())

    for elem in ds:
        tag = format_tag(elem.tag)
        if tag not in tag_existence:
            tag_existence[tag] = {}

        if file_path not in tag_existence[tag]:
            tag_existence[tag][file_path] = {
                "source": False,
                "a": False,
                "b": False,
            }
        tag_existence[tag][file_path][method] = True

        if method == "b" and source_tags is not None and tag not in source_tags:
            if tag not in tag_summary:
                tag_summary[tag] = {"name": elem.name}
            tag_summary[tag][pseudo_name] = "Created"

        all_tags.add(tag)


def track_tag_files(file_path, tag_data):
    all_tags = tag_data["all_tags"].copy()
    seen_files = tag_data["seen_files"]

    for tag in all_tags:
        if tag not in seen_files:
            seen_files[tag] = []
        seen_files[tag].append(file_path)


def create_summary_results(tag_data) -> List[Dict]:
    results = []
    all_tags = tag_data["all_tags"]
    tag_summary = tag_data["tag_summary"]
    tag_existence = tag_data["tag_existence"]
    inconsistent_tags = tag_data.get("inconsistent_tags", set())
    pseudo_a_name = tag_data["pseudonymizer_names"]["a"]
    pseudo_b_name = tag_data["pseudonymizer_names"]["b"]
    config = tag_data.get("config", ComparisonConfig())

    total_tags = len(all_tags)
    filtered_tags = all_tags - inconsistent_tags

    if inconsistent_tags:
        print(
            f"\nFiltering results: {len(filtered_tags)} of {total_tags} tags included"
        )
        print(f"Excluded {len(inconsistent_tags)} inconsistent tags")

    for tag in filtered_tags:
        info = tag_summary.get(tag, {})
        status_a, status_b = determine_tag_status(
            tag, info, tag_existence, pseudo_a_name, pseudo_b_name
        )

        result = {
            "tag": tag,
            "name": info.get("name", "Unknown"),
            pseudo_a_name: status_a,
            pseudo_b_name: status_b,
            "comparison": compare_methods(status_a, status_b, pseudo_b_name, config),
        }
        results.append(result)
    return results


def determine_tag_status(
    tag, info, tag_existence, pseudo_a_name, pseudo_b_name
) -> Tuple[str, str]:
    status_a = info.get(pseudo_a_name)
    status_b = info.get(pseudo_b_name)

    patterns = analyze_tag_existence_patterns(tag, tag_existence)

    pseudo_a_status = determine_pseudonymizer_status(status_a, patterns, "a")
    pseudo_b_status = determine_pseudonymizer_status(status_b, patterns, "b")

    return pseudo_a_status, pseudo_b_status


def analyze_tag_existence_patterns(tag, tag_existence) -> Dict:
    patterns = {
        "tag_only_in_source": False,
        "tag_only_in_a": False,
        "tag_only_in_b": False,
        "tag_in_source_and_a": False,
        "tag_in_source_and_b": False,
    }

    for _, existence_dict in tag_existence.get(tag, {}).items():
        source = existence_dict.get("source", False)
        a = existence_dict.get("a", False)
        b = existence_dict.get("b", False)

        if source and not a and not b:
            patterns["tag_only_in_source"] = True
        if not source and a and not b:
            patterns["tag_only_in_a"] = True
        if not source and not a and b:
            patterns["tag_only_in_b"] = True
        if source and a:
            patterns["tag_in_source_and_a"] = True
        if source and b:
            patterns["tag_in_source_and_b"] = True

    return patterns


def _get_status_from_patterns_for_method(
    patterns: Dict[str, bool], method: str
) -> Optional[str]:
    """Helper function to determine status based on patterns for a specific method."""
    if method == "a":
        if patterns["tag_only_in_a"]:
            return "Created"
        elif patterns["tag_in_source_and_a"]:
            return "Unchanged"
        elif patterns["tag_only_in_source"]:
            return "Removed"
    else:  # method == "b"
        if patterns["tag_only_in_b"]:
            return "Created"
        elif patterns["tag_in_source_and_b"]:
            return "Unchanged"
        elif patterns["tag_only_in_source"]:
            return "Removed"
    return None


def _check_removed_by_comparison(
    patterns: Dict[str, bool], method: str
) -> Optional[str]:
    """Helper to determine if tag was removed by comparing with the other method."""
    if method == "a" and (patterns["tag_in_source_and_b"] or patterns["tag_only_in_b"]):
        return "Removed"
    elif method == "b" and (
        patterns["tag_in_source_and_a"] or patterns["tag_only_in_a"]
    ):
        return "Removed"
    return None


def determine_pseudonymizer_status(
    change_status: str, patterns: Dict[str, bool], method: str
) -> str:
    """Determine the status for a tag with a specific pseudonymizer."""
    # If we already have an explicit status, use it
    if change_status:
        return change_status

    # Check for status based on patterns for this method
    status = _get_status_from_patterns_for_method(patterns, method)
    if status:
        return status

    # Check if the tag was removed compared to the other method
    status = _check_removed_by_comparison(patterns, method)
    if status:
        return status

    # Default case: tag doesn't exist in either dataset
    return "Not Present"


def format_tag(tag):
    if isinstance(tag, int):
        group = tag >> 16
        element = tag & 0xFFFF
        return f"{group:04x},{element:04x}"
    return str(tag)


def _normalize_diff_object(diff) -> DicomDifference:
    """Convert dictionary to DicomDifference if needed."""
    if not isinstance(diff, DicomDifference):
        return DicomDifference.from_dict(diff)
    return diff


def _extract_diff_values(diff: DicomDifference) -> Tuple[Union[str, int], str, str]:
    """Extract key values from a DicomDifference object."""
    tag_value = diff.tag
    name = diff.name
    change_type = (
        diff.change_type.value
        if isinstance(diff.change_type, ChangeType)
        else diff.change_type
    )
    return tag_value, name, change_type


def _update_tag_summary(tag_summary, tag, name, method, change_type):
    """Update the tag summary dictionary."""
    if tag not in tag_summary:
        tag_summary[tag] = {"name": name}

    # Only update if it's not already marked as Created
    already_created = tag_summary[tag].get(method) == "Created"
    if not already_created:
        tag_summary[tag][method] = change_type


def _update_tag_methods(tag_methods, tag, method, change_type, file_path):
    """Update the tag methods tracking."""
    if tag not in tag_methods:
        tag_methods[tag] = {}

    if method not in tag_methods[tag]:
        tag_methods[tag][method] = {}

    if change_type not in tag_methods[tag][method]:
        tag_methods[tag][method][change_type] = set()

    tag_methods[tag][method][change_type].add(file_path)


def process_differences(
    tag_summary: Dict[str, Dict[str, any]],
    differences: List[Union[DicomDifference, Dict[str, any]]],
    method: str,
    tag_methods: Dict[str, Dict[str, Dict[str, Set[str]]]] = None,
    file_path: str = None,
    file_tags: Set[str] = None,
    all_tags: Set[str] = None,
):
    """Process differences between datasets and update tracking structures."""
    for diff in differences:
        # Get normalized difference object and extract values
        diff = _normalize_diff_object(diff)
        tag_value, name, change_type = _extract_diff_values(diff)

        # Format the tag
        tag = format_tag(tag_value)

        # Update all_tags if provided
        if all_tags is not None:
            all_tags.add(tag)

        # Update tag summary
        _update_tag_summary(tag_summary, tag, name, method, change_type)

        # Update file_tags if provided
        if file_tags is not None:
            file_tags.add(tag)

        # Update tag_methods if provided
        if tag_methods is not None and file_path is not None:
            _update_tag_methods(tag_methods, tag, method, change_type, file_path)


def check_pseudonymization_consistency(tag_methods, files):
    """Check for inconsistencies in pseudonymization methods across files.

    Args
    ----
    tag_methods: Dict
        Dict containing tag methods and change types
    files: Dict
        Dict containing files where tags appear

    Returns
    -------
    tuple
        (set of inconsistent tags, error message)
    """
    inconsistencies = []
    inconsistent_tags = set()

    for tag, methods in tag_methods.items():
        for method_name, change_types in methods.items():
            if isinstance(change_types, dict) and len(change_types) > 1:
                inconsistent_tags.add(tag)

                # Create inconsistency record
                inconsistency = {
                    "tag": tag,
                    "method": method_name,
                    "change_types": list(change_types.keys()),
                    "files": {},
                }
                for change_type, file_set in change_types.items():
                    inconsistency["files"][change_type] = list(file_set)

                inconsistencies.append(inconsistency)

    # Prepare error message if inconsistencies exist
    if inconsistencies:
        error_msg = "Inconsistent pseudonymization detected:\n"
        for inc in inconsistencies:
            error_msg += (
                f"Tag {inc['tag']} was handled inconsistently by {inc['method']}:\n"
            )
            for change_type, files_list in inc["files"].items():
                file_examples = files_list[:3]  # Show at most 3 examples
                file_count = len(files_list)
                error_msg += (
                    f"  - {change_type}: {file_count} files, e.g., {file_examples}\n"
                )

        return inconsistent_tags, error_msg

    return set(), None


def compare_methods(status_a, status_b, pseudo_b_name, config=None):
    """
    Compare pseudonymization methods to determine which is stricter.

    Args
    ----
    status_a: Status of tag in first pseudonymizer
    status_b: Status of tag in second pseudonymizer
    pseudo_b_name: Name of second pseudonymizer
    config: Optional ComparisonConfig to use

    Returns
    -------
    String describing the comparison result
    """
    if config is None:
        config = ComparisonConfig()

    return config.get_comparison_result(status_a, status_b, pseudo_b_name)
