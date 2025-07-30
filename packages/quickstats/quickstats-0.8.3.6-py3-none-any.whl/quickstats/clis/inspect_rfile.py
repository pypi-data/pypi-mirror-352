import click

from .core import cli

__all__ = ['inspect_rfile']
    
@cli.command(name='inspect_rfile')
@click.option('-i', '--file_expr', required=True, help='File name expression '
              '(supports wild card, multiple files separated by commas).')
@click.option('-t', '--treename', default=None, help='Tree name. Auto-default by default.')
@click.option('-o', '--output_file', default=None, help='Export output to text file. If None, no output is saved.')
@click.option('--include', 'include_patterns', default=None, 
              help='Match variable names with given patterns (separated by commas).')
@click.option('--exclude', 'exclude_patterns', default=None,
              help='Exclude variable names with given patterns (separated by commas).')
@click.option('-f','--filter', 'filter_expr', default=None, show_default=True,
              help='Apply a filter to the events.')
@click.option('-v', '--verbosity',  default="INFO", show_default=True,
              help='verbosity level ("DEBUG", "INFO", "WARNING", "ERROR")')
def inspect_rfile(file_expr, treename, filter_expr=None, output_file=None,
                  include_patterns=None, exclude_patterns=None, verbosity="INFO"):
    '''Tool for inspecting root files
    '''
    from quickstats.utils.string_utils import split_str
    file_expr = split_str(file_expr, sep=',', remove_empty=True)
    if include_patterns is not None:
        include_patterns = split_str(include_patterns, sep=',', remove_empty=True)
    if exclude_patterns is not None:
        exclude_patterns = split_str(exclude_patterns, sep=',', remove_empty=True)
    from quickstats.components import RooInspector
    rinspector = RooInspector(file_expr, treename=treename,
                              filter_expr=filter_expr, verbosity=verbosity)
    rinspector.print_summary(include_patterns=include_patterns,
                             exclude_patterns=exclude_patterns,
                             save_as=output_file)