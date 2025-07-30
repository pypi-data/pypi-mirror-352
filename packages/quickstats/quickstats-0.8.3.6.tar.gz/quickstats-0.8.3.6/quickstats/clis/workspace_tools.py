import click

from .core import DelimitedStr, cli

__all__ = ['inspect_ws', 'compare_ws', 'build_xml_ws', 'modify_ws', 'combine_ws', 'decompose_ws']

kItemChoices = ['workspace', 'dataset', 'snapshot', 'category', 'poi', 
                'detailed_nuisance_parameter', 'nuisance_parameter',
                'global_observable', 'auxiliary']
kDefaultItems = ",".join(['workspace', 'dataset', 'snapshot', 'category',
                 'poi', 'detailed_nuisance_parameter'])

@cli.command(name='inspect_ws')
@click.option('-i', '--input_file', required=True, help='Path to the input workspace file.')
@click.option('-w', '--workspace', 'ws_name', default=None, help='Name of workspace. Auto-detect by default.')
@click.option('-d', '--dataset', 'data_name', default=None, help='Name of dataset. Generally not needed.')
@click.option('-m', '--model_config', 'mc_name', default=None, help='Name of model config. Auto-detect by default.')
@click.option('-o', '--output_file', default=None, help='Export output to a text file. If None, no output is saved.')
@click.option('--items', cls=DelimitedStr, type=click.Choice(kItemChoices), show_default=True,
              default=kDefaultItems, help='Items to include in the summary (separated by commas).')
@click.option('--include', 'include_patterns', default=None, 
              help='Match variable names with given patterns (separated by commas).')
@click.option('--exclude', 'exclude_patterns', default=None,
              help='Exclude variable names with given patterns (separated by commas).')
@click.option('--detailed/--name-only', default=True, show_default=True,
              help='Include detailed variable properties or just the variable name in the summary.')
def inspect_ws(input_file, ws_name=None, data_name=None, mc_name=None, output_file=None, items=None,
               include_patterns=None, exclude_patterns=None, detailed=True):
    '''
        Inspect workspace attributes
    '''
    from quickstats.components import ExtendedModel
    model = ExtendedModel(input_file, ws_name=ws_name, mc_name=mc_name, data_name=data_name,
                          verbosity="WARNING")
    from quickstats.utils.string_utils import split_str
    #items = items.split(",") if items is not None else None
    include_patterns = split_str(include_patterns, ',') if include_patterns is not None else None
    exclude_patterns = split_str(exclude_patterns, ',') if exclude_patterns is not None else None
    model.stdout.verbosity = "INFO"
    model.print_summary(items=items, save_as=output_file, detailed=detailed,
                        include_patterns=include_patterns, exclude_patterns=exclude_patterns)

@cli.command(name='build_xml_ws')
@click.option('-i', '--filename', 'source', required=True, 
              help='Input xml file.')
@click.option('--data_storage_type', default="vector", show_default=True, 
              type=click.Choice(['vector', 'tree', 'composite']),
              help='Set RooAbsData StorageType. Available choices: "vector", "tree", "composite".')
@click.option('-d', '--basedir', default=None, 
              help='Base directory to which files in the xmls are referenced. '
                   'By default, the directory of the input xml file is used.')
@click.option('-t', '--minimizer_type', default="Minuit2", show_default=True,
              help='Minimizer type.')
@click.option('-a', '--minimizer_algo', default="Migrad", show_default=True,
              help='Minimizer algorithm.')
@click.option('--strategy', type=int, default=1, show_default=True,
              help='Default minimization strategy.')
@click.option('-e', '--eps', type=float, default=1.0, show_default=True,
              help='Minimization convergence criterium.')
@click.option('--retry', type=int, default=1, show_default=True,
              help='Maximum number of retries upon a failed fit.')
@click.option('--retry-policy', type=click.IntRange(0, 2), default=1, show_default=True,
              help='\b\n Policy to retry when the fit failed.'
                   '\b\n Case 0: Do not retry.'
                   '\b\n Case 1: Update strategy dynamically.'
                   '\b\n Case 2: Update eps dynamically.')
@click.option('--optimize', type=int, default=2, show_default=True,
              help='Optimize constant terms.')
@click.option('--minimizer_offset', type=int, default=1, show_default=True,
              help='Enable minimizer offsetting.')
@click.option('--offset/--no-offset', default=True, show_default=True,
              help='Offset likelihood.')
@click.option('--use-piecewise-interp/--use-response-function', default=True, show_default=True,
              help='Offset likelihood.')
@click.option('--use-binned/--use-unbinned', default=False, show_default=True,
              help='Whether to convert unbinned dataset to binned dataset.')
@click.option('-c', '--num_cpu', type=int, default=1, show_default=True,
              help='Number of CPUs to use during minimization.')
