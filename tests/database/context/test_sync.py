from contextlib import suppress
from functools import wraps
import sqlalchemy as sa

from gyver.context import Context
from gyver.context import atomic
from gyver.database.context.sync import SaAdapter, SessionAdapter
from tests.database.context.signal import Signal

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
    # sourcery skip: extract-method
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

    context = adapter.context(transaction_on=None)

    with atomic(context):
        with atomic(context) as client:
            assert client.in_transaction()
            assert client.in_nested_transaction()
        assert client.in_transaction()
        assert not client.in_nested_transaction()


def test_sqlalchemy_adapter_works_correctly_with_sa_acquire_session():
    adapter = SaAdapter(uri=sqlite_uri)
    context = adapter.session()

    with context as session:
        result = session.execute(sa.text("SELECT 1")).first()
        assert result
        (first,) = result
        assert first == 1


def test_sqlalchemy_context_and_adapter_are_compliant_to_atomic():
    adapter = SaAdapter(uri=sqlite_uri)
    context = adapter.context()

    with atomic(context) as client:
        result = client.execute(sa.text("SELECT 1")).first()
        assert result
        (first,) = result
        assert first == 1
        assert adapter.in_atomic(client)
    assert not adapter.in_atomic(client)


def test_sqlalchemy_session_and_adapter_are_compliant_to_atomic():
    adapter = SessionAdapter(SaAdapter(uri=sqlite_uri))
    context = adapter.context()

    with atomic(context) as client:
        result = client.execute(sa.text("SELECT 1")).first()
        assert result
        (first,) = result
        assert first == 1
        assert adapter.in_atomic(client)
    assert not adapter.in_atomic(client)


class MockException(Exception):
    pass


def make_rollback(func, signal: Signal):
    @wraps(func)
    def rollback(*args, **kwargs):
        signal.do()
        return func(*args, **kwargs)

    return rollback


def test_transaction_did_rollback_with_atomic():
    adapter = SaAdapter(uri=sqlite_uri)
    context = adapter.context()
    signal = Signal()
    with suppress(Exception):
        with atomic(context) as client:
            trx = client.get_transaction()
            assert trx is not None
            adapter.rollback = make_rollback(adapter.rollback, signal)
            raise MockException
    assert signal.did


def test_transaction_did_rollback_with_atomic_session():
    adapter = SessionAdapter(SaAdapter(uri=sqlite_uri))
    context = adapter.context()
    signal = Signal()
    with suppress(Exception):
        with atomic(context) as client:
            trx = client.get_transaction()
            assert trx is not None
            adapter.rollback = make_rollback(adapter.rollback, signal)
            raise MockException
    assert signal.did
