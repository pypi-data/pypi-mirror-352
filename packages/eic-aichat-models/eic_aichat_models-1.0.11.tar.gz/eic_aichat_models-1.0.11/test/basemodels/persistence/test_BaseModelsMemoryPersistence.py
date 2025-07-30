# -*- coding: utf-8 -*-
from eic_aichat_models.basemodels.persistence import BaseModelsMemoryPersistence
from test.basemodels.persistence.BaseModelsPersistenceFixture import BaseModelsPersistenceFixture


class TestBaseModelsMemoryPersistence:
    persistence: BaseModelsMemoryPersistence
    fixture: BaseModelsPersistenceFixture

    def setup_method(self):
        self.persistence = BaseModelsMemoryPersistence()

        self.fixture = BaseModelsPersistenceFixture(self.persistence)

        self.persistence.open(None)
        self.persistence.clear(None)

    def teardown_method(self):
        self.persistence.close(None)

    def test_crud_operations(self):
        self.fixture.test_crud_operations()

    def test_get_with_filters(self):
        self.fixture.test_get_with_filters()
