import dataclasses
from typing import Optional
from javaobj import JavaObject
from .BackgroundImage import BackgroundImage
from .ModelBase import ModelBase
from ..BuildContext import BuildContext


@dataclasses.dataclass(unsafe_hash=True)
class Level(ModelBase):
    identifier: str
    name: str
    elevation: float
    floor_thickness: float
    height: float
    background_image: Optional[BackgroundImage]
    is_visible: bool
    is_viewable: bool
    elevation_index: int

    @classmethod
    def from_javaobj(cls, o: JavaObject, build_context: BuildContext) -> 'Level':
        identifier = o.id
        if identifier in build_context.level_cache:
            return build_context.level_cache[identifier]

        level = cls(
            identifier=identifier,
            name=o.name,
            elevation=o.elevation,
            floor_thickness=o.floorThickness,
            height=o.height,
            background_image=BackgroundImage.from_javaobj(o.backgroundImage, build_context) if o.backgroundImage else None,
            is_visible=o.visible,
            is_viewable=o.viewable,
            elevation_index=o.elevationIndex
        )

        build_context.level_cache[identifier] = level

        return level

    @classmethod
    def from_identifier(cls, identifier: str, build_context: BuildContext) -> 'Level':
        wall = build_context.level_cache.get(identifier)
        if not wall:
            raise ValueError('Identifier not found in cache')
        return wall

    @classmethod
    def from_xml_dict(cls, data: dict, build_context: BuildContext) -> 'Level':
        identifier = data.get('@id')
        if not identifier:
            raise ValueError('@id is required')
        background_image = data.get('backgroundImage')
        if identifier in build_context.level_cache:
            return build_context.level_cache[identifier]

        level = cls(
            identifier=identifier,
            name=cls.required_str(data.get('@name')),
            elevation=cls.required_float(data.get('@elevation')),
            floor_thickness=cls.required_float(data.get('@floorThickness')),
            height=cls.required_float(data.get('@height')),
            background_image=BackgroundImage.from_xml_dict(background_image, build_context) if background_image else None,
            is_visible=data.get('@visible', 'true') == 'true',
            is_viewable=data.get('@viewable', 'true') == 'true',
            elevation_index=cls.required_int(data.get('@elevationIndex'))
        )

        build_context.level_cache[identifier] = level

        return level
