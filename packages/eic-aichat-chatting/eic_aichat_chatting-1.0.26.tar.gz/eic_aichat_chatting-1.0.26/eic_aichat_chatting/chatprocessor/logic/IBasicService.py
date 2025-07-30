from abc import ABC, abstractmethod
from typing import Optional
from pip_services4_components.context import IContext
from ..data import RequestV1, ResponseV1

class IBasicService(ABC):
    """
    Defines the service business logic interface.
    """

    @abstractmethod
    def handle_model_request(context: Optional[IContext], request: RequestV1) -> ResponseV1:
        """
        Some API function of module.

        :param context: The context.
        :param request: A request object.
        :return: A response object.
        """
        pass