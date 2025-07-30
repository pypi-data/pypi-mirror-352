import quickstats

from . import template_styles
from . import template_analysis_label_options

from .core import *
from .color_schemes import *
from .registry import Registry
from .abstract_plot import AbstractPlot
from .collective_data_plot import CollectiveDataPlot
from .stat_plot_config import *
from .hypotest_inverter_plot import HypoTestInverterPlot
from .variable_distribution_plot import VariableDistributionPlot
from .score_distribution_plot import ScoreDistributionPlot
from .test_statistic_distribution_plot import TestStatisticDistributionPlot
from .histogram_plot import HistogramPlot
from .general_1D_plot import General1DPlot
from .two_axis_1D_plot import TwoAxis1DPlot
from .general_2D_plot import General2DPlot
from .upper_limit_1D_plot import UpperLimit1DPlot
from .upper_limit_2D_plot import UpperLimit2DPlot
from .upper_limit_3D_plot import UpperLimit3DPlot
from .upper_limit_benchmark_plot import UpperLimitBenchmarkPlot
from .likelihood_1D_plot import Likelihood1DPlot
from .likelihood_2D_plot import Likelihood2DPlot
from .pdf_distribution_plot import PdfDistributionPlot
from .correlation_plot import CorrelationPlot
from .sample_purity_plot import SamplePurityPlot
from .bidirectional_bar_chart import BidirectionalBarChart
from .two_panel_1D_plot import TwoPanel1DPlot
from .multi_panel_1D_plot import MultiPanel1DPlot
from .tomography_plot import TomographyPlot
from .bumphunt_1D_plot import BumpHunt1DPlot
from .data_modeling_plot import DataModelingPlot

# Reference from https://github.com/beojan/atlas-mpl
reload_styles()
use_style('hep')

register_colors(EXTRA_COLORS)
register_cmaps(QUICKSTATS_PALETTES)