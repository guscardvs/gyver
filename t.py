from gyver.config import as_config
from gyver.config.adapter.helpers import attribute


@as_config
class Recipient:
    name: str
    surname: str = ""

    @property
    def fullname(self):
        return " ".join(filter(bool, (self.name, self.surname)))


class Test:
    @attribute.lazy
    def say_hello(self, recipient: Recipient) -> str:
        print("Running Test.say_hello")
        return f"Hello, {recipient.fullname}"


test = Test()
print(test.say_hello)
print(test.say_hello)
print(test.say_hello)
print(test.say_hello)
