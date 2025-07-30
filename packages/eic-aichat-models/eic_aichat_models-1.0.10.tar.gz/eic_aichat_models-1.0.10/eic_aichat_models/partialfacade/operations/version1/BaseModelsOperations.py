# -*- coding: utf-8 -*-
import json

import bottle
from pip_services4_commons.convert import TypeCode
from pip_services4_components.refer import Descriptor, IReferences
from pip_services4_data.validate import ObjectSchema
from pip_services4_http.controller import RestOperations, RestController
from pip_services4_components.context import Context

from eic_aichat_models.basemodels.data import BaseModel, BaseModelSchema
from eic_aichat_models.basemodels.logic.IBaseModelsService import IBaseModelsService

from eic_aichat_users.partialfacade.operations.version1.Authorize import AuthorizerV1

class BaseModelsOperations(RestOperations):
    def __init__(self):
        super().__init__()
        self._base_models_service: IBaseModelsService = None
        self._dependency_resolver.put("basemodels-service", Descriptor('aichatmodels-basemodels', 'service', '*', '*', '1.0'))

    def configure(self, config):
        super().configure(config)

    def set_references(self, references: IReferences):
        super().set_references(references)
        self._base_models_service = self._dependency_resolver.get_one_required('basemodels-service')

    def get_base_models(self):
        context = Context.from_trace_id(self._get_trace_id())
        filter_params = self._get_filter_params()
        paging_params = self._get_paging_params()
        try:
            res = self._base_models_service.get_models(context, filter_params, paging_params)
            res.data = [topic.to_dict() for topic in res.data]
            return self._send_result(res)
        except Exception as err:
            return self._send_error(err)

    def get_base_model_by_id(self, id):
        context = Context.from_trace_id(self._get_trace_id())
        try:
            res = self._base_models_service.get_model_by_id(context, id)
            return self._send_result(res.to_dict())
        except Exception as err:
            return self._send_error(err)
        
    def get_base_model_by_name(self, name):
        context = Context.from_trace_id(self._get_trace_id())
        try:
            res = self._base_models_service.get_model_by_name(context, name)
            return self._send_result(res.to_dict())
        except Exception as err:
            return self._send_error(err)

    def create_base_model(self):
        context = Context.from_trace_id(self._get_trace_id())
        data = bottle.request.json
        base_model = data if isinstance(data, dict) else json.loads(data)
        base_model = None if not base_model else BaseModel(**base_model)
        try:
            res = self._base_models_service.create_model(context, base_model)
            return self._send_result(res.to_dict())
        except Exception as err:
            return self._send_error(err)

    def update_base_model(self):
        context = Context.from_trace_id(self._get_trace_id())
        data = bottle.request.json
        base_model = data if isinstance(data, dict) else json.loads(data)
        base_model = None if not base_model else BaseModel(**base_model)
        try:
            res = self._base_models_service.update_model(context, base_model)
            return self._send_result(res.to_dict())
        except Exception as err:
            return self._send_error(err)

    def delete_base_model_by_id(self, id):
        context = Context.from_trace_id(self._get_trace_id())
        try:
            res = self._base_models_service.delete_model_by_id(context, id)
            return self._send_result(res.to_dict())
        except Exception as err:
            return self._send_error(err)

    def register_routes(self, controller: RestController, auth: AuthorizerV1):
        # controller.register_route('get', '/base_models', ObjectSchema(True)
        #                           .with_optional_property("filter", FilterParamsSchema())
        #                           .with_optional_property("paging", PagingParamsSchema()),
        #                           self.get_base_models)
        controller.register_route_with_auth('get', '/models/base', None, auth.signed(),
                            self.get_base_models)

        controller.register_route_with_auth('get', '/models/base/<id>', ObjectSchema(True)
                            .with_optional_property("base_model_id", TypeCode.String), auth.signed(),
                            self.get_base_model_by_id)

        controller.register_route_with_auth('post', '/models/base', ObjectSchema(True)
                            .with_required_property("body", BaseModelSchema()), auth.admin(),
                            self.create_base_model)

        controller.register_route_with_auth('put', '/models/base', ObjectSchema(True)
                            .with_required_property("body", BaseModelSchema()), auth.admin(),
                            self.update_base_model)

        controller.register_route_with_auth('delete', '/models/base/<id>', ObjectSchema(True)
                            .with_required_property("base_model_id", TypeCode.String), auth.admin(),
                            self.delete_base_model_by_id)

