import click
from dicomdiff.main import compare_dicom_files, print_differences


@click.group()
def cli():
    pass


@cli.command()
@click.argument("dataset_a")
@click.argument("dataset_b")
@click.option("--changed", is_flag=True, help="Show only tags that were changed")
@click.option("--created", is_flag=True, help="Show only tags that were created")
@click.option("--removed", is_flag=True, help="Show only tags that were removed")
def compare(dataset_a, dataset_b, changed, created, removed):
    differences = compare_dicom_files(dataset_a, dataset_b)

    if any([changed, created, removed]):
        filtered_differences = []
        if changed:
            filtered_differences.extend(
                [d for d in differences if d["change_type"] == "Changed"]
            )
        if created:
            filtered_differences.extend(
                [d for d in differences if d["change_type"] == "Created"]
            )
        if removed:
            filtered_differences.extend(
                [d for d in differences if d["change_type"] == "Removed"]
            )
        differences = filtered_differences

    print_differences(differences)


if __name__ == "__main__":
    cli()
