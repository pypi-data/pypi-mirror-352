# -*- coding: utf-8 -*-
from pip_services4_data.query import FilterParams, PagingParams

from eic_aichat_models.basemodels.data.BaseModel import BaseModel
from eic_aichat_models.basemodels.persistence.IBaseModelsPersistence import IBaseModelsPersistence

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

BASE_MODEL3 = BaseModel(
    id='3',
    api='glhf',
    name="name3",
    base_url="localhost:3002",
    supported_models=['model5'],
)


class BaseModelsPersistenceFixture:
    _persistence: IBaseModelsPersistence

    def __init__(self, persistence: IBaseModelsPersistence):
        assert persistence is not None
        self._persistence = persistence

    def test_create_base_models(self):
        # Create the first model
        entity = self._persistence.create(None, BASE_MODEL1)
        assert BASE_MODEL1.api == entity.api
        assert BASE_MODEL1.base_url == entity.base_url
        assert entity.supported_models is not None

        # Create the second model
        entity = self._persistence.create(None, BASE_MODEL2)
        assert BASE_MODEL2.api == entity.api
        assert BASE_MODEL2.base_url == entity.base_url
        assert entity.supported_models is not None

        # Create the third model
        entity = self._persistence.create(None, BASE_MODEL3)
        assert BASE_MODEL3.api == entity.api
        assert BASE_MODEL3.base_url == entity.base_url
        assert entity.supported_models is not None

    def test_crud_operations(self):
        # Create items
        self.test_create_base_models()

        # Get all models
        page = self._persistence.get_page_by_filter(None, FilterParams(), PagingParams())
        assert page is not None
        assert len(page.data) == 3

        entity1: BaseModel = page.data[0]

        # Update the model
        entity1.api = 'ABC'

        entity = self._persistence.update(None, entity1)
        assert entity1.id == entity.id
        assert 'ABC' == entity.api

        # Get model by api
        entity = self._persistence.get_one_by_api(None, entity1.api)
        assert entity1.id == entity.id

        # Delete the model
        entity = self._persistence.delete_by_id(None, entity1.id)
        assert entity1.id == entity.id

        # Try to get deleted model
        entity = self._persistence.get_one_by_id(None, entity1.id)
        assert entity is None

    def test_get_with_filters(self):
        # Create items
        self.test_create_base_models()

        # Filter by id
        page = self._persistence.get_page_by_filter(None, FilterParams.from_tuples('id', '1'), PagingParams())
        assert len(page.data) != 0

        # Filter by supported_models
        page = self._persistence.get_page_by_filter(None,
                                                    FilterParams.from_tuples('supported_models', 'model1'),
                                                    PagingParams())
        assert len(page.data) != 0

        # Filter by api
        page = self._persistence.get_page_by_filter(None,
                                                    FilterParams.from_tuples('api', 'openapi'),
                                                    PagingParams())
        assert len(page.data) != 0
