import sqlalchemy as sa

from gyver.database.typedef import ClauseType

from . import interface


class NullBind(interface.BindClause):
    type_ = ClauseType.BIND

    def bind(self, mapper: interface.Mapper) -> interface.Comparison:
        del mapper
        return sa.true()
