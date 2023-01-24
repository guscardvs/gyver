import sqlalchemy as sa

from gyver.context import Context
from gyver.database.context.sync import SaAdapter

sqlite_uri = "sqlite:///:memory:"


def test_sqlalchemy_adapter_works_correctly_with_default_context():
    adapter = SaAdapter(uri=sqlite_uri)
    context = Context(adapter)

    with context.begin() as conn:
        result = conn.execute("SELECT 1").first()
        assert result
        (first,) = result
        assert first == 1


def test_sqlalchemy_adapter_works_correctly_with_sa_context():
    adapter = SaAdapter(uri=sqlite_uri)

    context = adapter.context()

    with context.begin() as conn:
        result = conn.execute("SELECT 1").first()
        assert result
        (first,) = result
        assert first == 1


def test_sqlalchemy_adapter_works_correctly_with_sa_context_transaction():
    adapter = SaAdapter(uri=sqlite_uri)
    context = adapter.context(transaction_on="begin")
    with context.open():
        with context.begin() as conn:
            result = conn.execute("SELECT 1").first()
            assert result
            assert conn.in_transaction()
            assert not conn.in_nested_transaction()
            (first,) = result
            assert first == 1

    context = adapter.context(transaction_on="open")

    with context.open():
        with context.begin():
            assert context.client.in_transaction()
            assert not context.client.in_nested_transaction()


def test_sqlalchemy_adapter_works_correctly_with_sa_acquire_session():
    adapter = SaAdapter(uri=sqlite_uri)
    context = adapter.context()

    with context.acquire_session() as session:
        result = session.execute(sa.text("SELECT 1")).first()
        assert result
        (first,) = result
        assert first == 1
