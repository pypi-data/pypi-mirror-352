import click

from .core import cli

__all__ = ['cls_limit', 'limit_scan']

@cli.command(name='cls_limit')
@click.option('-i', '--input_file', 'filename', required=True, 
              help='Path to the input workspace file.')
@click.option('-p', '--poi', 'poi_name', default=None, show_default=True,
              help='Name of the parameter of interest (POI). If not specified, the first POI from the workspace is used.')
@click.option('-d', '--data', 'data_name', default='combData', show_default=True,
              help='Name of dataset.')
@click.option('--asimov_data_name', 'asimov_data_name', default=None,
              help='If given, use custom background asimov dataset instead of generating on the fly.')
@click.option('-o', '--outname', default='limits.json', show_default=True,
              help='Name of output limit file.')
@click.option('--mu_exp', type=float, default=0, show_default=True,
              help='(DO NOT USE) Expected signal strengh value to be used for Asimov generation.')
@click.option('--mu_inj', type=float, default=None, show_default=True,
              help='Signal injection value to be used for Asimov generation.')
@click.option('--blind/--unblind', 'do_blind', default=True, show_default=True,
              help='Blind/unblind analysis.')
@click.option('--CL', 'CL', type=float, default=0.95, show_default=True,
              help='CL value to use.')
@click.option('--precision', default=0.005, show_default=True,
              help='precision in mu that defines iterative cutoff.')
@click.option('--adjust_fit_range/--keep_fit_range', default=True, show_default=True,
              help='whether to adjust the fit range to median limit +- 5 sigma for observed fit.')
@click.option('--do_tilde/--no_tilde', default=True, show_default=True,
              help='bound mu at zero if true and do the \tilde{q}_{mu} asymptotics.')
@click.option('--predictive_fit/--no_predictive_fit', default=False, show_default=True,
              help='extrapolate best fit nuisance parameters based on previous fit results.')
@click.option('--do_better_bands/--skip_better_bands', default=True, show_default=True,
              help='evaluate asymptotic CLs limit for various sigma bands.')
@click.option('--better_negative_bands/--skip_better_negative_bands', default=False, show_default=True,
              help='evaluate asymptotic CLs limit for negative sigma bands.')
@click.option('--binned/--unbinned', 'binned_likelihood', default=True, show_default=True,
              help='Activate binned likelihood for RooRealSumPdf.')
@click.option('--save_summary/--skip_summary', default=True, show_default=True,
              help='sSave summary information.')
@click.option('-z', '--profile', 'profile_param', default="", show_default=True,
              help='\b\n Parameters to profile. Multiple parameters are separated by commas. '
                   '\b\n Wildcard is supported. More details are given in the documentation.')
@click.option('-f', '--fix', 'fix_param', default="", show_default=True,
              help='\b\n Parameters to fix. Multiple parameters are separated by commas. '
                   '\b\n Wildcard is supported. More details are given in the documentation.')
@click.option('-w', '--workspace', 'ws_name', default=None, show_default=True,
              help='Name of workspace. Auto-detect by default.')
@click.option('-m', '--model_config', 'mc_name', default=None, show_default=True,
              help='Name of model config. Auto-detect by default.')
@click.option('-s', '--snapshot', 'snapshot_name', default=None, show_default=True,
              help='Name of initial snapshot.')
@click.option('--constrain/--no-constrain', 'constrain_nuis', default=True, show_default=True,
              help='Use constrained NLL.')
@click.option('-t', '--minimizer_type', default="Minuit2", show_default=True,
              help='Minimizer type.')
@click.option('-a', '--minimizer_algo', default="Migrad", show_default=True,
              help='Minimizer algorithm.')
@click.option('--strategy', type=int, default=1, show_default=True,
              help='Default minimization strategy.')
@click.option('-e', '--eps', type=float, default=1.0, show_default=True,
              help='Minimization convergence criterium.')
