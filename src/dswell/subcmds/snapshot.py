import zipfile
from datetime import datetime
from pathlib import Path

import click


@click.command()
@click.option("--output", "-o", help="Output path for the snapshot file.")
def snapshot(output: str | None) -> None:
    """Create a zip archive of the .dswell directory for debugging."""
    dswell_path = Path.home() / ".dswell"
    if not dswell_path.exists():
        raise click.ClickException("No .dswell directory found.")

    if output:
        archive_path = Path(output)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_name = f"dswell_snapshot_{timestamp}"
        # Create snapshot in the current working directory
        archive_path = Path.cwd() / snapshot_name

    try:
        with zipfile.ZipFile(f"{archive_path}.zip", "w", zipfile.ZIP_DEFLATED) as zf:
            for file in dswell_path.rglob("*"):
                zf.write(file, file.relative_to(dswell_path))
        click.echo(f"Successfully created snapshot: {archive_path}.zip")
    except Exception as e:
        click.echo(f"Failed to create snapshot: {e}", err=True)
