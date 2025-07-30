# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from typing import Optional

from pip_services4_commons.data import FilterParams, PagingParams, DataPage

from ..data import EntityV1


class IBasicService(ABC):

    def get_entities(self, correlation_id: Optional[str], filter_params: FilterParams, paging: PagingParams) -> DataPage:
        raise NotImplementedError("Method is not implemented")

    def get_entity_by_id(self, correlation_id: Optional[str], entity_id: str) -> EntityV1:
        raise NotImplementedError("Method is not implemented")

    def get_entity_by_name(self, correlation_id: Optional[str], name: str) -> EntityV1:
        raise NotImplementedError("Method is not implemented")

    def create_entity(self, correlation_id: Optional[str], entity: EntityV1) -> EntityV1:
        raise NotImplementedError("Method is not implemented")

    def update_entity(self, correlation_id: Optional[str], entity: EntityV1) -> EntityV1:
        raise NotImplementedError("Method is not implemented")

    def delete_entity_by_id(self, correlation_id: Optional[str], entity_id: str) -> EntityV1:
        raise NotImplementedError("Method is not implemented")
