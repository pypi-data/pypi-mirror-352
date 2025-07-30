[![CI](https://github.com/ResearchBureau/dicomdiff/actions/workflows/build.yml/badge.svg)](https://github.com/ResearchBureau/dicomdiff/actions/workflows/build.yml)
[![PyPI](https://img.shields.io/pypi/v/dicomdiff)](https://pypi.org/project/dicomdiff/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dicomdiff)](https://pypi.org/project/dicomdiff/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# Dicomdiff
A comprehensive Python module for analyzing DICOM file pseudonymization and de-identification processes. Dicomdiff enables researchers and healthcare professionals to evaluate, compare, and validate different pseudonymization methods by providing detailed analysis of how DICOM tags are transformed during de-identification.

## What Dicomdiff Does

**Core Functionality:**
- **Individual File Comparison**: Compare original DICOM files with their de-identified versions to detect specific changes
- **Pseudonymization Method Analysis**: Evaluate and compare different pseudonymization approaches across multiple files
- **Cross-Method Comparison**: Analyze how different pseudonymization tools handle the same source data
- **Consistency Validation**: Check whether pseudonymization methods behave consistently across datasets
- **Tag Transformation Tracking**: Monitor how specific DICOM tags are modified, removed, or preserved during pseudonymization


## Installation
Install the module using pip

```bash
  pip install dicomdiff
```

## Usage


### Compare two DICOM files in Python
```python
from dicomdiff.main import compare_dicom_files, print_differences

original_file = "path to original dcm file"
deidentified_file = "path to de-identified dcm file"

result = compare_dicom_files(original_file, deidentified_file) # compare the files
print_differences(result) # print the results
```

### Compare two pseudonymization methods
```python
from idiscore.defaults import create_default_core
from dicomdiff.pseudonymizer import InferredPseudonymizer
from dicomdiff.summary import generate_pseudonymization_summary

pseudonymizer_A = create_default_core()
pseudonymizer_B = InferredPseudonymizer(mapping, output_files)

# List of DICOM file paths to analyze
file_paths = ["path/to/file1.dcm", "path/to/file2.dcm"]

# Generate comparison summary
summary_df = generate_pseudonymization_summary(
    file_paths=file_paths,
    pseudonymizer_a=pseudonymizer_A,
    pseudonymizer_b=pseudonymizer_B
)
```

### Compare two DICOM files using CLI
```bash
# Compare two DICOM files
dicomdiff compare file1.dcm file2.dcm

# Filter results
dicomdiff compare file1.dcm file.dcm --changed
```

#### CLI Flags
| Flag | Description |
|------|-------------|
| `--changed` | Show only tags that have different values between files |
| `--removed` | Show only tags that exist in original but not in de-identified file |
| `--added` | Show only tags that exist in de-identified but not in original file |
| `--unchanged` | Show only tags that have identical values in both files |
