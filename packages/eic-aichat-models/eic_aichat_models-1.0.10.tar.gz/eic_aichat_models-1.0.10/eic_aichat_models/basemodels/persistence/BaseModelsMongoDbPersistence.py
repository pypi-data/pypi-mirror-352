# -*- coding: utf-8 -*-
from typing import Optional, Any

from pip_services4_components.context import IContext
from pip_services4_data.query import DataPage, PagingParams, FilterParams
from pip_services4_mongodb.persistence import IdentifiableMongoDbPersistence

from ..data import BaseModel
from .IBaseModelsPersistence import IBaseModelsPersistence


class BaseModelsMongoDbPersistence(IdentifiableMongoDbPersistence, IBaseModelsPersistence):

    def __init__(self):
        super().__init__('base_models')

        self._max_page_size = 1000

    def __compose_filter(self, filter_params: FilterParams):
        filter_params = filter_params or FilterParams()

        filters = []

        id = filter_params.get_as_nullable_string('id')
        if id is not None:
            filters.append({'_id': id})

        api = filter_params.get_as_nullable_string('api')
        if api is not None:
            filters.append({'api': api})
        
        name = filter_params.get_as_nullable_string('name')
        if name is not None:
            filters.append({'name': name})

        temp_models = filter_params.get_as_nullable_string('supported_models')
        if temp_models is not None:
            models = temp_models.split(',')
            filters.append({'supported_models': {'$in': models}})

        return None if len(filters) < 1 else {'$and': filters}

    def get_page_by_filter(self, context: Optional[IContext], filter: Any, paging: PagingParams,
                           sort: Any = None, select: Any = None) -> DataPage:
        return super().get_page_by_filter(context, self.__compose_filter(filter), paging, None, None)

    def get_one_by_api(self, context: Optional[IContext], api: str) -> BaseModel:
        criteria = {'api': api}
        item = self._collection.find_one(criteria)

        if item is None:
            self._logger.trace(context, "Cannot find base model with api=%s", str(api))
        else:
            self._logger.trace(context, "Found base model with api=%s", str(api))

        item = self._convert_to_public(item)
        return item
    
    def get_one_by_name(self, context: Optional[IContext], name: str) -> BaseModel:
        criteria = {'name': name}
        item = self._collection.find_one(criteria)

        if item is None:
            self._logger.trace(context, "Cannot find base model with name=%s", str(name))
        else:
            self._logger.trace(context, "Found base model with name=%s", str(name))

        item = self._convert_to_public(item)
        return item
    
