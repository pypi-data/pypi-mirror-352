from IPython.display import display
import numpy as np
import plotly.graph_objects as go
import time
import ipywidgets
from IPython.core.displaypub import DisplayPublisher
from IPython.core.interactiveshell import InteractiveShell
from types import ModuleType
import plotly.basedatatypes

class contextAware(type):
    class InterceptingPublisher(DisplayPublisher):
        def publish(
            self, data, metadata=None, source=None, *, transient=None, update=False
        ):
            if "application/vnd.plotly.v1+json" in data:
                print("show invoked")
                return
            else:
                pass

    @staticmethod
    def isNoteBookEnv():
        from IPython import get_ipython

        ip = get_ipython()
        try:
            if ip is None:
                return False
            return True
        except Exception as e:
            return False

    # Define time processing of environment
    def __new__(cls, name, bases, attrs):
        new_class = super().__new__(cls, name, bases, attrs)
        if contextAware.isNoteBookEnv():
            new_class.shell = InteractiveShell.instance()
            # global instance but assigned to attr for easy retreval
            new_class.shell.display_pub = contextAware.InterceptingPublisher()

        return new_class


def f(*args, **kwargs):
    """
    Dummy function to test the metaclass.
    """
    print("display overwrite")


# --- Simplified Demo Class ---
class _test_Plots:

    @staticmethod
    def scatter(x, y):
        return go.Figure(go.Scatter(x=x, y=y, mode="lines+markers"))

    @staticmethod
    def show_scatter(x, y):
        fig = _demo_Plots.scatter(x, y)
        # sendPlotlyFigToGui(fig)
        fig.show()
        return fig

    @staticmethod
    def updateLiveScatter(fig, x_new, y_new):
        if not isinstance(fig, go.Figure):
            fig = go.Figure(fig)
        xs = (
            [*fig.data[0].x, *x_new]
            if isinstance(x_new, (list, tuple))
            else [*fig.data[0].x, x_new]
        )
        ys = (
            [*fig.data[0].y, *y_new]
            if isinstance(y_new, (list, tuple))
            else [*fig.data[0].y, y_new]
        )
        fig.data[0].x = xs
        fig.data[0].y = ys
        # Update data on the figure
        # For FigureWidget, batch_update is better. For go.Figure, direct assignment is fine.
        if isinstance(fig, go.FigureWidget):
            with fig.batch_update():
                fig.data[0].x = xs
                fig.data[0].y = ys
        else:
            fig.data[0].x = xs
            fig.data[0].y = ys

        display(fig)  # Crucial: direct display call
        return fig
