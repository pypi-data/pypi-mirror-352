import click

from .core import cli

__all__ = ['generate_standard_asimov', 'generate_asimov', 'toy_significance', 'toy_limit']

@cli.command(name='generate_standard_asimov')
@click.option('-i', '--input_file', 'filename', required=True, 
              help='Path to the input workspace file.')
@click.option('-o', '--output_file', 'outname', required=True, 
              help='Name of the output workspace containing the '
                   'generated asimov dataset.')
@click.option('-d', '--data', 'data_name', default='combData', show_default=True,
              help='Name of the dataset used in NP profiling.')
@click.option('-p', '--poi', 'poi_name', required=True, 
              help='Name of the parameter of interest (POI). Multiple POIs are separated by commas.')
@click.option('-s', '--poi_scale', type=float, default=1.0, show_default=True,
              help='Scale factor applied to the poi value.')
@click.option('-e', '--eps', type=float, default=1.0, show_default=True,
              help='Minimization convergence criterium.')
@click.option('--strategy', type=int, default=1, show_default=True,
              help='Default minimization strategy.')
@click.option('-f', '--fix', 'fix_param', default="", show_default=True,
              help='Parameters to fix.')
@click.option('-r', '--profile', 'profile_param', default="", show_default=True,
              help='Parameters to profile.')
@click.option('-s', '--snapshot', 'snapshot_name', default=None, show_default=True,
              help='Name of initial snapshot.')
@click.option('--rebuild/--do-not-rebuild', default=False, show_default=True,
              help='Rebuild the workspace.')
@click.option('--overwrite/--do-not-overwrite', default=True, show_default=True,
              help='Overwrite existing datasets.')
@click.option('--asimov_names', default=None, show_default=True,
              help='Names of the output asimov datasets (separated by commas). If not specified, '
                   'a default name for the corresponding asimov type will be given.')
@click.option('--asimov_snapshots', default=None, show_default=True,
              help='Names of the output asimov snapshots (separated by commas). If not specified, '
                   'a default name for the corresponding asimov type will be given.')
@click.option('--method', default="baseline", show_default=True,
              help='Method for generating asimov dataset from main pdf.')
@click.option('-t', '--asimov_types', default="0,1,2", show_default=True,
              help='\b\n Types of asimov dataset to generate separated by commas.  '
                   '\b\n 0: fit with POI fixed to 0                                '
                   '\b\n 1: fit with POI fixed to 1                                '
                   '\b\n 2: fit with POI free and set POI to 1 after fit           '
                   '\b\n 3: fit with POI and constrained NP fixed to 0             '
                   '\b\n 4: fit with POI fixed to 1 and constrained NP fixed to 0  '
                   '\b\n 5: fit with POI free and constrained NP fixed to 0 and    '
                   '\b\n    set POI to 1 after fit                                 '
                   '\b\n -1: nominal NP with POI set to 0                          '
                   '\b\n -2: nominal NP with POI set to 1                          ')
@click.option('--extra_minimizer_options', default=None, show_default=True,
              help='Additional minimizer options to include. Format should be <config>=<value> '
                   'separated by commas. Example: "discrete_min_tol=0.001,do_discrete_iteration=1"')
@click.option('--cms_runtimedef', 'runtimedef_expr', default=None, show_default=True,
              help='CMS specific runtime definitions. Format should be <config>=<value> '
                   'separated by commas. Example: "REMOVE_CONSTANT_ZERO_POINT=1,ADDNLL_GAUSSNLL=0"')
@click.option('-v', '--verbosity', default='INFO', show_default=True,
              type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
              help='Verbosity level.')
