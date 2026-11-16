
import os
import time
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    MofNCompleteColumn,
)

API_URL = "https://cataas.com/api/cats"
IMAGE_URL = "https://cataas.com/cat/{}"

OUTPUT_DIR = Path("static/imgs/cats")

MAX_WORKERS = 20
BATCH_SIZE = 100

MAX_RETRIES = 5
BACKOFF_FACTOR = 1.0
TIMEOUT = (10, 30)

console = Console()

MIME_TYPES = {
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/gif": "gif",
    "image/webp": "webp",
    "image/avif": "avif",
}

local = threading.local()

def get_session():
    """Create a thread-local requests session with retry support."""

    if not hasattr(local, "session"):
        session = requests.Session()

        retry = Retry(
            total=MAX_RETRIES,
            connect=MAX_RETRIES,
            read=MAX_RETRIES,
            status=MAX_RETRIES,
            backoff_factor=BACKOFF_FACTOR,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
            respect_retry_after_header=True,
        )

        adapter = HTTPAdapter(
            max_retries=retry,
            pool_connections=MAX_WORKERS,
            pool_maxsize=MAX_WORKERS,
        )

        session.mount("https://", adapter)
        session.mount("http://", adapter)

        local.session = session

    return local.session

def get_img(offset: int):
    session = get_session()

    try:
        response = session.get(
            API_URL,
            params={
                "skip": offset,
                "limit": BATCH_SIZE,
            },
            timeout=TIMEOUT,
        )

        response.raise_for_status()

        data = response.json()

        if not isinstance(data, list):
            raise ValueError("API returned an unexpected response.")

        images = []

        for img in data:
            image_id = img.get("id")
            mimetype = img.get("mimetype")

            extension = MIME_TYPES.get(mimetype)

            if not image_id or not extension:
                continue

            images.append({"url": IMAGE_URL.format(image_id), "output": OUTPUT_DIR / f"{image_id}.{extension}",})

        return images

    except (requests.RequestException, ValueError) as error:
        raise RuntimeError(f"Failed to retrieve batch at offset {offset}: {error}") from error

def download(img: dict):
    output = img["output"]
    url = img["url"]

    if output.exists():
        return "skipped"

    session = get_session()
    temp_output = output.with_name(output.name + ".part")

    for attempt in range(MAX_RETRIES + 1):
        try:
            response = session.get(
                url,
                timeout=TIMEOUT,
                stream=True,
            )

            response.raise_for_status()

            content_type = (response.headers.get("Content-Type", "").split(";")[0].lower())

            expected_extension = MIME_TYPES.get(content_type)

            if expected_extension != output.suffix.lstrip("."):
                raise ValueError(f"Unexpected content type: {content_type}")

            with open(temp_output, "wb") as file:
                for chunk in response.iter_content(chunk_size=64 * 1024):
                    if chunk:
                        file.write(chunk)

            temp_output.replace(output)

            return "downloaded"

        except (requests.RequestException, OSError, ValueError):
            temp_output.unlink(missing_ok=True)

            if attempt >= MAX_RETRIES:
                return "failed"

            time.sleep(BACKOFF_FACTOR * (2 ** attempt))

        finally:
            if "response" in locals():
                response.close()

    return "failed"


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    console.print("\n[bold cyan]Cat Image Downloader[/bold cyan]\n")

    images = []
    offset = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[cyan]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        console=console,
    ) as progress:

        task = progress.add_task(
            "Fetching image metadata",
            total=None,
        )

        while True:
            try:
                batch = get_img(offset)

                if not batch:
                    break

                images.extend(batch)
                offset += BATCH_SIZE

                progress.update(task, advance=len(batch))

            except RuntimeError as error:
                console.print(f"\n[red]{error}[/red]")
                break

        progress.update(task, completed=progress.tasks[0].completed)

    if not images:
        console.print("[yellow]No images found.[/yellow]")
        return

    downloaded = 0
    skipped = 0
    failed = 0

    console.print(f"\n[bold]Found {len(images):,} images.[/bold]")

    try:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [
                executor.submit(download, img)
                for img in images
            ]

            with Progress(
                SpinnerColumn(),
                TextColumn("[cyan]{task.description}"),
                BarColumn(),
                MofNCompleteColumn(),
                TextColumn("[green]Elapsed:[/green]"),
                TimeElapsedColumn(),
                TextColumn("[yellow]Remaining:[/yellow]"),
                TimeRemainingColumn(),
                console=console,
            ) as progress:
                task = progress.add_task("Downloading images", total=len(futures))

                for future in as_completed(futures):
                    try:
                        result = future.result()

                        if result == "downloaded":
                            downloaded += 1
                        elif result == "skipped":
                            skipped += 1
                        else:
                            failed += 1

                    except Exception as error:
                        failed += 1
                        console.print(f"\n[red]Unexpected error: {error}[/red]")

                    progress.advance(task)

    except KeyboardInterrupt:
        console.print("\n[yellow]Download interrupted.[/yellow]")
        return

    console.print("\n[bold green]Download complete![/bold green]")

    console.print(f"[green]Downloaded:[/green] {downloaded:,}")
    console.print(f"[yellow]Skipped:[/yellow] {skipped:,}")
    console.print(f"[red]Failed:[/red] {failed:,}")
    console.print(f"[cyan]Total:[/cyan] {len(images):,}")

    console.print(f"\n[dim]Saved to: {OUTPUT_DIR.resolve()}[/dim]")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Exiting...[/yellow]")
