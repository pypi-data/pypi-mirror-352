# t
# from plot_interceptor import isNoteBookEnv
import plotly.graph_objects as go
from plotly.basedatatypes import BaseFigure
from IPython.display import display

# print(isNoteBookEnv())
import plotly.graph_objects as go
from plotly.basedatatypes import BaseFigure

try:

    shell = InteractiveShell.instance()

    class InterceptingPublisher(DisplayPublisher):
        def publish(
            self, data, metadata=None, source=None, *, transient=None, update=False
        ):
            if "application/vnd.plotly.v1+json" in data:
                print("show invoked")
                return
            else:
                pass
                # print(f"{data}")
            # return super().publish(
            #     data, metadata, source, transient=transient, update=update
            # )

    shell.display_pub = InterceptingPublisher()

except Exception as e:
    print("Failed to set up custom display publisher:", e)

# # plotly.io.renderers
# fig = go.Figure(data=go.Scatter(x=[1, 2, 3], y=[4, 5, 6]))

NewFigType = type("test_fig", (BaseFigure,), {})


def test_display(self):
    print("displaying")


def test_call(self):
    print("call")


NewFigType._ipython_display_ = test_display
NewFigType.__call__ = test_call

new_fig = NewFigType()
# # object.__setattr__(fig, "enabled", True)

super(NewFigType, new_fig).__setattr__("__call__", test_call)

import inspect

# print(inspect.isclass(fig))
# # print(callable(fig))
# display(new_fig)
new_fig.show()

# class TestIntercept:
#     from IPython.core.interactiveshell import InteractiveShell
#     from IPython.core.displaypub import DisplayPublisher
