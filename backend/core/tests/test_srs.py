from __future__ import annotations

from datetime import date

import pytest

from core.srs import ReviewResult, sm2


def test_quality_0_failure_resets() -> None:
    base = date(2026, 1, 1)
    result = sm2(easiness_factor=2.5, interval=10, repetitions=5, quality=0, today=base)
    assert isinstance(result, ReviewResult)
    assert result.repetitions == 0
    assert result.interval_days == 1
    assert result.next_review_date == date(2026, 1, 2)


def test_quality_3_barely_passes_progresses() -> None:
    base = date(2026, 1, 1)
    # First successful review => interval 1, repetitions 1
    result = sm2(easiness_factor=2.5, interval=0, repetitions=0, quality=3, today=base)
    assert result.repetitions == 1
    assert result.interval_days == 1
    assert result.next_review_date == date(2026, 1, 2)
    # EF should decrease but not below minimum
    assert result.easiness_factor >= 1.3
    assert result.easiness_factor < 2.5


def test_quality_5_perfect_increases_ef() -> None:
    base = date(2026, 1, 1)
    result = sm2(easiness_factor=2.5, interval=0, repetitions=0, quality=5, today=base)
    assert result.repetitions == 1
    assert result.interval_days == 1
    assert result.easiness_factor > 2.5


def test_multiple_consecutive_reviews_follow_1_6_then_ef_times_previous() -> None:
    base = date(2026, 1, 1)
    # Review 1 (rep 0 -> 1): interval 1
    r1 = sm2(easiness_factor=2.5, interval=0, repetitions=0, quality=5, today=base)
    assert r1.interval_days == 1
    assert r1.repetitions == 1

    # Review 2 (rep 1 -> 2): interval 6
    r2 = sm2(
        easiness_factor=r1.easiness_factor,
        interval=r1.interval_days,
        repetitions=r1.repetitions,
        quality=5,
        today=base,
    )
    assert r2.interval_days == 6
    assert r2.repetitions == 2

    # Review 3 (rep 2 -> 3): interval round(prev_interval * EF)
    r3 = sm2(
        easiness_factor=r2.easiness_factor,
        interval=r2.interval_days,
        repetitions=r2.repetitions,
        quality=5,
        today=base,
    )
    expected = int(round(6 * r2.easiness_factor))
    assert r3.interval_days == expected
    assert r3.repetitions == 3


@pytest.mark.parametrize("q", [-1, 6])
def test_invalid_quality_raises(q: int) -> None:
    with pytest.raises(ValueError):
        sm2(easiness_factor=2.5, interval=1, repetitions=1, quality=q)

