import os
import json
import click

from .core import cli

__all__ = ['likelihood_fit', 'likelihood_scan']

@cli.command(name='likelihood_fit')
@click.option('-i', '--input_file', "filename", required=True, 
              help='Path to the input workspace file.')
@click.option('--display/--no-display', default=True, show_default=True,
              help='Display fit result.')
@click.option('--save-result', default=None, show_default=True,
              help='Save fit result as a json file to the given path.')
@click.option('--save-log', default=None, show_default=True,
              help='Save log as a text file to the given path.')
@click.option('--save-ws', default=None, show_default=True,
              help='Save fitted workspace to the given path.')
@click.option('--save-snapshot', default=None, show_default=True,
              help='Save fitted values of all variables as a snapshot and restore all variables to '
              'their initial values. Should be used together with --save_ws.')
@click.option('--save-pulls', default=None, show_default=True,
              help='Export (constrained) NP results for pulls to the given directory.')
@click.option('--rebuild/--no-rebuild', default=True, show_default=True,
              help='Save fitted workspace by rebuilding it. Should be used together with --save_ws.')
@click.option('-w', '--workspace', 'ws_name', default=None, show_default=True,
              help='Name of workspace. Auto-detect by default.')
@click.option('-m', '--model_config', 'mc_name', default=None, show_default=True,
              help='Name of model config. Auto-detect by default.')
@click.option('-d', '--data', 'data_name', default='combData', show_default=True,
              help='Name of dataset.')
@click.option('-s', '--snapshot', 'snapshot_name', default=None, show_default=True,
              help='Name of initial snapshot.')
@click.option('-z', '--profile', 'profile_param', default="", show_default=True,
              help='\b\n Parameters to profile. Multiple parameters are separated by commas. '
                   '\b\n Wildcard is supported. More details are given in the documentation.')
@click.option('-f', '--fix', 'fix_param', default="", show_default=True,
              help='\b\n Parameters to fix. Multiple parameters are separated by commas. '
                   '\b\n Wildcard is supported. More details are given in the documentation.')
@click.option('-r', '--range', 'fit_range', default=None, show_default=True,
              help='\b\n Name of fit range. To define a new range on the fly, use the syntax '
                   '\b\n single range: <range_name>=<min>_<max>'
                   '\b\n multi range: <range_name1>=<min1>_<max1>,<range_name2>=<min2>_<max2> '
                   '\b\n channel-specific range: <range_name>@<channel1>=<min1>_<max1>; '
                   '\b\n                         <range_name>@<channel2>=<min2>_<max2> ')
@click.option('--constrain/--no-constrain', 'constrain_nuis', default=True, show_default=True,
              help='Use constrained NLL (i.e. include systematics).')
@click.option('--minos', default="", show_default=True,
              help='Set of POIs (separated by commas) for evaluating errors with Minos.')
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
@click.option('--binned/--unbinned', 'binned_likelihood', default=True, show_default=True,
              help='Activate binned likelihood for RooRealSumPdf.')
@click.option('--print_level', type=int, default=-1, show_default=True,
              help='Minimizer print level.')
@click.option('-c', '--num_cpu', type=int, default=1, show_default=True,
              help='Number of CPUs to use during minimization.')
@click.option('--batch_mode/--no-batch', default=False, show_default=True,
              help='Batch mode when evaluating likelihood.')
@click.option('--int_bin_precision', type=float, default=-1., show_default=True,
              help='Integrate the PDF over the bins instead of using the probability '
                   'density at the bin center.')
@click.option('--extra_minimizer_options', default=None, show_default=True,
              help='Additional minimizer options to include. Format should be <config>=<value> '
                   'separated by commas. Example: "discrete_min_tol=0.001,do_discrete_iteration=1"')
@click.option('--cms_runtimedef', 'runtimedef_expr', default=None, show_default=True,
              help='CMS specific runtime definitions. Format should be <config>=<value> '
                   'separated by commas. Example: "REMOVE_CONSTANT_ZERO_POINT=1,ADDNLL_GAUSSNLL=0"')
@click.option('-v', '--verbosity', default='INFO', show_default=True,
              type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
              help='Verbosity level.')
