"""ReeSaber: A Python package for creating and manipulating ReeSaber presets."""

__version__ = "1.0.1"

from .models.base import Color, Vector3, Transform
from .models.control import ControlPoint
from .models.driver import Driver, DriverType
from .modules.blur_saber import BlurSaber
from .modules.simple_trail import SimpleTrail
from .modules.vanilla_saber import VanillaSaber
from .config import SaberConfig
from .builder import ReeSaberBuilder
from .utils import create_rainbow_saber, configure_logging, create_gradient_saber, color_palette, clone_module, merge_configs, export_config_for_all_sabers

__all__ = [
    "Color",
    "Vector3",
    "Transform",
    "ControlPoint",
    "Driver",
    "DriverType",
    "BlurSaber",
    "SimpleTrail",
    "VanillaSaber",
    "SaberConfig",
    "ReeSaberBuilder",
    "create_rainbow_saber",
    "configure_logging",
    "create_gradient_saber",
    "color_palette",
    "clone_module",
    "merge_configs",
    "export_config_for_all_sabers",
    "__version__",
]