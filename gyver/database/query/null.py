from gyver.database.typedef import ClauseType
from . import interface
import sqlalchemy as sa


class NullBind(interface.BindClause):
    type_ = ClauseType.BIND

    def bind(self, mapper: interface.Mapper) -> interface.Comparison:
        del mapper
        return sa.true()
