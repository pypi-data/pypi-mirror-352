import os
import json
import click

from .core import cli

__all__ = ['harmonize_np', 'run_pulls', 'plot_pulls', 'np_correlation']

@cli.command(name='harmonize_np')
@click.argument('ws_files', nargs=-1)
@click.option('-r', '--reference', required=True, help='Path to reference json file containing renaming scheme.')
@click.option('-i', '--input_config_path', default=None, show_default=True,
              help='Path to json file containing input workspace paths.')
@click.option('-b', '--base_path', default='./', show_default=True,
              help='Base path for input config.')
@click.option('-o', '--outfile', default='renamed_np.json', show_default=True,
              help='Output filename.')
def harmonize_np(ws_files, reference, input_config_path, base_path, outfile):
    """
    Harmonize NP names across different workspaces
    """
    from quickstats.components import NuisanceParameterHarmonizer
    harmonizer = NuisanceParameterHarmonizer(reference)
    if (len(ws_files) > 0) and input_config_path is not None:
        raise RuntimeError('either workspace paths or json file containing workspace paths should be given')
    if len(ws_files) > 0:
        harmonizer.harmonize(ws_files, outfile=outfile)
    elif (input_config_path is not None):
        harmonizer.harmonize_multi_input(input_config_path, base_path, outfile=outfile)

@cli.command(name='run_pulls')
@click.option('-i', '--input_file', 'filename', required=True, 
              help='Path to the input workspace file.')
@click.option('-x', '--poi', 'poi_name', default=None,
              help='POI to measure NP impact on.')
@click.option('-o', '--outdir', default="pulls", show_default=True,
              help='Output directory.')
@click.option('-w', '--workspace', 'ws_name', default=None, 
              help='Name of workspace. Auto-detect by default.')
@click.option('-m', '--model_config', 'mc_name', default=None, 
              help='Name of model config. Auto-detect by default.')
@click.option('-d', '--data', 'data_name', default='combData', show_default=True,
              help='Name of dataset.')
@click.option('--filter', 'filter_expr', default=None, show_default=True,
              help='Filter nuisance parameter(s) to run pulls and impacts on.'+\
                   'Multiple parameters are separated by commas.'+\
                   'Wildcards are accepted. All NPs are included by default.')
@click.option('-z', '--profile', 'profile_param', default=None, show_default=True,
              help='Parameters to profile.')
@click.option('-f', '--fix', 'fix_param', default=None, show_default=True,
              help='Parameters to fix.')
@click.option('-s', '--snapshot', 'snapshot_name', default=None, show_default=True,
              help='Name of initial snapshot.')
@click.option('-t', '--minimizer_type', default="Minuit2", show_default=True,
              help='Minimizer type.')
@click.option('-a', '--minimizer_algo', default="Migrad", show_default=True,
              help='Minimizer algorithm.')
@click.option('--strategy', type=int, default=1, show_default=True,
              help='Default minimization strategy.')
@click.option('-e', '--eps', type=float, default=1.0, show_default=True,
              help='Minimization convergence criterium.')
@click.option('-q', '--precision', type=float, default=0.001, show_default=True,
              help='Precision of sigma scan.')
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
@click.option('--print_level', type=int, default=-1, show_default=True,
              help='Minimizer print level.')
@click.option('--batch_mode/--no-batch', default=False, show_default=True,
              help='Batch mode when evaluating likelihood.')
@click.option('--int_bin_precision', type=float, default=-1., show_default=True,
              help='Integrate the PDF over the bins instead of using the probability '
                   'density at the bin center.')
@click.option('--parallel', type=int, default=-1, show_default=True,
              help='\b\n Parallelize job across the N workers.'
                   '\b\n Case  0: Jobs are run sequentially (for debugging).'
                   '\b\n Case -1: Jobs are run across N_CPU workers.')
@click.option('--cache/--no-cache', default=True, show_default=True,
              help='Cache existing result.')
@click.option('--exclude', 'exclude_expr', default=None, show_default=True,
              help='Exclude NPs to run pulls and impacts on. '+\
                   'Multiple parameters are separated by commas.'+\
                   'Wildcards are accepted.')
@click.option('--save_log/--skip_log', default=True, show_default=True,
              help='Save log file.')
@click.option('--constrained_only/--any_nuis', default=True, show_default=True,
              help='Whether to include constrained nuisance parameters only.')
@click.option('--extra_minimizer_options', default=None, show_default=True,
              help='Additional minimizer options to include. Format should be <config>=<value> '
                   'separated by commas. Example: "discrete_min_tol=0.001,do_discrete_iteration=1"')
@click.option('--cms_runtimedef', 'runtimedef_expr', default=None, show_default=True,
              help='CMS specific runtime definitions. Format should be <config>=<value> '
                   'separated by commas. Example: "REMOVE_CONSTANT_ZERO_POINT=1,ADDNLL_GAUSSNLL=0"')
@click.option('--version', type=click.Choice(['1', '2']), default='2', show_default=True,
              help='Version of tool to use (Choose between 1 and 2).')
@click.option('-v', '--verbosity', default='INFO', show_default=True,
              type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
              help='Verbosity level.')
