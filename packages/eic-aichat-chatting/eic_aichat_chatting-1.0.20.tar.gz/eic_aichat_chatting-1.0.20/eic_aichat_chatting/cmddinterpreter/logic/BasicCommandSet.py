# -*- coding: utf-8 -*-
from typing import Optional

from pip_services4_commons.commands import CommandSet, ICommand, Command
from pip_services4_commons.convert import TypeCode
from pip_services4_commons.data import FilterParams, PagingParams
from pip_services4_commons.run import Parameters
from pip_services4_commons.validate import ObjectSchema, FilterParamsSchema, PagingParamsSchema

from ..data import EntityV1
from ..data import EntityV1Schema
from .IBasicService import IBasicService


class BasicCommandSet(CommandSet):

    def __init__(self, service: IBasicService):
        super().__init__()

        self.__service = service

        self.add_command(self.__make_get_entities_command())
        self.add_command(self.__make_get_entity_by_id_command())
        self.add_command(self.__make_get_entity_by_name_command())
        self.add_command(self.__make_create_entity_command())
        self.add_command(self.__make_update_entity_command())
        self.add_command(self.__make_delete_entity_by_id_command())

    def __make_get_entities_command(self) -> ICommand:
        def action(correlation_id: Optional[str], args: Parameters):
            filter = FilterParams.from_value(args.get('filter'))
            paging = PagingParams.from_value(args.get('paging'))
            return self.__service.get_entities(correlation_id, filter, paging)

        return Command(
            'get_entities',
            ObjectSchema(True)
                .with_optional_property('filter', FilterParamsSchema())
                .with_optional_property('paging', PagingParamsSchema()),
            action
        )

    def __make_get_entity_by_id_command(self) -> ICommand:
        def action(correlation_id: Optional[str], args: Parameters):
            entity_id = args.get_as_string('entity_id')
            return self.__service.get_entity_by_id(correlation_id, entity_id)

        return Command(
            'get_entity_by_id',
            ObjectSchema(True).with_optional_property('entity_id', TypeCode.String),
            action
        )

    def __make_get_entity_by_name_command(self) -> ICommand:
        def action(correlation_id: Optional[str], args: Parameters):
            name = args.get_as_string('name')
            return self.__service.get_entity_by_name(correlation_id, name)

        return Command(
            'get_entity_by_name',
            ObjectSchema(True).with_optional_property('name', TypeCode.String),
            action
        )

    def __make_create_entity_command(self) -> ICommand:
        def action(correlation_id: Optional[str], args: Parameters):
            entity = args.get_as_object('entity')
            if isinstance(entity, dict):
                entity = EntityV1(**entity)
            return self.__service.create_entity(correlation_id, entity)

        return Command(
            'create_entity',
            ObjectSchema(True).with_required_property('entity', EntityV1Schema()),
            action
        )

    def __make_update_entity_command(self) -> ICommand:
        def action(correlation_id: Optional[str], args: Parameters):
            entity = args.get_as_object('entity')
            if isinstance(entity, dict):
                entity = EntityV1(**entity)
            return self.__service.update_entity(correlation_id, entity)

        return Command(
            'update_entity',
            ObjectSchema(True).with_required_property('entity', EntityV1Schema()),
            action
        )

    def __make_delete_entity_by_id_command(self) -> ICommand:
        def action(correlation_id: Optional[str], args: Parameters):
            entity_id = args.get_as_string('entity_id')
            return self.__service.delete_entity_by_id(correlation_id, entity_id)

        return Command(
            'delete_entity_by_id',
            ObjectSchema(True).with_required_property('entity_id', TypeCode.String),
            action
        )
