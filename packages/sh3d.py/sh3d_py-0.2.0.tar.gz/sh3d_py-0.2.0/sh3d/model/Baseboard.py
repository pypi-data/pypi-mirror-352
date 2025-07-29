import dataclasses

from javaobj import JavaObject

from sh3d.BuildContext import BuildContext
from sh3d.model.HomeTexture import HomeTexture
from sh3d.model.ModelBase import ModelBase

@dataclasses.dataclass
class BaseBoard(ModelBase):
    thickness: float
    height: float
    color: int
    texture: HomeTexture

    @classmethod
    def from_javaobj(cls, o: JavaObject, build_context: BuildContext) -> 'ModelBase':
        raise NotImplementedError

    @classmethod
    def from_xml_dict(cls, data: dict, build_context: BuildContext) -> 'ModelBase':
        raise NotImplementedError