def likelihood_fit(**kwargs):
    """
    Perform likelihood fit on a workspace
    """
    
    from quickstats import stdout
    from quickstats.utils.string_utils import split_str
    from quickstats.components import AnalysisBase
    from quickstats.concurrent.logging import redirect_log

    fit_range = kwargs.pop("fit_range")
    rebuild = kwargs.pop("rebuild")
    minos_pois = kwargs.pop("minos")
    minos_pois = split_str(minos_pois, sep=',', remove_empty=True)
    do_minos = len(minos_pois) > 0
    do_pulls = kwargs['save_pulls'] is not None
    _kwargs = {}
    for arg_name in ["display", "save_result", "save_log",
                     "save_pulls", "save_ws", "save_snapshot"]:
        _kwargs[arg_name] = kwargs.pop(arg_name)
    _init_kwargs = {}
    for arg_name in ["filename", "data_name", "verbosity"]:
        _init_kwargs[arg_name] = kwargs.pop(arg_name)
    _init_kwargs['config'] = kwargs
    _init_kwargs['poi_name'] = minos_pois
    log_path = _kwargs['save_log']
    with redirect_log(log_path):
        analysis = AnalysisBase(**_init_kwargs)
        if do_pulls:
            analysis.minimizer.configure(hesse=True)
        if fit_range is not None:
            analysis.set_fit_range_expression(fit_range)
        fit_result = analysis.nll_fit(mode=3, do_minos=do_minos)
    if log_path:
        stdout.info(f'Saved fit log as "{log_path}"')
    analysis.stdout.verbosity = "SILENT"
    output = {}
    output['fit_result'] = fit_result
    df = {'pois':{}, 'nuisance_parameters':{}}
    analysis.load_snapshot("currentSnapshot")
    df['pois']['prefit'] = analysis.model.as_dataframe('poi')
    df['nuisance_parameters']['prefit'] = analysis.model.as_dataframe('nuisance_parameter')
    analysis.load_snapshot("nllFit")
    if do_minos:
        df['pois']['postfit'] = analysis.model.as_dataframe('poi', asym_error=True)
    else:
        df['pois']['postfit'] = analysis.model.as_dataframe('poi')
    df['nuisance_parameters']['postfit'] = analysis.model.as_dataframe('nuisance_parameter')
    if _kwargs['display']:
        import pandas as pd
        pd.set_option('display.max_rows', None)
    for key in ['pois', 'nuisance_parameters']:
        df[key]['combined'] = df[key]['prefit'].drop(["value", "error"], axis=1)
        df[key]['combined']['value_prefit'] = df[key]['prefit']['value']
        df[key]['combined']['value_postfit'] = df[key]['postfit']['value']
        df[key]['combined']['error_prefit'] = df[key]['prefit']['error']
        if (key == "pois") and do_minos:
            df[key]['combined']['errorlo_postfit'] = df[key]['postfit']['errorlo']
            df[key]['combined']['errorhi_postfit'] = df[key]['postfit']['errorhi']
        else:
            df[key]['combined']['error_postfit'] = df[key]['postfit']['error']
        output[key] = df[key]['combined'].to_dict("list")
        if _kwargs['display']:
            stdout.info(f"{key.title()}:\n{df[key]['combined']}\n\n")
    # save fit result
    result_path = _kwargs['save_result']
    if result_path:
        with open(result_path, "w") as f:
            json.dump(output, f, indent=2)
        stdout.info(f'Saved fit result as "{result_path}"')
    # save pulls
    pulls_dir = _kwargs['save_pulls']
    if pulls_dir:
        os.makedirs(pulls_dir, exist_ok=True)
        nuis_df = df[key]['combined'].drop(['min', 'max', 'is_constant', 'error_prefit'], axis=1)
        nuis_df = nuis_df.rename(columns={"value_prefit":"nuis_nom", "name":"nuisance", 
                                          "value_postfit":"nuis_hat", "error_postfit":"nuis_hi"})
        nuis_df["nuis_lo"] = nuis_df["nuis_hi"]
        nuis_df["nuis_prefit"] = 1.0
        nuis_df = nuis_df.set_index(['nuisance'])
        constrained_np = [i.GetName() for i in analysis.model.get_constrained_nuisance_parameters()]
        nuis_df = nuis_df.loc[constrained_np].reset_index()
        nuis_data = nuis_df.to_dict('index')
        for i in nuis_data:
            data = nuis_data[i]
            np_name = data['nuisance']
            outpath = os.path.join(pulls_dir, f"{np_name}.json")
            with open(outpath, "w") as outfile:
                json.dump({"nuis": data}, outfile, indent=2)
        stdout.info(f'Saved pull results to "{pulls_dir}"')
    # save fitted workspace (and snapshot)
    ws_path = _kwargs["save_ws"]
    if ws_path:
        snapshot_name = _kwargs["save_snapshot"]
        if snapshot_name:
            from quickstats.components.basics import WSArgument
            analysis.save_snapshot(snapshot_name, WSArgument.MUTABLE)
            analysis.load_snapshot(analysis.kInitialSnapshotName)
        analysis.save(ws_path, rebuild=rebuild)
        stdout.info(f'Saved fitted workspace as "{ws_path}"')

