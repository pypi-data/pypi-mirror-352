# -*- coding: utf-8 -*-
from typing import Dict, List
from pip_services4_data.data import IStringIdentifiable


class BaseModel(IStringIdentifiable):
    def __init__(self, id: str = None, name: str = None, api: str = None, base_url: str = None, supported_models: List[str] = None):
        self.id = id
        self.name = name
        self.api = api
        self.base_url = base_url
        self.supported_models = supported_models

    def to_dict(self) -> Dict[str, str]:
        return {
            'id': self.id,
            'name': self.name,
            'api': self.api,
            'base_url': self.base_url,
            'supported_models': ','.join(self.supported_models)
        }
