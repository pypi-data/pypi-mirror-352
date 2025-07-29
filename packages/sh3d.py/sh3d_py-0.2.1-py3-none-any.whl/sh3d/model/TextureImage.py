import io
import weakref
import dataclasses
from typing import Any, ClassVar
from PIL import Image
from javaobj import JavaObject
from .Content import Content
from .ModelBase import ModelBase
from ..BuildContext import BuildContext


@dataclasses.dataclass(frozen=True)
class TextureImage(ModelBase):
    name: str
    image: Content
    width: float
    height: float
    _instances: ClassVar[weakref.WeakValueDictionary[str, 'TextureImage']] = weakref.WeakValueDictionary()


    def __new__(cls, name: str, *_args: Any, **_kwargs: Any) -> 'TextureImage':
        if name in cls._instances:
            return cls._instances[name]
        instance = super().__new__(cls)
        cls._instances[name] = instance
        return instance

    @classmethod
    def from_content(cls, content: Content) -> 'TextureImage':
        image_info = Image.open(io.BytesIO(content.data))
        return cls(
            name=content.content_digest.name,
            image=content,
            width=image_info.width,
            height=image_info.height
        )

    @classmethod
    def from_javaobj(cls, o: JavaObject, build_context: BuildContext) -> 'TextureImage':
        image = build_context.asset_manager.get_pattern(o.name)
        image_info = Image.open(io.BytesIO(image.data))

        return cls(
            name=o.name,
            image=image,
            width=image_info.width,
            height=image_info.height
        )

    @classmethod
    def from_xml_dict(cls, data: dict, build_context: BuildContext) -> 'ModelBase':
        raise NotImplementedError

    @classmethod
    def from_str(cls, pattern_name: str, build_context: BuildContext) -> 'TextureImage':
        image = build_context.asset_manager.get_pattern(pattern_name)
        image_info = Image.open(io.BytesIO(image.data))
        return cls(
            name=pattern_name,
            image=image,
            width=image_info.width,
            height=image_info.height
        )