@cli.command(name='likelihood_scan')
@click.option('-i', '--input_path', required=True, 
              help='Input directory/path containing the workspace file(s) to process.')
@click.option('--file_expr', default=None, show_default=True,
              help='\b\n File name expression describing the external parameterisation.'
                   '\b\n Example: "<mass[F]>_kl_<klambda[P]>"'
                   '\b\n Regular expression is supported'
                   '\b\n Refer to documentation for more information')
@click.option('-p', '--param_expr', default=None,
              help='\b\n Parameter expression, e.g.'
                   '\b\n 1D scan: "poi_name=<poi_min>_<poi_max>_<step>"'
                   '\b\n 2D scan: "poi_1_name=<poi_1_min>_<poi_1_max>_<step_1>,'
                   '\b\n           poi_2_name=<poi_2_min>_<poi_2_max>_<step_2>"')
@click.option('--filter', 'filter_expr', default=None, show_default=True,
              help='\b\n Filter parameter points by expression.'
                   '\b\n Example: "mass=2*,350,400,450;klambda=1.*,2.*,-1.*,-2.*"'
                   '\b\n Refer to documentation for more information')
@click.option('--exclude', 'exclude_expr', default=None, show_default=True,
              help='\b\n Exclude parameter points by expression.'
                   '\b\n Example: "mass=2*,350,400,450;klambda=1.*,2.*,-1.*,-2.*"'
                   '\b\n Refer to documentation for more information')
@click.option('--cache/--no-cache', default=True, show_default=True,
              help='Cache existing result.')
@click.option('--cache-ws/--no-cache-ws', 'cache_ws', default=False, show_default=True,
              help='Cache the post-fit workspace.')
@click.option('-o', '--outname', default='{poi_names}.json', show_default=True,
              help='Name of output file.')
@click.option('--outdir', default='likelihood_scan', show_default=True,
              help='Output directory.')
@click.option('--cachedir', default='cache', show_default=True,
              help='Cache directory relative to the output directory.')
@click.option('--save_log/--skip_log', default=True, show_default=True,
              help='Save log file.')
@click.option('-w', '--workspace', 'ws_name', default=None, show_default=True,
              help='Name of workspace. Auto-detect by default.')
@click.option('-m', '--model_config', 'mc_name', default=None, show_default=True,
              help='Name of model config. Auto-detect by default.')
@click.option('-d', '--data', 'data_name', default='combData', show_default=True,
              help='Name of dataset.')
@click.option('-s', '--snapshot', 'snapshot_name', default=None, show_default=True,
              help='Name of initial snapshot.')
@click.option('--uncond_snapshot', default=None, show_default=True,
              help='Name of snapshot with unconditional fit result.')
@click.option('-z', '--profile', 'profile_param', default="", show_default=True,
              help='\b\n Parameters to profile. Multiple parameters are separated by commas. '
                   '\b\n Wildcard is supported. More details are given in the documentation.')
@click.option('-f', '--fix', 'fix_param', default="", show_default=True,
              help='\b\n Parameters to fix. Multiple parameters are separated by commas. '
                   '\b\n Wildcard is supported. More details are given in the documentation.')
@click.option('--constrain/--no-constrain', 'constrain_nuis', default=True, show_default=True,
              help='Use constrained NLL (i.e. include systematics).')
