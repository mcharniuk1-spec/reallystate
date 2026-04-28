"""Stage 1 scrape control plane: pattern-driven, no implicit live execution."""

from .region import ONLY_REGION_KEY
from .segments import SEGMENT_KEYS, is_allowed_segment


def run_parallel_varna_scrape(*args, **kwargs):
    """Run the one-call Varna full scrape without importing live runtimes eagerly."""
    from .varna_full_scrape import run_parallel_varna_scrape as _run_parallel_varna_scrape

    return _run_parallel_varna_scrape(*args, **kwargs)


def run_parallel_all_scrape(*args, **kwargs):
    """Run the one-call all-Bulgaria full scrape without importing live runtimes eagerly."""
    from .varna_full_scrape import run_parallel_all_scrape as _run_parallel_all_scrape

    return _run_parallel_all_scrape(*args, **kwargs)


__all__ = [
    "ONLY_REGION_KEY",
    "SEGMENT_KEYS",
    "is_allowed_segment",
    "run_parallel_varna_scrape",
    "run_parallel_all_scrape",
]
