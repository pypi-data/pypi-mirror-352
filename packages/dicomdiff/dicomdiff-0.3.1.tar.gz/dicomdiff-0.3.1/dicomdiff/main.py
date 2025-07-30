import pydicom
from typing import List
from dicomdiff.datamodel import DicomDifference, ChangeType


def compare_dicom_datasets(dataset_a, dataset_b) -> List[DicomDifference]:
    """
    Compares DICOM tags between DICOM files.

    Args
    -----
        dataset_a: First DICOM dataset
        dataset_b: Second DICOM dataset

    Returns
    -------
        list: A list of DicomDifference objects representing differences
        between dataset_a and dataset_b DICOM files.
    """
    differences = []

    differences.extend(_compare_elements_in_b(dataset_a, dataset_b))
    differences.extend(_compare_elements_in_a(dataset_a, dataset_b))

    return differences


def _compare_elements_in_b(dataset_a, dataset_b):
    differences = []
    for elem in dataset_b:
        tag = elem.tag
        name = elem.name

        if tag in dataset_a:
            dataset_a_elem = dataset_a[tag]
            differences.extend(_compare_existing_tag(dataset_a_elem, elem, tag, name))
        else:
            differences.append(_create_difference(elem, tag, name))
    return differences


def _compare_existing_tag(dataset_a_elem, elem, tag, name):
    differences = []
    if elem.VR == "SQ":
        differences.extend(_compare_sequences(dataset_a_elem, elem, name))
    elif isinstance(elem.value, (bytes, bytearray)):
        if elem.value != dataset_a_elem.value:
            differences.append(_binary_difference(dataset_a_elem, elem, name, tag))

    elif elem.VR == "PN":
        if str(dataset_a_elem.value) != str(elem.value):
            differences.append(_value_difference(dataset_a_elem, elem, name, tag))

    elif hasattr(elem, "VM") and elem.VM > 1:
        if str(dataset_a_elem.value) != str(elem.value):
            differences.append(_value_difference(dataset_a_elem, elem, name, tag))

    elif dataset_a_elem.value != elem.value:
        differences.append(_value_difference(dataset_a_elem, elem, name, tag))
    return differences


def _compare_sequences(dataset_a_elem, elem, name):
    differences = []
    if dataset_a_elem.value != elem.value:
        for i, (item_a, item_b) in enumerate(zip(dataset_a_elem, elem, strict=True)):
            seq_diffs = compare_dicom_datasets(item_a, item_b)
            if seq_diffs:
                for diff in seq_diffs:
                    # If diff is a DicomDifference object, extract values
                    tag = diff.tag if hasattr(diff, "tag") else diff["tag"]
                    name_value = diff.name if hasattr(diff, "name") else diff["name"]
                    diff_name = f"{name}[{i}].{name_value}"

                    dataset_a_value = (
                        diff.dataset_a_value
                        if hasattr(diff, "dataset_a_value")
                        else diff["dataset_a_value"]
                    )
                    dataset_b_value = (
                        diff.dataset_b_value
                        if hasattr(diff, "dataset_b_value")
                        else diff["dataset_b_value"]
                    )
                    change_type = (
                        diff.change_type
                        if hasattr(diff, "change_type")
                        else diff["change_type"]
                    )

                    differences.append(
                        DicomDifference(
                            tag=tag,
                            name=diff_name,
                            dataset_a_value=dataset_a_value,
                            dataset_b_value=dataset_b_value,
                            change_type=change_type,
                        )
                    )
    return differences


def _binary_difference(dataset_a_elem, elem, name, tag):
    return DicomDifference(
        tag=tag,
        name=name,
        dataset_a_value=f"Binary data ({dataset_a_elem.VR}): {len(dataset_a_elem.value)} bytes",
        dataset_b_value=f"Binary data ({elem.VR}): {len(elem.value)} bytes",
        change_type=ChangeType.CHANGED,
    )


def _value_difference(dataset_a_elem, elem, name, tag):
    return DicomDifference(
        tag=tag,
        name=name,
        dataset_a_value=dataset_a_elem.value,
        dataset_b_value=elem.value,
        change_type=ChangeType.CHANGED,
    )


def _create_difference(elem, tag, name):
    if isinstance(elem.value, (bytes, bytearray)):
        value = f"Binary data ({elem.VR}): {len(elem.value)} bytes"
    elif elem.VR == "SQ" and not elem.value:
        value = f"Empty sequence ({elem.VR})"
    elif elem.value == "" or elem.value is None:
        value = f"Empty ({elem.VR})"
    elif hasattr(elem, "is_empty") and elem.is_empty:
        value = f"Empty ({elem.VR})"
    else:
        value = elem.value

    return DicomDifference(
        tag=tag,
        name=name,
        dataset_a_value="Not Present in Dataset A",
        dataset_b_value=value,
        change_type=ChangeType.CREATED,
    )


def _compare_elements_in_a(dataset_a, dataset_b):
    differences = []
    for elem in dataset_a:
        tag = elem.tag
        if tag not in dataset_b:
            value = (
                f"Binary data ({elem.VR}): {len(elem.value)} bytes"
                if isinstance(elem.value, (bytes, bytearray))
                else elem.value
            )
            differences.append(
                DicomDifference(
                    tag=tag,
                    name=elem.name,
                    dataset_a_value=value,
                    dataset_b_value="Not Present in Dataset B",
                    change_type=ChangeType.REMOVED,
                )
            )
    return differences


def compare_dicom_files(dataset_a_file, dataset_b_file):
    dataset_a = pydicom.dcmread(dataset_a_file)
    dataset_b = pydicom.dcmread(dataset_b_file)
    return compare_dicom_datasets(dataset_a, dataset_b)


def print_differences(differences):
    """
    Prints out the differences in a user-friendly format.

    Args
    ----
        differences (list): A list of DicomDifference objects.
    """
    if not differences:
        print("No differences found.")
        return

    for diff in differences:
        print("-" * 50)
        tag = diff.tag if hasattr(diff, "tag") else diff["tag"]
        name = diff.name if hasattr(diff, "name") else diff["name"]
        ds_a_val = (
            diff.dataset_a_value
            if hasattr(diff, "dataset_a_value")
            else diff["dataset_a_value"]
        )
        ds_b_val = (
            diff.dataset_b_value
            if hasattr(diff, "dataset_b_value")
            else diff["dataset_b_value"]
        )
        change_type = (
            diff.change_type.value
            if hasattr(diff, "change_type") and hasattr(diff.change_type, "value")
            else diff["change_type"]
        )

        print(f"Tag: {tag}, Name: {name}")
        print(f"  Dataset A Value: {ds_a_val}")
        print(f"  Dataset B Value: {ds_b_val}")
        print(f"  Change Type: {change_type}")
