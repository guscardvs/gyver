from gyver.model import Model
from gyver.utils import to_camel


class BotoModel(Model):
    class Config:
        @staticmethod
        def alias_generator(field: str):
            return field[:1].upper() + to_camel(field[1:])
