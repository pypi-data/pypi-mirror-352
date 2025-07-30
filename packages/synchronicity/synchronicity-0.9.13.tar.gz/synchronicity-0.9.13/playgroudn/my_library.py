import typing
import _my_library

def foo() -> typing.Generator[int, None, None]:
    _my_library.foo.__original__