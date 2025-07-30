from IPython.core.formatters



class WindowDisplay:
	from plotly.io._base_renderers import MimetypeRenderer
	from plotly.offline.offline import _get_jconfig, get_plotlyjs
	import json
	from plotly.io.json import to_json
	class Renderer(MimetypeRenderer):
		"""
		Renderer to display figures using the plotly mime type.  This renderer is
		compatible with VSCode and nteract.

		mime type: 'application/vnd.plotly.v1+json'
		"""

		def __init__(self, config=None):
			self.config = dict(config) if config else {}

		def to_mimebundle(self, fig_dict):
			config = _get_jconfig(self.config)
			if config:
				fig_dict["config"] = config

			json_compatible_fig_dict = json.loads(
				to_json(fig_dict, validate=False, remove_uids=False)
			)
			print("got,data)")

			return {"application/vnd.plotly.v1+json": json_compatible_fig_dict}


    HTML_TEMPLATE = """
    <html><head><script src=\"https://cdn.plot.ly/plotly-latest.min.js\"></script></head>
    <body><div id=\"graph_div\"></div></body></html>
    """
