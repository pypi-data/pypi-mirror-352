import typing
from synchronicity import Synchronizer


synchronizer = Synchronizer()


async def foo() -> typing.AsyncGenerator[int, None]:
    yield 1


foo = synchronizer.wrap(foo, target_module="my_library")