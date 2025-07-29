import click
import requests
from pathlib import Path
from typing import Optional
import re
from .settings import read_api_endpoint, read_api_token


@click.command()
@click.argument("object_id", type=str)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output directory path to save the downloaded file",
)
@click.option(
    "--use-object-id",
    is_flag=True,
    help="Use object ID as filename instead of server filename",
)
def download_matrix(
    object_id: str, output: Optional[str] = None, use_object_id: bool = False
):
    """This api download matrix of given object_id"""
    with requests.post(
        f"{read_api_endpoint()}/api_public/download_matrix",
        cookies={"cdiam_session_token": read_api_token()},
        json={"data_id": object_id},
        stream=True,
    ) as response:

        content_disposition = response.headers.get("Content-Disposition")
        filename = None
        if content_disposition and not use_object_id:
            # Look for 'filename' in the header (e.g., 'attachment; filename="example.pdf"')
            filename_match = re.search(r'filename="(.+)"', content_disposition)
            filename = filename_match.group(1) if filename_match else None

        if filename is None:
            filename = object_id
        # If output path is specified, join it with the filename
        if output:
            output_path = Path(output)
            output_path.mkdir(parents=True, exist_ok=True)
            file_path = output_path / filename
        else:
            file_path = filename
        response.raise_for_status()
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # Filter out keep-alive chunks
                    f.write(chunk)
