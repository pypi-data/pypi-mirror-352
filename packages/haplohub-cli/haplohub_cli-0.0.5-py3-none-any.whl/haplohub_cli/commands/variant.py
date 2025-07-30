import click
from haplohub import GetVariantRequest

from haplohub_cli.core.api.client import client


@click.group()
def variant():
    """
    Work with variants
    """
    pass


@variant.command()
@click.argument("file", type=str, required=True)
@click.option("--accession", "-a", type=str, required=True)
@click.option("--start", "-s", type=int, required=True)
@click.option("--end", "-e", type=int, required=True)
@click.option("--cohort", "-c", type=str, required=True)
def fetch(file: str, accession: str, start: int, end: int, cohort: str):
    request = GetVariantRequest(
        file_name=file,
        accession=accession,
        start=start,
        end=end,
    )

    return client.variant.get_variant(cohort, request)
