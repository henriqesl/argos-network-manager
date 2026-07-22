"""Tests for polling result summaries."""

from datetime import datetime, timezone

from app.services.polling import (
    RouterPollingResult,
    build_polling_summary,
)


def make_result(
    *,
    router_id: int,
    status: str,
) -> RouterPollingResult:
    checked_at = datetime.now(timezone.utc)

    return RouterPollingResult(
        router_id=router_id,
        status=status,
        checked_at=checked_at,
        finished_at=checked_at,
        duration_ms=100,
    )


def test_builds_polling_summary() -> None:
    results = [
        make_result(router_id=1, status="online"),
        make_result(router_id=2, status="online"),
        make_result(router_id=3, status="offline"),
        make_result(router_id=4, status="error"),
    ]

    summary = build_polling_summary(results)

    assert summary.total == 4
    assert summary.online == 2
    assert summary.offline == 1
    assert summary.errors == 1