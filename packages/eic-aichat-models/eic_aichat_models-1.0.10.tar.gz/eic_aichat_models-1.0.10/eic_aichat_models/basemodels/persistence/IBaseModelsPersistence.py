# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from typing import Optional

from pip_services4_components.context import IContext
from pip_services4_data.query import DataPage, PagingParams, FilterParams

from ..data import BaseModel


class IBaseModelsPersistence(ABC):
    @abstractmethod
    def __init__(self):
        pass

    def get_page_by_filter(self, context: Optional[IContext], filter_params: FilterParams, paging: PagingParams) -> DataPage:
        pass

    def get_one_by_id(self, context: Optional[IContext], entity_id: str) -> BaseModel:
        pass

    def get_one_by_api(self, context: Optional[IContext], api: str) -> BaseModel:
        pass

    def get_one_by_name(self, context: Optional[IContext], name: str) -> BaseModel:
        pass

    def create(self, context: Optional[IContext], entity: BaseModel) -> BaseModel:
        pass

    def update(self, context: Optional[IContext], entity: BaseModel) -> BaseModel:
        pass

    def delete_by_id(self, context: Optional[IContext], entity_id: str) -> BaseModel:
        pass
