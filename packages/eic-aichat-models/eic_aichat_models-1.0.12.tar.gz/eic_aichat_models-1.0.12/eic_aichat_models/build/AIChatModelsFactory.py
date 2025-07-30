# -*- coding: utf-8 -*-
from pip_services4_components.refer import Descriptor
from pip_services4_components.build import Factory

from eic_aichat_models.basemodels.logic.BaseModelsService import BaseModelsService
from eic_aichat_models.basemodels.persistence.BaseModelsMemoryPersistence import BaseModelsMemoryPersistence
from eic_aichat_models.basemodels.persistence.BaseModelsMongoDbPersistence import BaseModelsMongoDbPersistence


class AIChatModelsFactory(Factory):
    __MemoryPersistenceDescriptor = Descriptor('aichatmodels-basemodels', 'persistence', 'memory', '*', '1.0')
    __MongoDbPersistenceDescriptor = Descriptor('aichatmodels-basemodels', 'persistence', 'mongodb', '*', '1.0')
    __ServiceDescriptor = Descriptor('aichatmodels-basemodels', 'service', 'default', '*', '1.0')


    def __init__(self):
        super().__init__()

        self.register_as_type(self.__MemoryPersistenceDescriptor, BaseModelsMemoryPersistence)
        self.register_as_type(self.__MongoDbPersistenceDescriptor, BaseModelsMongoDbPersistence)
        self.register_as_type(self.__ServiceDescriptor, BaseModelsService)
