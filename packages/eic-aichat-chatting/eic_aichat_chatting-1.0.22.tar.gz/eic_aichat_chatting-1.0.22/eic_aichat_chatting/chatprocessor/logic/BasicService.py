from typing import Optional

from pip_services4_components.config import ConfigParams, IConfigurable
from pip_services4_components.context import IContext
from pip_services4_components.refer import IReferences, IReferenceable, Descriptor
from pip_services4_observability.log import CompositeLogger
from pip_services4_observability.count import CompositeCounters
from pip_services4_config.connect import ConnectionParams

from ..data import RequestV1, ResponseV1
from ..logic import IBasicService

from eic_aichat_models.basemodels.logic.BaseModelsService import BaseModelsService
from eic_aichat_connect.services.ModelConnectionService import ModelConnectionService
from eic_aichat_connect.data.version1.ModelRequestV1 import ModelRequestV1


class BasicService(IBasicService, IConfigurable, IReferenceable):
    """
    Implements the business logic operations of the controller.
    """

    def __init__(self):
        self._logger = CompositeLogger()
        self._counters = CompositeCounters()
        self._default_response = ''
        self._base_models_service: BaseModelsService = None
        self._conn_service: ModelConnectionService = None

        self.api_key = ''

    def configure(self, config: ConfigParams):
        """
        Configures component by passing configuration parameters.

        :param config: Configuration parameters to be set.
        """
        self._logger.configure(config)
        self._default_response = config.get_as_string_with_default('configuration.response', self._default_response)
        self.api_key = config.get_as_string('api_key')

    def set_references(self, references: IReferences):
        """
        Sets references to dependent components.

        :param references: References to locate the component dependencies.
        """
        self._logger.set_references(references)
        self._counters.set_references(references)

        self._base_models_service = references.get_one_required(Descriptor('aichatmodels-basemodels', 'service', '*', '*', '1.0'))
        if self._base_models_service is not None:
            self._base_models_service.set_references(references)

        self._conn_service = references.get_one_required(Descriptor('aichatconnect', 'service', '*', '*', '1.0'))
        if self._conn_service is not None:
            self._conn_service.set_references(references)

    def handle_model_request(self, context: Optional[IContext], request: RequestV1) -> ResponseV1:
        """
        Handles a model API request and returns the result in a ResponseV1 object.

        :param context: The operational context (can be None).
        :param request: The request object containing prompt and model details.
        :return: The response object containing the result.
        :raises ValueError: If the request is None.
        :raises Exception: If any error occurs during processing.
        """
        try:
            if request is None:
                raise ValueError("Request cannot be None")

            # Retrieve the model configuration by ID
            model = self._base_models_service.get_model_by_id(context, request.model_id)

            # Assemble connection parameters
            conn_params = ConnectionParams.from_tuples(
                "user", request.user_id,
                "api", model.api,
                "base_url", model.base_url,
                "api_key", self.api_key,
            )

            # Construct and send model request
            req = ModelRequestV1(request.prompt, request.model_name)
            resp = self._conn_service.execute_request(conn_params, req)

            self._logger.info(context, f"Processed request: {resp}")
            self._counters.increment_one('basic.handle_model_request')

            return resp

        except Exception as e:
            self._logger.error(context, e, "Failed to handle model request")
            raise