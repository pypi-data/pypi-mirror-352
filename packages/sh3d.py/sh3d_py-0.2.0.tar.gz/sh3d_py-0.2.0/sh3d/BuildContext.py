from typing import Dict, TYPE_CHECKING
from sh3d.AssetManager import AssetManager

if TYPE_CHECKING:
    from sh3d.model.Wall import Wall
    from sh3d.model.Level import Level

class BuildContext:
    asset_manager: AssetManager
    level_cache: Dict[str, 'Level'] = {}
    wall_cache: Dict[str, 'Wall'] = {}

    def __init__(self, asset_manager: AssetManager):
        self.asset_manager = asset_manager
        self.level_cache = {}
        self.wall_cache = {}
