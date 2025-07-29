import click
from .commands.analyze import analyze
from .commands.enrich import enrich
from .commands.plot import plot_volcano,plot_manhan
from .commands.run_all import run_all


@click.group()
def cli():
    """Splicing-regulatory Driver Genes (SDG) Identification Tool"""
    pass

cli.add_command(analyze)
cli.add_command(enrich)
cli.add_command(plot_volcano)
cli.add_command(plot_manhan)
cli.add_command(run_all)
if __name__ == '__main__':
    cli()