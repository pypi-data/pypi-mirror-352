from haplohub import (
    ErrorResponse,
)
from rich.text import Text

from haplohub_cli.formatters.decorators import register


@register(ErrorResponse)
def format_error_response(data: ErrorResponse):
    return Text(f"Error [{data.error.code}]: {data.error.message}", style="red")
