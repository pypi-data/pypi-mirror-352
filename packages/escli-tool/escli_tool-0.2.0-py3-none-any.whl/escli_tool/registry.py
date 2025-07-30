# registry.py
# Register a processor to process json files
from escli_tool.utils import get_logger

logger = get_logger()

CLASS_REGISTRY = {}


def register_class(cls):
    if hasattr(cls, 'CLS_BRIEF_NAME'):
        CLASS_REGISTRY[cls.CLS_BRIEF_NAME] = cls
    else:
        CLASS_REGISTRY[cls.__name__] = cls
    logger.info(f'Registering class: {cls.__name__}')
    return cls


def get_class(name):
    if name in CLASS_REGISTRY:
        cls = CLASS_REGISTRY.get(name)
        logger.info(f'Found registered processor: {cls.__name__}')
        return cls
    logger.warning(
        f"class: {name} is not registered in the list: {set(CLASS_REGISTRY)}")
    return CLASS_REGISTRY.get(name)


def list_registered_classes():
    return list(CLASS_REGISTRY.keys())
