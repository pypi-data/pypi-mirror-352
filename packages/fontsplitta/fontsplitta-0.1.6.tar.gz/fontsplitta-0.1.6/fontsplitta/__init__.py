import click
from fontsplitta import split
from fontsplitta import test_server
from fontsplitta import google_fonts

from importlib.metadata import version

__version__ = version("fontsplitta")


@click.group()
@click.version_option(version=__version__)
def cli():
    pass


def main():
    cli.add_command(split.split)
    cli.add_command(test_server.test_server)
    cli.add_command(google_fonts.get_unicode_ranges_from_google_fonts)
    cli()


if __name__ == "__main__":
    main()