@click.option('--allow-nan/--not-allow-nan', default=True, show_default=True,
              help='Allow cached nll to be nan.')
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
@click.option('--binned/--unbinned', 'binned_likelihood', default=True, show_default=True,
              help='Activate binned likelihood for RooRealSumPdf.')
@click.option('--print_level', type=int, default=-1, show_default=True,
              help='Minimizer print level.')
@click.option('-c', '--num_cpu', type=int, default=1, show_default=True,
              help='Number of CPUs to use during minimization.')
@click.option('--batch_mode/--no-batch', default=False, show_default=True,
              help='Batch mode when evaluating likelihood.')
@click.option('--int_bin_precision', type=float, default=-1., show_default=True,
              help='Integrate the PDF over the bins instead of using the probability '
                   'density at the bin center.')
@click.option('--extra_minimizer_options', default=None, show_default=True,
              help='Additional minimizer options to include. Format should be <config>=<value> '
                   'separated by commas. Example: "discrete_min_tol=0.001,do_discrete_iteration=1"')
@click.option('--cms_runtimedef', 'runtimedef_expr', default=None, show_default=True,
              help='CMS specific runtime definitions. Format should be <config>=<value> '
                   'separated by commas. Example: "REMOVE_CONSTANT_ZERO_POINT=1,ADDNLL_GAUSSNLL=0"')
@click.option('--parallel', type=int, default=-1, show_default=True,
              help='\b\n Parallelize job across the N workers.'
                   '\b\n Case  0: Jobs are run sequentially (for debugging).'
                   '\b\n Case -1: Jobs are run across N_CPU workers.')
@click.option('-v', '--verbosity', default='INFO', show_default=True,
              type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
              help='Verbosity level.')
def likelihood_scan(**kwargs):
    """
    Evaluate a set of parmeterised likelihood values
    """
    _kwargs = {}
    for arg_name in ["input_path", "file_expr", "param_expr", "data_name", "outdir", "filter_expr",
                     "uncond_snapshot", "exclude_expr", "outname", "cache", "cachedir", "save_log",
                     "parallel", "verbosity", "allow_nan", "cache_ws"]:
        _kwargs[arg_name] = kwargs.pop(arg_name)
    _kwargs['config'] = kwargs
    from quickstats.concurrent import ParameterisedLikelihood
    runner = ParameterisedLikelihood(**_kwargs)
    runner.run()

@cli.command(name='significance_scan')
@click.option('-i', '--input_path', required=True, 
              help='Path to the input workspace file or directory containing the parameterised '
                   'input workspace files.')
@click.option('-p', '--poi', 'poi_name', default=None,
              help='Name of the parameter of interest (POI). If None, the first POI is used.')
@click.option('--mu_exp', type=float, default=0., show_default=True,
              help='Expected value of the POI under the null hypothesis.')
@click.option('--asimov_type', type=int, default=None,
              help='\b\n Evaluate significance on an Asimov dataset of this type. '
                   'If not specified, the observed data is used. '
                   '\b\n Choices of asimov types are'
                   '\b\n 0: fit with POI fixed to 0'
                   '\b\n 1: fit with POI fixed to 1'
                   '\b\n 2: fit with POI free and set POI to 1 after fit'
                   '\b\n 3: fit with POI and constrained NP fixed to 0'
                   '\b\n 4: fit with POI fixed to 1 and constrained NP fixed to 0'
                   '\b\n 5: fit with POI free and constrained NP fixed to 0 and set POI to 1 after fit'
                   '\b\n -1: nominal NP with POI set to 0'
                   '\b\n -2: nominal NP with POI set to 1')
@click.option('--file_expr', default=r"[\w-]+", show_default=True,
              help='\b\n File name expression describing the external parameterisation.'
                   '\b\n Example: "<mass[F]>_kl_<klambda[P]>"'
                   '\b\n Regular expression is supported'
                   '\b\n Refer to documentation for more information')
@click.option('--param_expr', default=None, show_default=True,
              help='\b\n Parameter name expression describing the internal parameterisation.'
                   '\b\n Example: "klambda=-10_10_0.2,k2v=(1,2,3)"'
                   '\b\n Refer to documentation for more information')
