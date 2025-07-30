from abc import ABC, abstractmethod
from typing import Optional

from pip_services4_components.context import IContext
from pip_services4_data.query import DataPage, PagingParams, FilterParams

from ..data import BaseModel


class IBaseModelsService(ABC):

    def get_models(self, context: Optional[IContext], filter_params: FilterParams, paging: PagingParams) -> DataPage:
        raise NotImplementedError("Method is not implemented")

    def get_model_by_id(self, context: Optional[IContext], model_id: str) -> BaseModel:
        raise NotImplementedError("Method is not implemented")

    def get_model_by_api(self, context: Optional[IContext], api: str) -> BaseModel:
        raise NotImplementedError("Method is not implemented")
    
    def get_model_by_name(self, context: Optional[IContext], name: str) -> BaseModel:
        raise NotImplementedError("Method is not implemented")

    def create_model(self, context: Optional[IContext], model: BaseModel) -> BaseModel:
        raise NotImplementedError("Method is not implemented")

    def update_model(self, context: Optional[IContext], model: BaseModel) -> BaseModel:
        raise NotImplementedError("Method is not implemented")

    def delete_model_by_id(self, context: Optional[IContext], model_id: str) -> BaseModel:
        raise NotImplementedError("Method is not implemented")