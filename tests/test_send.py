from meteor.mediator import IRequest, IRequestHandler, Mediator


async def test_abstract_handler() -> None:
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
