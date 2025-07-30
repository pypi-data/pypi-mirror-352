# -*- coding: utf-8 -*-
from copy import deepcopy
from typing import Optional, Callable, List

from pip_services4_commons.commands import ICommandable, CommandSet
from pip_services4_commons.config import IConfigurable, ConfigParams
from pip_services4_commons.data import FilterParams, PagingParams, DataPage, IdGenerator
from pip_services4_commons.refer import IReferenceable, Descriptor, IReferences

from ..data import EntityTypeV1
from ..data import EntityV1

from .BasicCommandSet import BasicCommandSet
from .IBasicService import IBasicService


class BasicService(IBasicService, IConfigurable, IReferenceable, ICommandable):

    def __init__(self):
        self.__max_page_size: int = 100
        self.__items: List[EntityV1] = []
        self.__command_set: BasicCommandSet = None

    def configure(self, config: ConfigParams):
        pass

    def set_references(self, references: IReferences):
        pass

    def __compose_filter(self, filter_params: FilterParams) -> Callable[[EntityV1], bool]:
        filter_params = filter_params or FilterParams()

        id = filter_params.get_as_nullable_string("id")
        siteId = filter_params.get_as_nullable_string("site_id")
        name = filter_params.get_as_nullable_string("name")

        temp_names = filter_params.get_as_nullable_string("names")
        names = None if temp_names is None else temp_names.split(",")

        def compare(item: EntityV1) -> bool:
            if id is not None and item.id != id:
                return False
            if siteId is not None and item.site_id is not siteId:
                return False
            if name is not None and item.name is not name:
                return False
            if names is not None and item.name in names:
                return False
            return True

        return compare

    def get_command_set(self) -> CommandSet:
        if self.__command_set is None:
            self.__command_set = BasicCommandSet(self)

        return self.__command_set

    def get_entities(self, correlation_id: Optional[str], filter_params: FilterParams,
                     paging: PagingParams) -> DataPage:
        filter_entities = self.__compose_filter(filter_params)
        entities = list(filter(filter_entities, self.__items))

        # Extract a page
        paging = paging or PagingParams()
        skip = paging.get_skip(-1)
        take = paging.get_take(self.__max_page_size)
        total = None

        if paging.total: total = len(entities)
        if skip > 0: entities = entities[skip:]

        entities = entities[:take]
        return DataPage(entities, total)

    def get_entity_by_id(self, correlation_id: Optional[str], entity_id: str) -> EntityV1:
        entities = list(filter(lambda x: x.id == entity_id, self.__items))
        entity = None if len(entities) == 0 else entities[0]
        return entity

    def get_entity_by_name(self, correlation_id: Optional[str], name: str) -> EntityV1:
        entities = list(filter(lambda x: x.name == name, self.__items))
        entity = None if len(entities) == 0 else entities[0]
        return entity

    def create_entity(self, correlation_id: Optional[str], entity: EntityV1) -> Optional[EntityV1]:
        if entity is None:
            return None

        entity.id = entity.id or IdGenerator.next_long()
        entity.type = entity.type or EntityTypeV1.Unknown

        self.__items.append(entity)

        return entity

    def update_entity(self, correlation_id: Optional[str], entity: EntityV1) -> Optional[EntityV1]:
        ids = list(map(lambda x: x.id, self.__items))

        if entity.id not in ids:
            return None

        index = ids.index(entity.id)

        entity = deepcopy(entity)
        self.__items[index] = entity

        return entity

    def delete_entity_by_id(self, correlation_id: Optional[str], entity_id: str) -> Optional[EntityV1]:
        ids = list(map(lambda x: x.id, self.__items))

        if entity_id not in ids:
            return None

        index = ids.index(entity_id)

        entity = self.__items[index]
        del self.__items[index]

        return entity
