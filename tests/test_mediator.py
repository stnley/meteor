from typing import Any

import pytest
from _pytest.capture import CaptureFixture

from meteor.exceptions import UnknownRequestType
from meteor.mediator import IRequest, IRequestHandler, Mediator


async def test_unknown_request_raises() -> None:
    class Pong(str):
        ...

    class Ping(str, IRequest[Pong]):
        ...

    mediator = Mediator()

    with pytest.raises(UnknownRequestType):
        _ = await mediator.send(Ping("Ping"))


async def test_send_returns_expected_response() -> None:
    class Pong(str):
        ...

    class Ping(str, IRequest[Pong]):
        ...

    class PingHandler(IRequestHandler[Ping, Pong]):
        async def handle(self, request: Ping) -> Pong:
            return Pong(request + " Pong")

    mediator = Mediator()

    await mediator.register(Ping, PingHandler)

    response = await mediator.send(Ping("Ping"))

    assert isinstance(response, Pong)
    assert response == "Ping Pong"


async def test_publish_unknown_request_warns() -> None:
    class Zing(str, IRequest[None]):
        ...

    mediator = Mediator()

    with pytest.warns(UserWarning, match="No handler defined for request type 'Zing'"):
        _ = await mediator.publish(Zing("Zing"))


async def test_publish_returns_none() -> None:
    class Zing(str, IRequest[None]):
        ...

    class ZingHandler(IRequestHandler[Zing, None]):
        async def handle(self, request: Zing) -> None:
            ...

    mediator = Mediator()

    await mediator.register(Zing, ZingHandler)

    response = await mediator.publish(Zing("Zing"))

    assert response is None


async def test_publish_returns_none_even_if_handler_returns() -> None:
    class Zap(str):
        ...

    class Zing(str, IRequest[Zap]):
        ...

    class ZingHandler(IRequestHandler[Zing, None]):
        async def handle(self, request: Zing) -> Any:
            return Zap(request + " Zap")

    mediator = Mediator()

    await mediator.register(Zing, ZingHandler)
    response = await mediator.publish(Zing("Zing"))

    assert response is None


async def test_publish_succeeds_to_other_handlers_when_one_handler_raises(
    capsys: CaptureFixture[str],
) -> None:
    class Zing(str, IRequest[None]):
        ...

    class ZingHandler(IRequestHandler[Zing, None]):
        async def handle(self, request: Zing) -> Any:
            print("handling zing")

    class BadZingHandler(IRequestHandler[Zing, None]):
        async def handle(self, request: Zing) -> Any:
            raise RuntimeError("raised inside handler")

    mediator = Mediator()

    await mediator.register(Zing, BadZingHandler)
    await mediator.register(Zing, ZingHandler)

    with pytest.raises(RuntimeError, match="raised inside handler"):
        await mediator.publish(Zing("Zing"))

    captured = capsys.readouterr()
    assert captured.out == "handling zing\n"
