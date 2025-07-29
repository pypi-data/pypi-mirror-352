import dataclasses
from typing import Optional
from javaobj import JavaObject
from .HomeTexture import HomeTexture
from .ModelBase import ModelBase
from ..BuildContext import BuildContext


@dataclasses.dataclass
class HomeMaterial(ModelBase):
    name: str
    color: Optional[int]
    texture: Optional[HomeTexture]
    shininess: Optional[float]

    @classmethod
    def from_javaobj(cls, o: JavaObject, build_context: BuildContext) -> 'HomeMaterial':
        return cls(
            name=o.name,
            color=o.color,
            texture=HomeTexture.from_javaobj(o.texture, build_context) if o.texture else None,
            shininess=o.shininess,
        )
