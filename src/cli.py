
import os
import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from core import Light, with_light

console = Console()

common_options = [
    click.option('--email', default=None),
    click.option('--email-file', default=None),
    click.option('--password', default=None),
    click.option('--password-file', default=None),
    click.option('--device-id', default=None),
    click.option('--device-id-file', default=None),
    click.option('--no-headless', is_flag=True),
]   

def with_common_options(f):
    for option in common_options:
        f = option(f)
    return f

@click.group()
def cli():
    """Interface with Light device."""
    pass

@cli.group()
def music():
    """Manage Light music library."""
    pass

@music.command()
@with_common_options
@with_light
@click.argument('songs', nargs=-1, required=True)
@click.option('--allow-duplicates', is_flag=True)
@click.option('--match-title-by', '-m', type=click.Choice(['filename', 'metadata']), default='metadata')
def upload(light, songs, allow_duplicates, match_title_by, **kwargs):
    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console) as progress:
        task = progress.add_task("Uploading...")
        light.upload_tracks(list(songs), allow_duplicates=allow_duplicates, match_title_by=match_title_by)
        progress.update(task, description="Done.")                                                                                                    

@music.command()
@with_common_options
@with_light
@click.argument('songs', nargs=-1, required=True)
def delete(light, songs, **kwargs):
    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console) as progress:
        task = progress.add_task("Deleting...")
        light.delete_tracks(list(songs))
        progress.update(task, description="Done.")                                                                                                    


if __name__ == "__main__":
    cli()
