import os
import inspect
from .interface import PluginInterface


class PluginManager:
    def __init__(self):
        self.plugin_folder = os.path.dirname(__file__)
        self.plugins = self._load_plugins()

    def _load_plugins(self):
        plugins = []
        for filename in os.listdir(self.plugin_folder):
            if (
                filename.endswith(".py")
                and filename != "__init__.py"
                and filename != "interface.py"
                and filename != "manager.py"
            ):
                module_name = filename[:-3]
                module = __import__(
                    f"aixblock_core.plugins.{module_name}", fromlist=["*"]
                )
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (
                        inspect.isclass(attr)
                        and issubclass(attr, PluginInterface)
                        and attr is not PluginInterface
                    ):
                        plugins.append(attr())
        return plugins

    async def execute_all(self):
        for plugin in self.plugins:
            await plugin.execute()


async def run_plugins():
    plugin_manager = PluginManager()
    await plugin_manager.execute_all()