def run_pulls(**kwargs):
    """
    Tool for computing NP pulls and impacts
    """
    version = kwargs.pop('version')
    if version == '1':
        from quickstats.components import NuisanceParameterPull
        NuisanceParameterPull().run_pulls(**kwargs)
    elif version == '2':
        from quickstats.concurrent import NuisanceParameterRankingRunner
        init_kwargs = {}
        for key in ['filename', 'filter_expr', 'exclude_expr', 'poi_name',
                    'data_name', 'cache', 'outdir', 'constrained_only',
                    'save_log', 'parallel', 'verbosity']:
            init_kwargs[key] = kwargs.pop(key)
        init_kwargs['config'] = kwargs
        runner = NuisanceParameterRankingRunner(**init_kwargs)
        runner.run()
    
@cli.command(name='plot_pulls')
@click.option('-i', '--inputdir', required=True, help='Path to directory containing pull results')
@click.option('-p', '--poi', default=None, help='Parameter of interest for plotting impact')
@click.option('-n', '--n_rank', type=int, default=None, help='Total number of NP to rank')
@click.option('-m', '--rank_per_plot', type=int, default=20, show_default=True,
              help='Number of NP to show in a single plot.')
@click.option('--ranking/--no_ranking', default=True, show_default=True,
              help='Rank NP by impact.')
@click.option('--threshold', type=float, default=0., show_default=True,
              help='Filter NP by postfit impact threshold.')
@click.option('--show_sigma/--hide_sigma', default=True, show_default=True,
              help='Show one standard deviation pull.')
@click.option('--show_prefit/--hide_prefit', default=True, show_default=True,
              help='Show prefit impact.')
@click.option('--show_postfit/--hide_postfit', default=True, show_default=True,
              help='Show postfit impact.')
@click.option('--sigma_bands/--no_sigma_bands', default=False, show_default=True,
              help='Draw +-1, +-2 sigma bands.')
@click.option('--sigma_lines/--no_sigma_lines', default=True, show_default=True,
              help='Draw +-1 sigma lines.')
@click.option('--ranking_label/--no_ranking_label', default=True, show_default=True,
              help='Show ranking labels.')
@click.option('--shade/--no_shade', default=True, show_default=True,
              help='Draw shade.')
@click.option('--correlation/--no_correlation', default=True, show_default=True,
              help='Show correlation impact.')
@click.option('--onesided/--overlap', default=True, show_default=True,
              help='Show onesided impact.')
@click.option('--relative/--absolute', default=False, show_default=True,
              help='Show relative variation.')
@click.option('--theta_max', type=float, default=2, show_default=True,
              help='Pull range.')
@click.option('-y', '--padding', type=int, default=7, show_default=True,
              help='Padding below plot for texts and legends. NP column height is 1 unit.')
@click.option('-h', '--height', type=float, default=1.0, show_default=True,
              help='NP column height.')
@click.option('-s', '--spacing', type=float, default=0., show_default=True,
              help='Spacing between impact box.')
@click.option('--label-fontsize', type=float, default=20., show_default=True,
              help='Fontsize of analysis label text.')
@click.option('-d', '--display_poi', default=r"$\mu$", show_default=True,
              help='POI name to be shown in the plot.')
@click.option('-t', '--extra_text', default=None, help='Extra texts below the ATLAS label. '+\
                                                       'Use "//" as newline delimiter.')
@click.option('--elumi_label/--no_elumi_label', default=True, show_default=True,
              help='Show energy and luminosity labels.')
@click.option('--ranking_label/--no_ranking_label', default=True, show_default=True,
              help='Show ranking label.')
@click.option('--energy', default="13 TeV", show_default=True, 
              help='Beam energy.')
@click.option('--lumi', default="140 fb$^{-1}$", show_default=True, 
              help='Luminosity.')
@click.option('--status', default="int", show_default=True, 
              help='\b\n Analysis status. Choose from'
                   '\b\n            int : Internal'
                   '\b\n            wip : Work in Progress'
                   '\b\n         prelim : Preliminary'
                   '\b\n          final : *no status label*'
                   '\b\n *custom input* : *custom input*')
@click.option('--combine_pdf/--split_pdf', default=True, show_default=True,
              help='Combine all ranking plots into a single pdf.')
@click.option('--outdir', default='ranking_plots', show_default=True,
              help='Output directory.')
@click.option('-o', '--outname', default='ranking', show_default=True,
              help='Output file name prefix.')
@click.option('--style', default='default', show_default=True,
              help='Plotting style. Built-in styles are "default" and "trex".'+\
                   'Specify path to yaml file to set custom plotting style.')
@click.option('--fix_axis_scale/--free_axis_scale', default=True, show_default=True,
              help='Fix the axis scale across all ranking plots.')
@click.option('--version', type=click.Choice(['1', '2']), default='2', show_default=True,
              help='Version of tool to use (Choose between 1 and 2).')
