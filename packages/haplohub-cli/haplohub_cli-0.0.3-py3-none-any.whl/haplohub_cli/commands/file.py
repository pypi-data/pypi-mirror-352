from concurrent.futures import ThreadPoolExecutor, as_completed
from posixpath import basename
from uuid import uuid4

import click
import requests
from haplohub import CreateUploadRequestRequest, FileInfo, UploadType
from rich.progress import Progress

from haplohub_cli.core.api.client import client
from haplohub_cli.core.checksum import calculate_checksum


@click.group()
def file():
    """
    Manage files
    """
    pass


@file.command()
@click.option("--cohort", "-c", type=click.STRING, required=True)
@click.option("--path", "-p", type=click.STRING, required=False)
@click.option("--recursive", "-r", is_flag=True, required=False)
def list(cohort: str, path: str = None, recursive: bool = False):
    return client.file.list_files(
        cohort,
        recursive=recursive,
        path=path,
    )


@file.command()
@click.argument("filenames", nargs=-1, type=click.Path(exists=True, dir_okay=False), required=True)
@click.option("--cohort", "-c", type=click.STRING, required=True)
@click.option("--file-type", "-t", type=click.Choice(UploadType), required=True)
@click.option("--sample", "-s", type=click.STRING, required=False)
@click.option("--member", "-m", type=click.STRING, required=False)
def upload(cohort: str, filenames: tuple[str, ...], file_type: UploadType = None, sample: str = None, member: str = None):
    checksums = {}
    file_map = {}

    for full_path in filenames:
        file_name = basename(full_path)
        checksums[file_name] = calculate_checksum(full_path)
        file_map[file_name] = full_path

    request = CreateUploadRequestRequest(
        upload_request_id=str(uuid4()),
        file_type=file_type,
        sample_id=sample,
        member_id=member,
        files=[
            FileInfo(
                file_path=file_name,
                md5_hash=checksums[file_name],
            )
            for file_name in file_map.keys()
        ],
    )

    response = client.upload.create_upload_request(cohort, request).actual_instance

    if response.status == "error":
        return response

    with Progress() as progress:
        uploading = progress.add_task("Uploading files", total=len(response.result.upload_links))

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [
                executor.submit(
                    requests.put,
                    file.signed_url,
                    data=open(file_map[file.original_file_path], "rb").read(),
                    headers={"Content-MD5": checksums[file.original_file_path]},
                )
                for file in response.result.upload_links
            ]

            for future in as_completed(futures):
                future.result().raise_for_status()
                progress.update(uploading, advance=1)
