import abc
import warnings
from typing import Any, Dict, Generic, Protocol, Set, Type, TypeVar, cast

from meteor.exceptions import UnknownRequestType

TRequest = TypeVar("TRequest")
TResponse = TypeVar("TResponse")


class IRequest(Generic[TResponse]):
    """Base request class.

    Should be subclassed by any type of message you want to send. If you want your
    request to have a specific response, use the generic parameter and specify what type
    the response is. You can also use Any if you don't care about the response type. If
    you don't need a respose you can use None.
    """

    ...


class _Handler(Protocol):
    async def handle(self, request: Any) -> Any:
        ...


class IRequestHandler(abc.ABC, Generic[TRequest, TResponse]):
    """Abstract class which receives and handles requests."""

    @abc.abstractmethod
    async def handle(self, request: TRequest) -> TResponse:
        ...


class Mediator:
    def __init__(self) -> None:
        self._handlers: Dict[Type[Any], Set[Type[_Handler]]] = {}

    async def register(
        self,
        request_type: Type[TRequest],
        request_handler: Type[IRequestHandler[TRequest, Any]],
    ) -> None:
        """Register a handler with the mediator.

        Associates a request type with a handler type. NB: this expects types, not
        instances of handlers.

        Args:
            request_type: Any type.
            request_handler: A type (or subclass) of IRequestHandler. Notice the
                request_type does not need to be a type of IRequest or subclass.
                The IRequestHandler interface will report an error if attempting to
                register a type that it does not handle. This type-checking is *not*
                during runtime however.
        """
        try:
            self._handlers[request_type].add(request_handler)
        except KeyError:
            self._handlers[request_type] = set([request_handler])

    async def send(self, request: IRequest[TResponse]) -> TResponse:
        """Asyncronously send a request to a single handler.

        Sends a request to the first handler matching the request type and returns the
        response. If multiple handlers are registered for the request type, only one
        will handle the request.

        Args:
            request: an instance of a IRequest (or subclass).


        Returns:
            A response of type TResponse in IRequest[TResponse] from the request
            argument.

        Raises:
            UnknownRequestType: There was no handler registered for the type of request.
        """
        request_type = type(request)
        try:
            # feels bad man
            return cast(
                TResponse,
                await next(iter(self._handlers[request_type]))().handle(request),
            )
        except KeyError as exc:
            raise UnknownRequestType(request, request_type.__name__) from exc

    async def publish(self, request: IRequest[None]) -> None:
        """Asyncronously send a request to multiple handlers.

        Sends a request to all handlers matching the request type. If no handlers match
        the request type, a warning is issued.

        Args:
            request: an instance of a IRequest[None] (or subclass).
        """
        request_type = type(request)
        try:
            handlers = self._handlers[request_type]
            for handler in handlers:
                await handler().handle(request)
        except KeyError:
            warnings.warn(
                "No handler defined for request type '{}'".format(request_type.__name__)
            )