def generate_standard_asimov(**kwargs):
    """
    Generate standard Asimov dataset
    """
    from quickstats.components import AsimovGenerator
    from quickstats.utils.string_utils import split_str
    outname = kwargs.pop('outname')
    asimov_types = kwargs.pop('asimov_types')
    try:
        asimov_types = split_str(asimov_types, sep=",", cast=int)
    except Exception:
        asimov_types = split_str(asimov_types, sep=",")
    fix_param = kwargs.pop('fix_param')
    profile_param = kwargs.pop('profile_param')
    snapshot_name = kwargs.pop('snapshot_name')
    poi_scale = kwargs.pop("poi_scale")
    asimov_names = kwargs.pop("asimov_names")
    asimov_snapshots = kwargs.pop("asimov_snapshots")
    verbosity = kwargs.pop("verbosity")
    rebuild = kwargs.pop("rebuild")
    overwrite = kwargs.pop("overwrite")
    method = kwargs.pop("method")
    kwargs['poi_name'] = split_str(kwargs.pop('poi_name'), sep=",")
    config = {
        'fix_param': fix_param,
        'profile_param': profile_param,
        'snapshot_name': snapshot_name
    }
    from quickstats.utils.string_utils import split_str
    if asimov_names is not None:
        asimov_names = split_str(asimov_names, sep=",")
    if asimov_snapshots is not None:
        asimov_snapshots = split_str(asimov_snapshots, sep=",")
    generator = AsimovGenerator(**kwargs, config=config, verbosity=verbosity)
    generator.generate_standard_asimov(asimov_types, poi_scale=poi_scale,
                                       asimov_names=asimov_names,
                                       asimov_snapshots=asimov_snapshots,
                                       method=method,
                                       do_import=True,
                                       overwrite=overwrite)
    generator.save(outname, rebuild=rebuild)
    
    
@cli.command(name='generate_asimov')
@click.option('-i', '--input_file', 'filename', required=True, 
              help='Path to the input workspace file.')
@click.option('-o', '--output_file', 'outname', required=True, 
              help='Name of the output workspace containing the '
                   'generated asimov dataset.')
@click.option('-d', '--data', 'data_name', default='combData', show_default=True,
              help='Name of the dataset used in NP profiling.')
@click.option('-p', '--poi', 'poi_name', required=True, 
              help='Name of the parameter of interest (POI). Multiple POIs are separated by commas.')
@click.option('--poi-val', default=None, show_default=True,
              help='\b\n Generate asimov data with POI(s) set at the specified value(s). '
                   '\b\n Multiple values are separated by commas and an empty value is '
                   '\b\n equivalent to None. If None, POI(s) will be kept at the post-fit '
                   '\b\n value(s) if a fitting is performed or the pre-fit value if no '
                   '\b\n fitting is performed.')
@click.option('--poi-profile', default=None, show_default=True,
              help='\b\n Perform nuisance parameter profiling with POI(s) set at the specified value(s). '
                   '\b\n Multiple values are separated by commas and an empty value is '
                   '\b\n equivalent to None. This option is only effective if do_fit is set to True. '
                   '\b\n If None, POI(s) is set floating (i.e. unconditional maximum likelihood estimate).')
@click.option('--do-fit/--no-fit', default=True, show_default=True,
              help='Perform nuisance parameter profiling with a fit to the given dataset.')
@click.option('--modify-globs/--no-modify-globs', 'modify_globs', default=True, show_default=True,
              help='\b\n Match the values of nuisance parameters and the corresponding global '
                   '\b\n observables when generating the asimov data. This is important for '
                   '\b\n making sure the asimov data has the (conditional) minimal NLL.')
@click.option('--constraint-option', type=int, default=0, show_default=True,
              help='\b\n Customize the target of nuisance paramaters involved in the profiling. '
                   '\b\n Case 0: All nuisance parameters are allowed to float; '
                   '\b\n Case 1: Constrained nuisance parameters are fixed to 0. '
                   '\b\n         Unconstrained nuisrance parameters are allowed to float.')
@click.option('--restore-states', type=int, default=0, show_default=True,
              help='\b\n Restore variable states at the end of asimov data generation. '
                   '\b\n Case 0: All variable states will be restored; '
                   '\b\n Case 1: Only global observable states will be restored.')
@click.option('-e', '--eps', type=float, default=1.0, show_default=True,
              help='Minimization convergence criterium.')
@click.option('--strategy', type=int, default=1, show_default=True,
              help='Default minimization strategy.')
@click.option('-f', '--fix', 'fix_param', default="", show_default=True,
              help='Parameters to fix.')
@click.option('-r', '--profile', 'profile_param', default="", show_default=True,
              help='Parameters to profile.')
@click.option('-s', '--snapshot', 'snapshot_name', default=None, show_default=True,
              help='Name of initial snapshot.')
@click.option('--rebuild/--do-not-rebuild', default=False, show_default=True,
              help='Rebuild the workspace.')
@click.option('--asimov-name', default='asimovData', show_default=True,
              help='Name of the generated asimov dataset.')
