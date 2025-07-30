import click


@click.group()
@click.version_option(
    prog_name="WorkTimer",
    message="%(prog)s v%(version)s",
)
def cli():
    """WorkTimer: Simple tracker of time spent at work"""
    pass