@click.option('--retry', type=int, default=2, show_default=True,
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
def cls_limit(**kwargs):
    """
    Tool for evaluating Asymptotic CLs limit
    """
    from quickstats.components import AsymptoticCLs
    outname = kwargs.pop('outname')
    save_summary = kwargs.pop('save_summary')
    asymptotic_cls = AsymptoticCLs(**kwargs)
    asymptotic_cls.evaluate_limits()
    asymptotic_cls.save(outname, summary=save_summary)
    
@cli.command(name='limit_scan')
@click.option('-i', '--input_path', 'input_path', required=True, 
              help='Input directory/path containing the workspace file(s) to process.')
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
@click.option('--outdir', default='output', show_default=True,
              help='Output directory where cached limit files and the merged limit file are saved.')
@click.option('--cachedir', default='cache', show_default=True,
              help='Cache directory relative to the output directory.')
@click.option('-o', '--outname', default='limits.json', show_default=True,
              help='Name of the output limit file (all parameter points merged).')
@click.option('--cache/--no-cache', default=True, show_default=True,
              help='Cache output of individual parameter point.')
@click.option('--save-log/--no-log', default=True, show_default=True,
              help='Save a log file for each parameter point.')
@click.option('--save-summary/--no-summary', default=True, show_default=False,
              help='Save a summary file for each parameter point.')
@click.option('-p', '--poi', 'poi_name', default=None,
              help='Name of the parameter of interest (POI). If None, the first POI is used.')
@click.option('--mu_exp', type=float, default=0, show_default=True,
              help='(DO NOT USE) Expected signal strengh value to be used for Asimov generation.')
@click.option('-d', '--data', 'data_name', default='combData', show_default=True,
              help='Name of dataset.')
@click.option('--asimov_data_name', 'asimov_data_name', default=None,
              help='If given, use custom background asimov dataset instead of generating on the fly.')
@click.option('--blind/--unblind', 'do_blind', default=True, show_default=True,
              help='Blind/unblind analysis.')
@click.option('--CL', 'CL', type=float, default=0.95, show_default=True,
              help='CL value to use.')
@click.option('--precision', default=0.005, show_default=True,
              help='precision in mu that defines iterative cutoff.')
@click.option('--adjust_fit_range/--keep_fit_range', default=True, show_default=True,
              help='whether to adjust the fit range to median limit +- 5 sigma for observed fit.')
@click.option('--do_tilde/--no_tilde', default=True, show_default=True,
              help='bound mu at zero if true and do the \tilde{q}_{mu} asymptotics.')
@click.option('--predictive_fit/--no_predictive_fit', default=False, show_default=True,
              help='extrapolate best fit nuisance parameters based on previous fit results.')
@click.option('--do_better_bands/--skip_better_bands', default=True, show_default=True,
              help='evaluate asymptotic CLs limit for various sigma bands.')
@click.option('--better_negative_bands/--skip_better_negative_bands', default=False, show_default=True,
              help='evaluate asymptotic CLs limit for negative sigma bands.')
@click.option('--binned/--unbinned', 'binned_likelihood', default=True, show_default=True,
              help='Activate binned likelihood for RooRealSumPdf.')
@click.option('--save_log/--skip_log', default=True, show_default=True,
              help='Save log file.')
@click.option('--save_summary/--skip_summary', default=True, show_default=True,
              help='Save summary information.')
@click.option('-z', '--profile', 'profile_param', default="", show_default=True,
              help='\b\n Parameters to profile. Multiple parameters are separated by commas. '
                   '\b\n Wildcard is supported. More details are given in the documentation.')
@click.option('-f', '--fix', 'fix_param', default="", show_default=True,
              help='\b\n Parameters to fix. Multiple parameters are separated by commas. '
                   '\b\n Wildcard is supported. More details are given in the documentation.')
@click.option('-w', '--workspace', 'ws_name', default=None, show_default=True,
              help='Name of workspace. Auto-detect by default.')
@click.option('-m', '--model_config', 'mc_name', default=None, show_default=True,
              help='Name of model config. Auto-detect by default.')
@click.option('-s', '--snapshot', 'snapshot_name', default=None, show_default=True,
              help='Name of initial snapshot.')
@click.option('--constrain/--no-constrain', 'constrain_nuis', default=True, show_default=True,
              help='Use constrained NLL.')
@click.option('-t', '--minimizer_type', default="Minuit2", show_default=True,
              help='Minimizer type.')
@click.option('-a', '--minimizer_algo', default="Migrad", show_default=True,
              help='Minimizer algorithm.')
@click.option('--strategy', type=int, default=1, show_default=True,
              help='Default minimization strategy.')
@click.option('-e', '--eps', type=float, default=1.0, show_default=True,
              help='Minimization convergence criterium.')
@click.option('--retry', type=int, default=2, show_default=True,
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
def limit_scan(**kwargs):
    """
    Evaluate a set of parmeterised asymptotic cls limits
    """
    _kwargs = {}
    for arg_name in ["input_path", "file_expr", "param_expr", "outdir", 
                     "filter_expr", "exclude_expr", "outname", "cache",
                     "cachedir", "save_log", "save_summary", "parallel"]:
        _kwargs[arg_name] = kwargs.pop(arg_name)
    _kwargs['config'] = kwargs
    from quickstats.concurrent import ParameterisedAsymptoticCLs
    runner = ParameterisedAsymptoticCLs(**_kwargs)
    runner.run()