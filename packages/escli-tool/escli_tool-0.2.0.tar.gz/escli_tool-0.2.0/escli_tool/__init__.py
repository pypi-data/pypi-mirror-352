import importlib
import pkgutil

import escli_tool.processor

for _, module_name, _ in pkgutil.iter_modules(escli_tool.processor.__path__):
    importlib.import_module(f"escli_tool.processor.{module_name}")