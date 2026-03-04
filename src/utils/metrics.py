import logging
import time
from contextlib import contextmanager
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

_collector: Optional[Dict[str, Any]] = None


def get_metrics_collector() -> Dict[str, Any]:
    """Get or create the metrics collector."""
    global _collector
    if _collector is None:
        _collector = {
            "operations": [],
            "totals": {}
        }
    return _collector


def reset_metrics() -> None:
    """Reset all metrics."""
    global _collector
    _collector = {
        "operations": [],
        "totals": {}
    }


@contextmanager
def timed_operation(operation_name: str, **kwargs):
    """
    Context manager to time an operation and log metrics.

    Usage:
        with timed_operation("fetch_matches", category="-18M", pool_id="123"):
            # do work
    """
    start_time = time.time()
    metadata = kwargs
    duration = 0.0
    status = "error"

    try:
        yield
        duration = time.time() - start_time
        status = "success"
    except Exception as e:
        duration = time.time() - start_time
        status = "error"
        metadata["error"] = str(e)
        raise
    finally:
        record_metric(operation_name, duration, status, **metadata)


def record_metric(operation: str, duration: float, status: str = "success", **metadata) -> None:
    """Record a metric for an operation."""
    collector = get_metrics_collector()

    entry = {
        "operation": operation,
        "duration": round(duration, 3),
        "status": status,
        **metadata
    }
    collector["operations"].append(entry)

    key = f"{operation}_total"
    if key not in collector["totals"]:
        collector["totals"][key] = {"count": 0, "duration": 0, "errors": 0}

    collector["totals"][key]["count"] += 1
    collector["totals"][key]["duration"] += duration
    if status == "error":
        collector["totals"][key]["errors"] += 1

    logger.debug(
        f"📊 [{operation}] {status} - {duration:.3f}s"
        + (f" | {metadata.get('category', '')}" if metadata.get('category') else "")
    )


def log_summary() -> None:
    """Log a summary of all recorded metrics."""
    collector = get_metrics_collector()

    if not collector["operations"]:
        logger.info("📊 No metrics recorded")
        return

    logger.info("=" * 50)
    logger.info("📊 METRICS SUMMARY")
    logger.info("=" * 50)

    for op_name, totals in collector["totals"].items():
        op = op_name.replace("_total", "")
        avg = totals["duration"] / totals["count"] if totals["count"] > 0 else 0
        logger.info(
            f"  {op}: {totals['count']} calls | "
            f"avg: {avg:.3f}s | "
            f"total: {totals['duration']:.3f}s | "
            f"errors: {totals['errors']}"
        )

    logger.info("=" * 50)