def plot_pulls(**kwargs):
    """
    Tool for plotting NP pulls and impact rankings
    """    
    from quickstats.plots.np_ranking_plot import NPRankingPlot
    inputdir, poi = kwargs.pop('inputdir'), kwargs.pop('poi')
    version = kwargs.pop('version')
    ranking_plot = NPRankingPlot(inputdir, poi, version=version)
    ranking_plot.plot(**kwargs)

@cli.command(name='np_correlation')
@click.option('-i', '--input_file', "filename", required=True, 
              help='Path to the input workspace file.')
@click.option('-o', '--basename', default='NP_correlation_matrix', show_default=True,
              help='Base name of the output.')
@click.option('--select', default=None, show_default=True,
              help='Select specific NPs to be stored in the final output (for json and plot only). '
                   'Use comma to separate the selection (wild card is supported).')
@click.option('--remove', default=None, show_default=True,
              help='Select specific NPs to be removed in the final output (for json and plot only). '
                   'Use comma to separate the selection (wild card is supported).')
@click.option('--save_plot/--no_save_plot', default=True, show_default=True,
              help='Save NP correlation matrix as a plot in pdf format')
@click.option('--save_json/--no_save_json', default=False, show_default=True,
              help='Save NP correlation matrix as a json file')
@click.option('--save_root/--no_save_root', default=False, show_default=True,
              help='Save NP correlation matrix as a 2D histogram in a root file')
@click.option('--plot_style', default="default", show_default=True,
              help='Plot style if save_plot is enabled. Choose between "default" and '
                   '"viridis". Alternatively, a path to a yaml config file can be used')
@click.option('--threshold', type=float, default=0., show_default=True,
              help='Require at least one correlation (except itself) to be larger than this threshold'
                    ' value, otherwise not shown in plot.')
@click.option('-w', '--workspace', 'ws_name', default=None, show_default=True,
              help='Name of workspace. Auto-detect by default.')
@click.option('-m', '--model_config', 'mc_name', default=None, show_default=True,
              help='Name of model config. Auto-detect by default.')
@click.option('-d', '--data', 'data_name', default='combData', show_default=True,
              help='Name of dataset.')
@click.option('-s', '--snapshot', 'snapshot_name', default=None, show_default=True,
              help='Name of initial snapshot.')
@click.option('-z', '--profile', 'profile_param', default="", show_default=True,
              help='Parameters to profile.')
@click.option('-f', '--fix', 'fix_param', default="", show_default=True,
              help='Parameters to fix.')
@click.option('--constrain/--no-constrain', 'constrain_nuis', default=True, show_default=True,
              help='Use constrained NLL (i.e. include systematics)')
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
def np_correlation(**kwargs):
    """
    Evaluate post-fit NP correlation matrix
    """
    _kwargs = {}
    for arg_name in ["basename", "save_plot", "save_json", "save_root",
                     "plot_style", "select", "remove", "threshold"]:
        _kwargs[arg_name] = kwargs.pop(arg_name)
    _init_kwargs = {}
    for arg_name in ["filename", "data_name", "verbosity"]:
        _init_kwargs[arg_name] = kwargs.pop(arg_name)
    _init_kwargs['config'] = kwargs
    _init_kwargs['poi_name'] = []
    from quickstats.components import AnalysisBase   
    analysis = AnalysisBase(**_init_kwargs)
    analysis.minimizer.configure(hesse=True)
    analysis.nll_fit(mode=3)
    fit_result = analysis.roofit_result
    basename = os.path.splitext(_kwargs['basename'])[0]
    from quickstats.utils.roofit_utils import get_correlation_matrix
    if _kwargs['save_root']:
        correlation_hist = get_correlation_matrix(fit_result, lib="root")
        outname = basename + ".root"
        correlation_hist.SaveAs(outname)
        print(f"INFO: Saved correlation histogram to `{outname}`")
        correlation_hist.Delete()
    from quickstats.utils.common_utils import filter_by_wildcards
    if _kwargs['save_json'] or _kwargs['save_plot']:
        df = get_correlation_matrix(fit_result, lib='pandas')
        labels = list(df.columns)
        selected = filter_by_wildcards(labels, _kwargs['select'])
        selected = filter_by_wildcards(selected, _kwargs['remove'], exclusion=True)
        to_drop = list(set(labels) - set(selected))
        df = df.drop(to_drop, axis=0).drop(to_drop, axis=1).transpose()
        if _kwargs['save_json']:
            data = df.to_dict()
            outname = basename + ".json"
            with open(outname, "w") as out:
                json.dump(data, out, indent=2)
            print(f"INFO: Saved correlation data to `{outname}`")
        if _kwargs['save_plot']:
            import matplotlib.pyplot as plt
            from quickstats.plots import CorrelationPlot
            if _kwargs['threshold'] > 0:
                cols_count = (df.abs() >= _kwargs['threshold']).sum(axis=0)
                cols_to_keep = cols_count[cols_count > 1].index # the diagonal element is always 1
                df = df.loc[cols_to_keep, cols_to_keep]
            plotter = CorrelationPlot(df)
            plotter.draw_style(_kwargs['plot_style'])
            outname = basename + ".pdf"
            plt.savefig(outname, bbox_inches="tight")
            print(f"INFO: Saved correlation plot to `{outname}`")