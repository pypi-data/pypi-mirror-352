import os

from aimms.model.enums.me_attribute_types import AttributeType

class AimmsLibrary:
    def __init__(self, name : str, aimms_version: str, prefix : str = "", **kwargs): # type: ignore
        self.name = name
        self.prefix = prefix
        self.aimms_version = aimms_version
        self.project = kwargs.get("project", None) # type: ignore

        self.me_handle = kwargs.get("model_reflection_handle")
        if self.prefix:
            self.prefix = self.project.aimms_api.get_attribute(self.me_handle, AttributeType.PREFIX.value)
        