@click.option('--filter', 'filter_expr', default=None, show_default=True,
              help='\b\n Filter parameter points by expression.'
                   '\b\n Example: "mass=(2*,350,400,450);klambda=(1.*,2.*,-1.*,-2.*)"'
                   '\b\n Refer to documentation for more information')
@click.option('--exclude', 'exclude_expr', default=None, show_default=True,
              help='\b\n Exclude parameter points by expression.'
                   '\b\n Example: "mass=(2*,350,400,450);klambda=(1.*,2.*,-1.*,-2.*)"'
                   '\b\n Refer to documentation for more information')
@click.option('--outdir', default='significance', show_default=True,
              help='Output directory where cached limit files and the merged limit file are saved.')
@click.option('--cachedir', default='cache', show_default=True,
              help='Cache directory relative to the output directory.')
@click.option('--cache/--no-cache', default=True, show_default=True,
              help='Cache existing result.')
@click.option('-o', '--outname', default='{param_names}.json', show_default=True,
              help='Name of the output significance file (all parameter points merged).')
@click.option('--save_log/--skip_log', default=True, show_default=True,
              help='Save log file.')
@click.option('-w', '--workspace', 'ws_name', default=None, show_default=True,
              help='Name of workspace. Auto-detect by default.')
@click.option('-m', '--model_config', 'mc_name', default=None, show_default=True,
              help='Name of model config. Auto-detect by default.')
@click.option('-d', '--data', 'data_name', default='combData', show_default=True,
              help='Name of dataset.')
@click.option('-s', '--snapshot', 'snapshot_name', default=None, show_default=True,
              help='Name of initial snapshot.')
@click.option('-z', '--profile', 'profile_param', default="", show_default=True,
              help='\b\n Parameters to profile. Multiple parameters are separated by commas. '
                   '\b\n Wildcard is supported. More details are given in the documentation.')
@click.option('-f', '--fix', 'fix_param', default="", show_default=True,
              help='\b\n Parameters to fix. Multiple parameters are separated by commas. '
                   '\b\n Wildcard is supported. More details are given in the documentation.')
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
@click.option('--binned/--unbinned', 'binned_likelihood', default=True, show_default=True,
              help='Activate binned likelihood for RooRealSumPdf.')
@click.option('--print_level', type=int, default=-1, show_default=True,
              help='Minimizer print level.')
@click.option('-c', '--num_cpu', type=int, default=1, show_default=True,
              help='Number of CPUs to use during minimization.')
@click.option('--batch_mode/--no-batch', default=False, show_default=True,
              help='Batch mode when evaluating likelihood.')
@click.option('--int_bin_precision', type=float, default=-1., show_default=True,
              help='Integrate the PDF over the bins instead of using the probability '
                   'density at the bin center.')
@click.option('--extra_minimizer_options', default=None, show_default=True,
              help='Additional minimizer options to include. Format should be <config>=<value> '
                   'separated by commas. Example: "discrete_min_tol=0.001,do_discrete_iteration=1"')
@click.option('--cms_runtimedef', 'runtimedef_expr', default=None, show_default=True,
              help='CMS specific runtime definitions. Format should be <config>=<value> '
                   'separated by commas. Example: "REMOVE_CONSTANT_ZERO_POINT=1,ADDNLL_GAUSSNLL=0"')
@click.option('--parallel', type=int, default=-1, show_default=True,
              help='\b\n Parallelize job across the N workers.'
                   '\b\n Case  0: Jobs are run sequentially (for debugging).'
                   '\b\n Case -1: Jobs are run across N_CPU workers.')
@click.option('-v', '--verbosity', default='INFO', show_default=True,
              type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
              help='Verbosity level.')
def significance_scan(**kwargs):
    """
    Evaluate a set of parmeterised significance values
    """
    _kwargs = {}
    for arg_name in ["input_path", "poi_name", "data_name", "file_expr", "param_expr",
                     "filter_expr", "exclude_expr", "mu_exp", "asimov_type",
                     "snapshot_name", "outdir", "cachedir", "outname", "cache",
                     "save_log", "parallel", "verbosity"]:
        _kwargs[arg_name] = kwargs.pop(arg_name)
    _kwargs['config'] = kwargs
    from quickstats.concurrent import ParameterisedSignificance
    runner = ParameterisedSignificance(**_kwargs)
    runner.run()