import click

from .core import cli

__all__ = ['process_rfile']

@cli.command(name='process_rfile')
@click.option('-i', '--input_file', 'filename', required=True, 
              help='Input ROOT file to process.')
@click.option('-c', '--config', 'config_path', required=True,
              help='Path to the processor card.')
@click.option('--multithread/--no-multirhread', default=True, show_default=True,
              help='Enable implicit multi-threading.')
@click.option('-g', '--global', 'glob', default=None,
              help='Include global variables in the form "<name>=<value>,..." .')
@click.option('-f', '--flag', default=None,
              help='Flags to set (separated by commas).')
@click.option('-v', '--verbosity', default='INFO', show_default=True,
              type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
              help='Verbosity level.')
def process_rfile(filename, config_path, multithread, glob, flag, verbosity):
    """
    Process a ROOT file based on RDataFrame routines
    """
    from quickstats.components.processors import RooProcessor
    from quickstats.components.processors.actions import RooProcGlobalVariables
    from quickstats.utils.string_utils import split_str
    if flag is not None:
        flags = split_str(flag, sep=',', remove_empty=True)
    else:
        flags = []
    rprocessor = RooProcessor(config_path, multithread=multithread, flags=flags, verbosity=verbosity)
    global_variables = RooProcGlobalVariables._parse(glob)
    rprocessor.global_variables.update(global_variables)
    rprocessor.run(filename)