import click

__all__ = ['compile_macros', 'add_macro', 'remove_macro', 'cli']

class NaturalOrderGroup(click.Group):
    """Command group trying to list subcommands in the order they were added.

    Make sure you initialize the `self.commands` with OrderedDict instance.

    With decorator, use::

        @click.group(cls=NaturalOrderGroup, commands=OrderedDict())
    """

    def list_commands(self, ctx):
        """List command names as they are in commands dict.

        If the dict is OrderedDict, it will preserve the order commands
        were added.
        """
        return self.commands.keys()

@click.group(cls=NaturalOrderGroup)
def cli():
    pass

class DelimitedStr(click.Option):
    def type_cast_value(self, ctx, value):
        try:
            return [i.strip() for i in value.split(",")]
        except Exception:
            raise click.BadParameter(value)


@cli.command(name='compile')
@click.option('-m', '--macros', default=None, show_default=True,
              help='Macros to compile (separated by commas). By default all macros are compiled.')
def compile_macros(macros):
    """
    Compile ROOT macros
    """
    import quickstats
    quickstats.compile_macros(macros)
    
@cli.command(name='add_macro')
@click.option('-i', '--input_path', 'path', required=True,
              help='Path to the directory containing the source file for the macro.')
@click.option('-n', '--name', default=None, 
              help='Name of the macro. By default, the name of the input directory is used.')
@click.option('-f', '--force', is_flag=True,
              help='Force overwrite existing files.')
@click.option('--copy-files/--do-not-copy-files', 'copy_files', default=True, show_default=True,
              help='Whether to copy files from the input directory (required if not already copied).')
@click.option('--add-to-workspace-extension/--do-not-add-to-workspace-extension', 'workspace_extension',
              default=True, show_default=True,
              help='Whether to include the macro as part of the workspace extensions.')
def add_macro(**kwargs):
    """
    Add a ROOT macro to the module
    """
    import quickstats
    quickstats.add_macro(**kwargs)
    
@cli.command(name='remove_macro')
@click.option('-n', '--name', required=True,
              help='Name of the macro.')
@click.option('-f', '--force', is_flag=True,
              help='Force remove files without notification.')
@click.option('--remove-files/--do-not-remove-files', 'remove_files',
              default=False, show_default=True,
              help='Whether to remove the macro from the workspace extension list only or also remove the files.')
def remove_macro(**kwargs):
    """
    Remove a ROOT macro from the module
    """    
    import quickstats
    quickstats.remove_macro(**kwargs)