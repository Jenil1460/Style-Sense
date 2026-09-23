"""
PerfTimer — High-resolution timing utility for StyleSense AI performance tracking.
"""

import time
import logging
from typing import Dict, Any

logger = logging.getLogger("app.perf")


class PerfTimer:
    def __init__(self):
        self.timings: Dict[str, float] = {}
        self._start_times: Dict[str, float] = {}
        self._global_start = time.perf_counter()

    def start(self, stage: str):
        self._start_times[stage] = time.perf_counter()

    def stop(self, stage: str) -> float:
        if stage in self._start_times:
            elapsed = time.perf_counter() - self._start_times.pop(stage)
            self.timings[stage] = round(elapsed, 4)
            return self.timings[stage]
        return 0.0

    class _StageContext:
        def __init__(self, timer: "PerfTimer", stage: str):
            self.timer = timer
            self.stage = stage

        def __enter__(self):
            self.timer.start(self.stage)
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.timer.stop(self.stage)

    def stage(self, stage_name: str):
        return self._StageContext(self, stage_name)

    def total(self) -> float:
        return round(time.perf_counter() - self._global_start, 4)

    def get_summary(self) -> Dict[str, Any]:
        summary = dict(self.timings)
        summary["total"] = self.total()
        return summary

    def log_summary(self, prefix: str = "[PERF]"):
        lines = [f"{prefix} Timing breakdown:"]
        for stage, duration in self.timings.items():
            lines.append(f"  • {stage}: {duration:.3f}s")
        lines.append(f"  ════ TOTAL: {self.total():.3f}s ════")
        logger.info("\n".join(lines))
