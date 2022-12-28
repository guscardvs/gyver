from gyver.utils import make_singleton


@make_singleton
class Singleton:
    counter = 1

    def __init__(self) -> None:
        type(self).counter += 1


def test_make_singleton_decorated_returns_always_same_class():
    instance = Singleton()
    second = Singleton()

    assert instance is second
    assert instance.counter == Singleton.counter == 2
