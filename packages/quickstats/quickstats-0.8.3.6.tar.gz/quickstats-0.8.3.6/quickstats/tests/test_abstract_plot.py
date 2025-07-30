import pytest
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

from quickstats import AbstractObject
from quickstats.plots import AbstractPlot, LegendEntry

class TestPlot(AbstractPlot):
    """Test implementation of AbstractPlot."""
    COLOR_MAP = {'test': 'red'}
    COLOR_CYCLE = 'viridis'
    LABEL_MAP = {'test': 'Test Label'}
    
    def get_default_legend_order(self) -> List[str]:
        return ['test']

class TestAbstractPlot:
    """Test suite for AbstractPlot class."""
    
    @pytest.fixture
    def plot(self):
        """Create a test plot instance."""
        return TestPlot()
        
    @pytest.fixture
    def ax(self):
        """Create a test axes."""
        fig, ax = plt.subplots()
        yield ax
        plt.close(fig)

    def test_initialization(self, plot):
        """Test plot initialization."""
        assert isinstance(plot, AbstractObject)
        assert plot.color_map.get('test') == 'red'
        assert plot.label_map.get('test') == 'Test Label'
        assert hasattr(plot, 'cmap')
        assert hasattr(plot, 'color_cycle')
        
    def test_color_cycle(self, plot):
        """Test color cycle functionality."""
        # Test default cycle
        colors = plot.get_colors()
        assert len(colors) > 0
        assert all(isinstance(c, str) for c in colors)
        
        # Test custom cycle
        plot.set_color_cycle(['red', 'blue'])
        colors = plot.get_colors()
        assert colors == ['red', 'blue']
        
    def test_legend_handling(self, plot, ax):
        """Test legend related functionality."""
        # Create test handle
        line = Line2D([0], [0], label='test')
        
        # Update legend handles
        plot.update_legend_handles({'test': line})
        
        # Check legend data
        entry = plot.legend_data.get('test')
        assert isinstance(entry, LegendEntry)
        assert entry.handle == line
        assert entry.label == 'test'
        assert entry.has_valid_label()
        
        # Test decoration
        rect = Rectangle((0, 0), 1, 1)
        plot.add_legend_decoration(rect, ['test'])
        
        entry = plot.legend_data.get('test')
        assert isinstance(entry.handle, tuple)
        assert len(entry.handle) == 2
        assert entry.handle[1] == rect
        
    def test_point_handling(self, plot):
        """Test point addition functionality."""
        plot.add_point(1.0, 2.0, label='test_point')
        assert len(plot._points) == 1
        point = plot._points[0]
        assert point.x == 1.0
        assert point.y == 2.0
        assert point.label == 'test_point'
        
        # Test duplicate name handling
        with pytest.raises(PlottingError):
            plot.add_point(3.0, 4.0, name='test_point')
            
    def test_annotation_handling(self, plot):
        """Test annotation functionality."""
        plot.add_annotation('test', x=0.5, y=0.5)
        assert len(plot._annotations) == 1
        ann = plot._annotations[0]
        assert ann.text == 'test'
        assert ann.options == {'x': 0.5, 'y': 0.5}
        
        # Test invalid input
        with pytest.raises(ValueError):
            plot.add_annotation('')
            
    def test_drawing(self, plot):
        """Test drawing functionality."""
        # Test single frame
        ax = plot.draw_frame()
        assert isinstance(ax, plt.Axes)
        
        # Test ratio frame
        ax_main, ax_ratio = plot.draw_frame(ratio=True)
        assert isinstance(ax_main, plt.Axes)
        assert isinstance(ax_ratio, plt.Axes)
        
    def test_cleanup(self, plot):
        """Test cleanup functionality."""
        ax = plot.draw_frame()
        plot.add_point(1.0, 2.0)
        plot.add_annotation('test')
        
        plot.reset()
        assert len(plot._points) == 0
        assert len(plot._annotations) == 0
        assert len(plot.legend_order) == 0
        
        AbstractPlot.close_all_figures()
        
    def test_axis_components(self, plot, ax):
        """Test axis component drawing."""
        plot.draw_axis_components(
            ax,
            xlabel='X',
            ylabel='Y',
            title='Test',
            xlim=(0, 1),
            ylim=(0, 1),
            xticks=[0, 0.5, 1],
            yticks=[0, 0.5, 1]
        )
        
        assert ax.get_xlabel() == 'X'
        assert ax.get_ylabel() == 'Y'
        assert ax.get_title() == 'Test'
        
    def test_axis_range(self, plot, ax):
        """Test axis range manipulation."""
        plot.set_axis_range(
            ax,
            xmin=0,
            xmax=1,
            ymin=0,
            ymax=1,
            ypad=0.1
        )
        
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        assert xlim == (0, 1)
        assert ylim[0] < 0  # Check padding
        assert ylim[1] > 1  # Check padding