"""Fuzzy matching utilities."""

from typing import Callable, Iterable, TypeVar
from rapidfuzz import fuzz

T = TypeVar("T")

DEFAULT_FUZZY_THRESHOLD = 80


def fuzzy_score(
    query: str, *fields: str, threshold: int = DEFAULT_FUZZY_THRESHOLD
) -> float | None:
    """Score a query against one or more fields.

    A literal case-insensitive substring match in any field always scores 100.
    Otherwise, falls back to fuzzy scoring per field. Only counted as a match if
    the best score clears `threshold`,

    Returns:
        The match score, or None if nothing cleared the bar.
    """
    query_lower = query.lower()
    if any(query_lower in field.lower() for field in fields):
        return 100.0

    best = max((fuzz.WRatio(query, field) for field in fields), default=0.0)
    return best if best >= threshold else None


def fuzzy_filter(
    query: str,
    items: Iterable[T],
    key: Callable[[T], tuple[str, ...]],
    threshold: int = DEFAULT_FUZZY_THRESHOLD,
) -> list[tuple[float, T]]:
    """Score and filter items against a query, best match first.

    Args:
        query: Search string.
        items: Items to score.
        key: Maps an item to the fields to match against (e.g. title/artist/album).
        threshold: Minimum fuzzy score required when there's no substring match.

    Returns:
        (score, item) pairs that matched, sorted best-first.
    """
    scored = []
    for item in items:
        score = fuzzy_score(query, *key(item), threshold=threshold)
        if score is not None:
            scored.append((score, item))
    scored.sort(key=lambda pair: -pair[0])
    return scored
