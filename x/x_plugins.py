from importlib.metadata import entry_points

from cxbind import CxBind
from cxbind.plugin import Plugin

app = CxBind()

plugin_eps = entry_points(group="cxbind.plugins")
print("plugin_eps", plugin_eps)


for ep in plugin_eps:
    print("ep", ep)

    plugin: Plugin = ep.load()()
    print("plugin", plugin)
    plugin.install(app)
