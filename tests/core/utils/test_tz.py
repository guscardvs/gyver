from gyver.utils import timezone


def test_timezone_now_returns_with_tzinfo():
    assert timezone.now().tzinfo is not None
