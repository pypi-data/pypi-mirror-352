# -*- coding: utf-8 -*-

from pip_services4_commons.convert import TypeCode
from pip_services4_data.validate import ObjectSchema


class BaseModelSchema(ObjectSchema):
    def __init__(self):
        super().__init__()

        self.with_optional_property('id', TypeCode.String)
        self.with_required_property('name', TypeCode.String)
        self.with_required_property('api', TypeCode.String)
        self.with_optional_property('base_url', TypeCode.String)
        self.with_optional_property('supported_models', TypeCode.Array)