@click.option('--asimov-snapshot', default=None, show_default=True,
              help='Names of the generated asimov snapshot.')
@click.option('--method', default="baseline", show_default=True,
              help='Method for generating asimov dataset from main pdf.')
@click.option('--extra-minimizer-options', default=None, show_default=True,
              help='\b\n Additional minimizer options to include. Format should be <config>=<value> '
                   '\b\n separated by commas. Example: "discrete_min_tol=0.001,do_discrete_iteration=1"')
@click.option('--cms-runtimedef', 'runtimedef_expr', default=None, show_default=True,
              help='CMS specific runtime definitions. Format should be <config>=<value> '
                   'separated by commas. Example: "REMOVE_CONSTANT_ZERO_POINT=1,ADDNLL_GAUSSNLL=0"')
@click.option('-v', '--verbosity', default='INFO', show_default=True,
              type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
              help='Verbosity level.')
def generate_asimov(**kwargs):
    """
    Generate customized Asimov dataset
    """
    from quickstats.components import AnalysisBase      
    from quickstats.utils.string_utils import split_str
    init_kwargs = {}
    for key in ['filename', 'poi_name', 'data_name',
                'fix_param', 'profile_param',
                'snapshot_name', 'eps', 'strategy',
                'extra_minimizer_options',
                'runtimedef_expr', 'verbosity']:
        init_kwargs[key] = kwargs.pop(key)
    if isinstance(init_kwargs['poi_name'], str):
        poi_name = split_str(init_kwargs['poi_name'], sep=',', strip=True)
        init_kwargs['poi_name'] = poi_name
    analysis = AnalysisBase(**init_kwargs)
    asimov_options = {}
    for key in ['poi_val', 'poi_profile', 'do_fit',
                'modify_globs', 'constraint_option',
                'restore_states', 'asimov_name',
                'asimov_snapshot', 'method']:
        asimov_options[key] = kwargs.pop(key)
    if isinstance(asimov_options['poi_val'], str):
        poi_val = split_str(asimov_options['poi_val'], sep=',', strip=True, empty_value=None, cast=float)
        if len(poi_val) == 1:
            asimov_options['poi_val'] = poi_val[0]
        else:
            asimov_options['poi_val'] = poi_val
    if isinstance(asimov_options['poi_profile'], str):
        poi_profile = split_str(asimov_options['poi_profile'], sep=',', strip=True, empty_value=None, cast=float)
        if len(poi_val) == 1:
            asimov_options['poi_profile'] = poi_profile[0]
        else:
            asimov_options['poi_profile'] = poi_profile
    pois = analysis.poi
    try:
        npoi = len(pois)
        poi_names = [poi.GetName() for poi in pois]
    except Exception:
        poi_names = pois.GetName()
    asimov_options['poi_name'] = poi_names
    analysis.model.generate_asimov(**asimov_options)
    rebuild = kwargs.pop('rebuild')
    outname = kwargs.pop('outname')
    analysis.save(outname, rebuild=rebuild)

@cli.command(name='toy_significance')
@click.option('-i', '--input_file', 'filename', required=True, 
              help='Path to the input workspace file.')
@click.option('-o', '--output_file', 'outname', default="toy_study/results.json", 
              help='Name of the output file containing toy results.')
@click.option('-n', '--n_toys', type=int,
              help='Number of the toys to use.')
@click.option('-b', '--batchsize', type=int, default=100, show_default=True,
              help='Divide the task into batches each containing this number of toys. '
                   'Result from each batch is saved for caching and different batches '
                   'are run in parallel if needed.')
@click.option('-s', '--seed', type=int, default=0,  show_default=True,
              help='Random seed used for generating toy datasets.')
@click.option('-p', '--poi', 'poi_name', default=None,
              help='Name of the parameter of interest (POI). If None, the first POI is used.')
@click.option('-v', '--poi_val', type=float, default=0,  show_default=True,
              help='POI value when generating the toy dataset.')
@click.option('--binned/--unbinned', default=True, show_default=True,
              help='Generate binned toy dataset.')
@click.option('--cache/--no-cache', default=True,  show_default=True,
              help='Cache existing batch results.')
@click.option('--fit_options', default=None, help='A json file specifying the fit options.')
@click.option('-v', '--verbosity', default='INFO', show_default=True,
              type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
              help='Verbosity level.')