@click.option('--apply-fix/--do-not-apply-fix', default=False, show_default=True,
              help='Apply a fix on the up/down uncertainty implementation.')
@click.option('--extra_minimizer_options', default=None, show_default=True,
              help='Additional minimizer options to include. Format should be <config>=<value> '
                   'separated by commas. Example: "discrete_min_tol=0.001,do_discrete_iteration=1"')
@click.option('--cms_runtimedef', 'runtimedef_expr', default=None, show_default=True,
              help='CMS specific runtime definitions. Format should be <config>=<value> '
                   'separated by commas. Example: "REMOVE_CONSTANT_ZERO_POINT=1,ADDNLL_GAUSSNLL=0"')
@click.option('-v', '--verbosity', default='INFO', show_default=True,
              type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
              help='Verbosity level.')
@click.option('--version', type=int,  default=2, show_default=True,
              help='Version of XMLWSBuilder to use (Choose between 1 and 2).')
def build_xml_ws(**kwargs):
    """
    Build workspace from XML config files
    """
    version = kwargs.pop("version")
    _kwargs = {}
    for arg_name in ["source", "use_binned", "data_storage_type",
                     "basedir", "verbosity", "apply_fix",
                     "use_piecewise_interp"]:
        _kwargs[arg_name] = kwargs.pop(arg_name)
    _kwargs['minimizer_config'] = kwargs
    if version == 1:
        from quickstats.components.workspaces import XMLWSBuilderV1 as XMLWSBuilder
    else:        
        from quickstats.components.workspaces import XMLWSBuilder
    builder = XMLWSBuilder(**_kwargs)
    builder.generate_workspace()
    
@cli.command(name='modify_ws')
@click.option('-i', '--filename', 'source', required=True, 
              help='Input xml/json file.')
@click.option('--input_workspace', 
              help='Override input workspace path from the xml/json file.')
@click.option('--output_workspace', 
              help='Override output workspace path from the xml/json file.')
@click.option('--import-class-code/--no-import-class-code', 'import_class_code',
              default=True, show_default=True,
              help='Import class code.')
@click.option('--float-all-nuis/--no-float-all-nuis', 'float_all_nuis',
              default=False, show_default=True,
              help='Float all NPs')
@click.option('--remove-fixed-nuis/--no-remove-fixed-nuis', 'remove_fixed_nuis',
              default=False, show_default=True,
              help='Remove fixed NPs')
@click.option('-t', '--minimizer_type', default="Minuit2", show_default=True,
              help='Minimizer type.')
@click.option('-a', '--minimizer_algo', default="Migrad", show_default=True,
              help='Minimizer algorithm.')
@click.option('--strategy', type=int, default=1, show_default=True,
              help='Default minimization strategy.')
@click.option('-e', '--eps', type=float, default=1.0, show_default=True,
              help='Minimization convergence criterium.')
@click.option('--retry', type=int, default=1, show_default=True,
              help='Maximum number of retries upon a failed fit.')
@click.option('--retry-policy', type=click.IntRange(0, 2), default=1, show_default=True,
              help='\b\n Policy to retry when the fit failed.'
                   '\b\n Case 0: Do not retry.'
                   '\b\n Case 1: Update strategy dynamically.'
                   '\b\n Case 2: Update eps dynamically.')
@click.option('--optimize', type=int, default=2, show_default=True,
              help='Optimize constant terms.')
@click.option('--minimizer_offset', type=int, default=1, show_default=True,
              help='Enable minimizer offsetting.')
@click.option('--offset/--no-offset', default=True, show_default=True,
              help='Offset likelihood.')
@click.option('-c', '--num_cpu', type=int, default=1, show_default=True,
              help='Number of CPUs to use during minimization.')
@click.option('--extra_minimizer_options', default=None, show_default=True,
              help='Additional minimizer options to include. Format should be <config>=<value> '
                   'separated by commas. Example: "discrete_min_tol=0.001,do_discrete_iteration=1"')
@click.option('--cms_runtimedef', 'runtimedef_expr', default=None, show_default=True,
              help='CMS specific runtime definitions. Format should be <config>=<value> '
                   'separated by commas. Example: "REMOVE_CONSTANT_ZERO_POINT=1,ADDNLL_GAUSSNLL=0"')
@click.option('-v', '--verbosity', default='INFO', show_default=True,
              type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
              help='Verbosity level.')
