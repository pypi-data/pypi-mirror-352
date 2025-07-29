import dataclasses
from javaobj import JavaObject
from .Content import Content
from .ModelBase import ModelBase
from ..BuildContext import BuildContext


@dataclasses.dataclass(frozen=True)
class HomeTexture(ModelBase):
    name: str
    image: Content
    width: float
    height: float
    left_to_right_oriented: bool

    @classmethod
    def from_javaobj(cls, o: JavaObject, build_context: BuildContext) -> 'HomeTexture':
        return cls(
            name=o.name,
            image=build_context.asset_manager.get_texture(o.name),
            width=o.width,
            height=o.height,
            left_to_right_oriented=o.left_to_right_oriented
        )

    @classmethod
    def from_xml_dict(cls, data: dict, build_context: BuildContext) -> 'HomeTexture':
        raise NotImplementedError
        #return cls(
        #    name=data.get('@name'),
        #    image=None,
        #    width=float(data.get('@width')),
        #    height=float(data.get('@height')),
        #    left_to_right_oriented=False
        #)
