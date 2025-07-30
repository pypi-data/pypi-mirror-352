# -*- coding: utf-8 -*-
from pip_services4_components.config import ConfigParams
from pip_services4_components.refer import References, Descriptor
from pip_services4_data.query import PagingParams, FilterParams

from eic_aichat_models.basemodels.data import BaseModel
from eic_aichat_models.basemodels.logic import BaseModelsService
from eic_aichat_models.basemodels.persistence import BaseModelsMemoryPersistence

BASE_MODEL1 = BaseModel(
    id='1',
    api='ai',
    name="name1",
    base_url="localhost:3000",
    supported_models=['model1', 'model2'],
)

BASE_MODEL2 = BaseModel(
    id='2',
    api='openapi',
    name="name2",
    base_url="localhost:3001",
    supported_models=['model3', 'model4'],
)


class TestBaseModelsService:
    persistence: BaseModelsMemoryPersistence
    service: BaseModelsService

    def setup_method(self):
        self.persistence = BaseModelsMemoryPersistence()
        self.persistence.configure(ConfigParams())

        self.service = BaseModelsService()
        self.service.configure(ConfigParams())

        references = References.from_tuples(
            Descriptor('aichatmodels-basemodels', 'persistence', 'memory', 'default', '1.0'), self.persistence,
            Descriptor('aichatmodels-basemodels', 'service', 'default', 'default', '1.0'), self.service
        )

        self.service.set_references(references)

        self.persistence.open(None)

    def teardown_method(self):
        self.persistence.close(None)

    def test_crud_operations(self):
        # Create the first model
        model = self.service.create_model(None, BASE_MODEL1)
        assert BASE_MODEL1.api == model.api
        assert BASE_MODEL1.base_url == model.base_url
        assert model.supported_models is not None

        # Create the second model
        model = self.service.create_model(None, BASE_MODEL2)
        assert BASE_MODEL2.api == model.api
        assert BASE_MODEL2.base_url == model.base_url
        assert model.supported_models is not None

        # Get all models
        page = self.service.get_models(None, FilterParams(), PagingParams())
        assert page is not None
        assert len(page.data) == 2

        model1: BaseModel = page.data[0]

        # Update the model
        model1.api = 'ABC'

        model = self.service.update_model(None, model1)
        assert model1.id == model.id
        assert 'ABC' == model.api

        # Get model by api
        model = self.service.get_model_by_api(None, model1.api)
        assert model1.id == model.id

        # Delete the model
        model = self.service.delete_model_by_id(None, model1.id)
        assert model1.id == model.id

        # Try to get deleted model
        model = self.service.get_model_by_id(None, model1.id)
        assert model is None
