# -*- coding: utf-8 -*-
from typing import Optional, Any, Callable

from pip_services4_components.context import IContext
from pip_services4_data.query import DataPage, PagingParams, FilterParams, SortParams
from pip_services4_persistence.persistence import IdentifiableMemoryPersistence

from ..data import BaseModel
from .IBaseModelsPersistence import IBaseModelsPersistence


class BaseModelsMemoryPersistence(IdentifiableMemoryPersistence, IBaseModelsPersistence):

    def __init__(self):
        super().__init__()

        self._max_page_size = 1000

    def __compose_filter(self, filter_params: FilterParams) -> Callable[[BaseModel], bool]:
        filter_params = filter_params or FilterParams()

        id = filter_params.get_as_nullable_string('id')
        api = filter_params.get_as_nullable_string('api')
        supported_models = filter_params.get_as_nullable_string('supported_models')
        name = filter_params.get_as_nullable_string('name')
        names = filter_params.get_as_nullable_string('names')

        if isinstance(names, str):
            names = names.split(',')
        if not isinstance(names, list):
            names = None

        if isinstance(supported_models, str):
            supported_models = supported_models.split(',')
        if not isinstance(supported_models, list):
            supported_models = None

        def filter_action(item: BaseModel) -> bool:
            if id is not None and item.id != id:
                return False
            if api is not None and item.api != api:
                return False
            if name is not None and item.name != name:
                return False
            if names is not None and item.name not in names:
                return False
            if supported_models is not None:
                if not any(model in supported_models for model in item.supported_models):
                    return False
            return True

        return filter_action

    def get_page_by_filter(self, context: Optional[IContext], filter: FilterParams, paging: PagingParams,
                           sort: SortParams = None, select: Any = None) -> DataPage:
        return super().get_page_by_filter(context, self.__compose_filter(filter), paging, None, None)

    def get_one_by_api(self, context: Optional[IContext], api: str) -> BaseModel:
        filtered = list(filter(lambda item: item.api == api, self._items))
        item = None if len(filtered) < 1 else filtered[0]

        if item is None:
            self._logger.trace(context, "Cannot find base model with api=%s", str(api))
        else:
            self._logger.trace(context, "Found base model with api=%s", str(api))

        return item
    
    def get_one_by_name(self, context: Optional[IContext], name: str) -> BaseModel:
        filtered = list(filter(lambda item: item.name == name, self._items))
        item = None if len(filtered) < 1 else filtered[0]

        if item is None:
            self._logger.trace(context, "Cannot find base model with name=%s", str(name))
        else:
            self._logger.trace(context, "Found base model with name=%s", str(name))

        return item
