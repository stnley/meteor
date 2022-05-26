from meteor.mediator import IRequestHandler


async def test_abstract_handler() -> None:
    class Ping(str):
        ...

    class Pong(str):
        ...

    class PingHandler(IRequestHandler[Ping, Pong]):
        async def handle(self, request: Ping) -> Pong:
            return Pong(request + " Pong")

    handler = PingHandler()

    response = await handler.handle(Ping("Ping"))

    assert isinstance(response, Pong)
    assert response == "Ping Pong"


async def test_abstract_handler_returning_none() -> None:
    class Ping(str):
        ...

    class PingHandler(IRequestHandler[Ping, None]):
        async def handle(self, request: Ping) -> None:
            ...

    handler = PingHandler()

    response = await handler.handle(Ping("Ping"))

    assert response is None
