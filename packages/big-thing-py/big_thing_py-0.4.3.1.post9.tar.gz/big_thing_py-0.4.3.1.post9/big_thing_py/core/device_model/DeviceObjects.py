from big_thing_py.core.service_model import SkillObjects
from big_thing_py.core.service_model.SkillObjects import MXClassproperty
from typing import Set, Dict, List, Union, Any

ALL_DEVICE_TYPES: dict[str, type["MXDeviceCategory"]] = {}


class MXDeviceCategory:
    """Base class for MX device types."""

    device_type: str
    skills: Set[SkillObjects.Skill]

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Register a subclass."""
        super().__init_subclass__(**kwargs)
        cls.device_type = cls.__name__
        try:
            ALL_DEVICE_TYPES[cls.device_type] = cls
        except NotImplementedError:
            pass

    @MXClassproperty
    def name(cls) -> str:
        """Return the class name as a string."""
        return cls.__name__
