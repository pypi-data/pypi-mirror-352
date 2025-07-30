import typing


class Request(typing.NamedTuple):
    """
    JSON-RPC Request.
    """

    method: str
    params: dict | list


class ResponseError(typing.TypedDict):
    """
    JSON-RPC Error Response.
    """

    code: int
    message: str
    data: typing.Any | None


class Response(typing.NamedTuple):
    """
    JSON-RPC Response.
    """

    request: Request
    result: typing.Any | None
    error: ResponseError | None = None


class Subscription:
    def __init__(self, subscription_id, queue):
        self.id = subscription_id
        self.queue = queue

    def __aiter__(self):
        return self

    async def __anext__(self):
        item = await self.queue.get()
        self.queue.task_done()
        return item