def modify_ws(**kwargs):
    """
    Modify workspace from XML/json config files
    """
    infile = kwargs.pop("input_workspace")
    outfile = kwargs.pop("output_workspace")
    import_class_code = kwargs.pop('import_class_code')
    float_all_nuis = kwargs.pop('float_all_nuis')
    remove_fixed_nuis = kwargs.pop('remove_fixed_nuis')
    _kwargs = {}
    for arg_name in ["source", "verbosity"]:
        _kwargs[arg_name] = kwargs.pop(arg_name)
    _kwargs['minimizer_config'] = kwargs
    from quickstats.components.workspaces import XMLWSModifier
    modifier = XMLWSModifier(**_kwargs)
    modifier.create_modified_workspace(infile=infile, outfile=outfile,
                                       import_class_code=import_class_code,
                                       float_all_nuis=float_all_nuis,
                                       remove_fixed_nuis=remove_fixed_nuis)
    
kItemChoices = ['workspace', 'dataset', 'category', 'snapshot', 'pdf',
                'function', 'poi', 'nuisance_parameter', 'global_observable',
                'constrained_nuisance_parameter', 'unconstrained_nuisance_parameter',
                'auxiliary']
kDefaultItems = ",".join(['workspace', 'dataset', 'category', 'poi', 'pdf',
                          'function', 'nuisance_parameter', 'global_observable',
                          'auxiliary'])
kDefaultVisibility = ",".join(["workspace=0b11001", "category=0b10011", "snapshot=0b10011",
                               "dataset=0b11011", "pdf=0b01011", "function=0b01011" , "poi=0b01011",
                               "nuisance_parameter=0b01011", "global_observable=0b01011", "auxiliary=0b01011"])

@cli.command(name='compare_ws')
@click.option('-l', '--left', required=True, 
              help='Path to the input workspace file (left of comparison).')
@click.option('-r', '--right', required=True, 
              help='Path to the input workspace file (right of comparison).')
@click.option('--items', cls=DelimitedStr, type=click.Choice(kItemChoices),
              default=kDefaultItems, show_default=True,
              help='Items to include in the comparison (seperated by commas).')
@click.option('--indent', default="   ", show_default=True,
              help='Indentation for each row.')
@click.option('--visibility', default=kDefaultVisibility, show_default=True,
              help='\b\n Set visibility of the items included in the comparison:'
                   '\b\n boolean mask for showing definitions of certain objects'
                   '\b\n 0b000001 = show definitions for unique objects'
                   '\b\n 0b000010 = show definitions for redefined objects'
                   '\b\n 0b000100 = show definitions for reconstituted objects'
                   '\b\n 0b001000 = show definitions for renamed/remapped objects'
                   '\b\n 0b010000 = show definitions for identical objects'
                   '\b\n 0b100000 = show definitions for regrouped objects')
@click.option('--save_text', default=None,
              help='Save summary print out as a text file.')
@click.option('--save_json_data', default=None,
              help='Save comparison data as a json file.')
@click.option('--save_excel_data', default=None,
              help='Save comparison data as an excel file.')
@click.option('-v', '--verbosity', default='INFO', show_default=True,
              type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
              help='Verbosity level.')
def compare_ws(**kwargs):
    """
    Compare two workspace files
    """
    from quickstats.components.workspaces import WSComparer
    comparer = WSComparer(kwargs["left"], kwargs["right"], items=kwargs["items"],
                          visibility_map=kwargs["visibility"])
    comparer.load_data()
    comparer.process_data()
    summary_str = comparer.get_summary_str(indent=kwargs["indent"])
    print(summary_str)
    save_text = kwargs["save_text"]
    save_json_data = kwargs["save_json_data"]
    save_excel_data = kwargs["save_excel_data"]
    if save_text is not None:
        with open(save_text, "w") as f:
            f.write(summary_str)
    if save_json_data is not None:
        comparer.save_json(save_json_data)
    if save_excel_data is not None:
        comparer.save_excel(save_excel_data)
        
        
@cli.command(name='combine_ws')
@click.option('-i', '--filename', 'source', required=True, 
              help='Input xml file.')
@click.option('--input_workspace', 
              help='Override input workspace paths from the xml file. Format: <channel>=<path>,...')
@click.option('--output_workspace', 
              help='Override output workspace path from the xml file.')
@click.option('--save_rename_ws/--skip_rename_ws', default=False, show_default=True,
              help='Save a temporary workspace after the rename step.')
@click.option('--save_combine_ws/--skip_combine_ws', default=False, show_default=True,
              help='Save a temporary workspace after the combine step.')
@click.option('-t', '--minimizer_type', default="Minuit2", show_default=True,
              help='Minimizer type.')
@click.option('-a', '--minimizer_algo', default="Migrad", show_default=True,
              help='Minimizer algorithm.')
@click.option('--strategy', type=int, default=1, show_default=True,
              help='Default minimization strategy.')
@click.option('-e', '--eps', type=float, default=1.0, show_default=True,
              help='Minimization convergence criterium.')
@click.option('--retry', type=int, default=1, show_default=True,
              help='Maximum number of retries upon a failed fit.')
