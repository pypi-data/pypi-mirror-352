from haplohub import ResultListResponseVariantSchema
from rich.table import Table

from haplohub_cli.formatters.decorators import register


@register(ResultListResponseVariantSchema)
def format_variants(data: ResultListResponseVariantSchema):
    table = Table(title="Variants", caption=f"Total: {len(data.items)}")
    table.add_column("Accession")
    table.add_column("Position")
    table.add_column("Id")
    table.add_column("Reference")
    table.add_column("Alternate")
    table.add_column("Quality")

    for item in data.items:
        table.add_row(
            item.accession,
            str(item.position),
            item.id,
            item.reference,
            ", ".join(item.alternate),
            f"{item.quality:.4f}" if item.quality else "N/A",
        )

    return table
