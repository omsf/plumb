import click

@click.group()
def cli():
    pass

@cli.command()
def bind_db():
    pass