@click.option('--parallel', type=int, default=-1, show_default=True,
              help='\b\n Parallelize job across the N workers.'
                   '\b\n Case  0: Jobs are run sequentially (for debugging).'
                   '\b\n Case -1: Jobs are run across N_CPU workers.')
def toy_significance(**kwargs):
    """
    Generate toys and evaluate significance
    """
    from quickstats.components import PValueToys
    n_toys = kwargs.pop("n_toys")
    batchsize = kwargs.pop("batchsize")
    seed = kwargs.pop("seed")
    cache = kwargs.pop("cache")
    outname = kwargs.pop("outname")
    parallel = kwargs.pop("parallel")
    pvalue_toys = PValueToys(**kwargs)
    pvalue_toys.get_toy_results(n_toys=n_toys, batchsize=batchsize, seed=seed,
                                cache=cache, save_as=outname, parallel=parallel)
    
@cli.command(name='toy_limit')
@click.option('-i', '--input_file', 'filename', required=True, 
              help='Path to the input workspace file.')
@click.option('-d', '--data', 'data_name', default='combData', show_default=True,
              help='Name of the dataset used for computing observed limit.')
@click.option('-o', '--output_file', 'outname', 
              default="toy_study/toy_result_seed_{seed}_batch_{batch}.root",
              show_default=True,
              help='Name of the output file containing toy results.')
@click.option('--poi_max', type=float, default=None,
              help='Maximum range of POI.')
@click.option('--poi_min', type=float, default=None,
              help='Minimum range of POI.')
@click.option('--scan_max', type=float, default=None,
              help='Maximum scan value of POI.')
@click.option('--scan_min', type=float, default=None,
              help='Minimum scan value of POI.')
@click.option('--steps', type=int, default=10, show_default=True,
              help='Number of scan steps.')
@click.option('--mu_val', type=float, default=None,
              help='Value of POI for running a single point.')
@click.option('-n', '--n_toys', type=int,
              help='Number of the toys to use.')
@click.option('-b', '--batchsize', type=int, default=50, show_default=True,
              help='Divide the task into batches each containing this number of toys. '
                   'Result from each batch is saved for caching and different batches '
                   'are run in parallel if needed.')
@click.option('-s', '--seed', type=int, default=2021,  show_default=True,
              help='Random seed used for generating toy datasets.')
@click.option('-t', '--tolerance', type=float, default=1.,  show_default=True,
              help='Tolerance for minimization.')
@click.option('-p', '--poi', 'poi_name', default=None,
              help='Name of the parameter of interest (POI). If None, the first POI is used.')
@click.option('--minimizer_type', default="Minuit2", show_default=True,
              help='Minimizer type.')
@click.option('--strategy', type=int, default=1, show_default=True,
              help='Default minimization strategy.')
@click.option('--offset/--no-offset', default=True, show_default=True,
              help='Use NLL offset.')
@click.option('--print_level', type=int, default=-1, show_default=True,
              help='Minimizer print level.')
@click.option('-v', '--verbosity', default='INFO', show_default=True,
              type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
              help='Verbosity level.')
@click.option('-f', '--fix', 'fix_param', default="", show_default=True,
              help='Parameters to fix.')
@click.option('-r', '--profile', 'profile_param', default="", show_default=True,
              help='Parameters to profile.')
@click.option('--snapshot', 'snapshot_name', default=None, help='Name of initial snapshot')
@click.option('--parallel', type=int, default=-1, show_default=True,
              help='\b\n Parallelize job across the N workers.'
                   '\b\n Case  0: Jobs are run sequentially (for debugging).'
                   '\b\n Case -1: Jobs are run across N_CPU workers.')
def toy_limit(**kwargs):
    """
    Generate toys and evaluate limits
    """
    from quickstats.components.toy_limit_calculator import evaluate_batched_toy_limits
    if not (((kwargs['scan_min'] is None) and (kwargs['scan_max'] is None) and (kwargs['mu_val'] is not None)) or \
           ((kwargs['scan_min'] is not None) and (kwargs['scan_max'] is not None) and (kwargs['mu_val'] is None))):
        raise ValueError("please provide either (scan_min, scan_max, steps) for running a scan or (mu_val)"
                         " for running a single point")        
    evaluate_batched_toy_limits(**kwargs)