@click.option('--retry-policy', type=click.IntRange(0, 2), default=1, show_default=True,
              help='\b\n Policy to retry when the fit failed.'
                   '\b\n Case 0: Do not retry.'
                   '\b\n Case 1: Update strategy dynamically.'
                   '\b\n Case 2: Update eps dynamically.')
@click.option('--optimize', type=int, default=2, show_default=True,
              help='Optimize constant terms.')
@click.option('--minimizer_offset', type=int, default=1, show_default=True,
              help='Enable minimizer offsetting.')
@click.option('--offset/--no-offset', default=True, show_default=True,
              help='Offset likelihood.')
@click.option('-c', '--num_cpu', type=int, default=1, show_default=True,
              help='Number of CPUs to use during minimization.')
@click.option('--import-class-code/--no-import-class-code', 'import_class_code',
              default=True, show_default=True,
              help='Import class code.')
@click.option('--extra_minimizer_options', default=None, show_default=True,
              help='Additional minimizer options to include. Format should be <config>=<value> '
                   'separated by commas. Example: "discrete_min_tol=0.001,do_discrete_iteration=1"')
@click.option('--cms_runtimedef', 'runtimedef_expr', default=None, show_default=True,
              help='CMS specific runtime definitions. Format should be <config>=<value> '
                   'separated by commas. Example: "REMOVE_CONSTANT_ZERO_POINT=1,ADDNLL_GAUSSNLL=0"')
@click.option('--use-cms-opt-pdf/--no-use-cms-opt-pdf', 'use_cms_opt_pdf', default=False, show_default=True,
              help='Use CMS Optimal PDF to make combined workspace.')
@click.option('-v', '--verbosity', default='INFO', show_default=True,
              type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
              help='Verbosity level.')
def combine_ws(**kwargs):
    """
    Combine workspace from XML config files
    """
    infile = kwargs.pop("input_workspace")
    outfile = kwargs.pop("output_workspace")
    import_class_code = kwargs.pop('import_class_code')
    from quickstats.utils.string_utils import split_str
    if infile is not None:
        infiles = {}
        items = split_str(infile, sep=",", remove_empty=True)
        for item in items:
            subitems = split_str(item, sep='=')
            if len(subitems) != 2:
                raise ValueError("invalid format for the argument \"input_workspace\"")
            infiles[subitems[0]] = subitems[1]
    else:
        infiles = None
    save_rename_ws = kwargs.pop("save_rename_ws")
    save_combine_ws = kwargs.pop("save_combine_ws")
    _kwargs = {}
    for arg_name in ["source", "verbosity", "use_cms_opt_pdf"]:
        _kwargs[arg_name] = kwargs.pop(arg_name)
    _kwargs['minimizer_config'] = kwargs
    from quickstats.components.workspaces import XMLWSCombiner
    combiner = XMLWSCombiner(**_kwargs)
    combiner.create_combined_workspace(infiles=infiles, outfile=outfile,
                                       save_rename_ws=save_rename_ws,
                                       save_combine_ws=save_combine_ws,
                                       save_final_ws=True,
                                       import_class_code=import_class_code)
    
    
@cli.command(name='decompose_ws')
@click.option('-i', '--infile', required=True, 
              help='Path to the input workspace file.')
@click.option('-o', '--outfile', required=True, 
              help='Path to the output workspace file.')
@click.option('--import-class-code/--no-import-class-code', 'import_class_code',
              default=True, show_default=True,
              help='Import class code.')
@click.option('-c', '--category_expr', default='*', show_default=True,
              help='Categories to keep in the decomposed workspace (separated by commas). '
              'Both category index and category label can be used. Category index can be '
              'a single number or a range "<min_index>-<max_index>. Wildcard is supported '
              'for category labels.')
@click.option('--snapshots', 'snapshots_to_save', default=None, show_default=True,
              help='Snapshots to save (separated by commas). '
              'By default, all existing snapshots will be saved.')
@click.option('--rebuild-nuis/--no-rebuild-nuis', default=False, show_default=True,
              help='Whether to rebuild the nuisance parameter set.')
@click.option('--rebuild-pdf/--no-rebuild-pdf', default=False, show_default=True,
              help='Whether to rebuild category pdfs.')
@click.option('-v', '--verbosity', default='INFO', show_default=True,
              type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
              help='Verbosity level.')
def decompose_ws(**kwargs):
    """
    Decompose workspace into subcategories
    """
    init_kwargs = {}
    for key in ['verbosity']:
        init_kwargs[key] = kwargs.pop(key)
    from quickstats.components.workspaces import WSDecomposer
    decomposer = WSDecomposer(**init_kwargs)
    decomposer.create_decomposed_workspace(**kwargs)