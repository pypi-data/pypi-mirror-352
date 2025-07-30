from collections import defaultdict
from datetime import datetime
from typing import Any

import numpy as np
from drain3 import TemplateMiner
from drain3.template_miner_config import TemplateMinerConfig
from pydantic import AwareDatetime, BaseModel
from sparklines import sparklines

from daydream.utils import print

LogLine = tuple[AwareDatetime, str]


class LogAnomaly(BaseModel):
    pattern: str
    peak_increase: float
    peak_time: AwareDatetime
    examples: list[str]
    frequencies: list[tuple[AwareDatetime, float]]
    counts: list[tuple[AwareDatetime, int]]
    counts_sparkline: str


HTTP_LOG_PATTERNS = [
    "HTTP/1.1",
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
    "HEAD",
]


def segment_logs_by_time(
    log_entries: list[tuple[datetime, str]], window_minutes: int = 5
) -> dict[datetime, list[str]]:
    time_windows = defaultdict(list)

    for dt, log_content in log_entries:
        window_key = dt.replace(
            minute=dt.minute - dt.minute % window_minutes, second=0, microsecond=0
        )
        time_windows[window_key].append(log_content)

    return time_windows


def analyze_pattern_trends(
    time_windows: dict[datetime, list[str]], template_miner: TemplateMiner
) -> tuple[dict[str, list[tuple[datetime, float]]], dict[str, list[tuple[datetime, int]]]]:
    """Track pattern frequencies across time windows

    Args:
        time_windows: Dictionary mapping window times to lists of log lines
        template_miner: Pre-trained drain3 TemplateMiner

    Returns:
        pattern_trends: Dictionary mapping patterns to lists of (time, frequency (%)) tuples
        pattern_counts: Dictionary mapping patterns to lists of (time, counts) tuples
    """
    # Get all templates from the pre-processed template miner
    templates_info = {}

    # Extract all templates (cluster info) from the template miner
    for cluster in template_miner.drain.clusters:
        cluster_id = cluster.cluster_id
        template = cluster.get_template()
        templates_info[cluster_id] = {
            "template": template,
            "cluster_id": cluster_id,
            "size": cluster.size,
        }

    # Track template frequencies across time windows
    pattern_trends = defaultdict(list)
    pattern_counts = defaultdict(list)
    all_templates = [info["template"] for info in templates_info.values()]

    # Calculate frequencies for each pattern across time windows
    for window_time, logs in sorted(time_windows.items()):
        if not logs:
            continue

        # Count occurrences of each template in this window
        template_counts = defaultdict(int)

        for log in logs:
            result = template_miner.match(log)
            if result is not None:
                template = result.get_template()
                template_counts[template] += 1

        # Calculate frequencies
        total_logs = len(logs)
        for template in all_templates:
            count = template_counts.get(template, 0)
            frequency = count / total_logs if total_logs > 0 else 0
            pattern_trends[template].append((window_time, frequency))
            pattern_counts[template].append((window_time, count))

    return pattern_trends, pattern_counts


def detect_significant_patterns(
    pattern_trends: dict[str, list[tuple[datetime, float]]],
    threshold: float = 0.2,
    min_occurrences: int = 3,
    focus_on_increases: bool = True,
) -> dict[str, dict[str, Any]]:
    """Identify patterns with significant frequency changes, focusing on increases

    Args:
        pattern_trends: Dictionary mapping patterns to lists of (time, frequency) tuples
        threshold: Minimum relative change to consider significant
        min_occurrences: Minimum number of occurrences required
        focus_on_increases: If True, only detect patterns that increase at some point

    Returns:
        Dictionary of significant patterns with their info
    """
    significant_patterns = {}

    for pattern, frequencies in pattern_trends.items():
        if len(frequencies) < min_occurrences:
            continue

        times, freqs = zip(*frequencies, strict=True)
        freqs = np.array(freqs)

        if np.max(freqs) == 0:
            continue

        # Calculate increase/decrease
        try:
            max_freq = np.max(freqs)
            max_idx = np.argmax(freqs)

            nonzero_indices = np.where(freqs > 0)[0]
            if len(nonzero_indices) == 0:
                continue

            start_idx = nonzero_indices[0]
            start_freq = freqs[start_idx]

            # Calculate increase to max (to detect patterns that increase then decrease)
            max_increase = (max_freq - start_freq) / start_freq if start_freq > 0 else float("inf")

            # Calculate end-to-end change (for full trend direction)
            end_change = (freqs[-1] - start_freq) / start_freq if start_freq > 0 else float("inf")

            increases_at_some_point = max_increase > threshold

            if increases_at_some_point or not focus_on_increases:
                significant_patterns[pattern] = {
                    "peak_increase": float(max_increase),
                    "end_to_end_change": float(end_change),
                    "peak_time": times[max_idx].isoformat()
                    if isinstance(times[max_idx], datetime)
                    else times[max_idx],
                    "frequencies": [
                        (
                            t.isoformat() if isinstance(t, datetime) else t,
                            float(f),
                        )
                        for t, f in frequencies
                    ],
                }
        except Exception as e:
            print(f"Error analyzing pattern: {pattern[:50]}... - {e}")

    return significant_patterns


def find_pattern_examples(
    log_entries: list[tuple[datetime, str]],
    pattern: str,
    template_miner: TemplateMiner,
    max_examples: int = 3,
) -> list[str]:
    examples = []
    log_contents = [content for _, content in log_entries]

    for log in log_contents:
        result = template_miner.match(log)
        if result is not None and result.get_template() == pattern:
            examples.append(log)
            if len(examples) >= max_examples:
                break

    return examples


def detect_log_anomalies(
    log_entries: list[tuple[datetime, str]],
    window_minutes: int = 5,
    threshold: float = 0.2,
    min_occurrences: int = 3,
) -> list[LogAnomaly]:
    if len(log_entries) == 0:
        return []

    config = TemplateMinerConfig()
    config.drain_sim_th = 0.5
    config.drain_depth = 4
    config.masking_instructions = []
    template_miner = TemplateMiner(config=config)

    # Pre-process all logs to train the template miner
    # Ignore HTTP logs for now - too noisy
    all_logs = [content for _, content in log_entries if not is_http_log(content)]
    for log in all_logs:
        template_miner.add_log_message(log)

    time_windows = segment_logs_by_time(log_entries, window_minutes=window_minutes)
    pattern_trends, pattern_counts = analyze_pattern_trends(time_windows, template_miner)

    significant_patterns = detect_significant_patterns(
        pattern_trends,
        threshold=threshold,
        min_occurrences=min_occurrences,
        focus_on_increases=True,
    )

    results = []
    for pattern, info in significant_patterns.items():
        examples = find_pattern_examples(log_entries, pattern, template_miner)

        results.append(
            LogAnomaly(
                pattern=pattern,
                peak_increase=info["peak_increase"],
                peak_time=info["peak_time"],
                examples=examples,
                frequencies=info["frequencies"],
                counts=pattern_counts[pattern],
                counts_sparkline="".join(
                    sparklines(np.array([f for _, f in pattern_counts[pattern]]))
                ),
            )
        )

    results.sort(key=lambda x: x.peak_increase, reverse=True)
    return results[:10]


def is_http_log(log: str) -> bool:
    return any(pattern in log for pattern in HTTP_LOG_PATTERNS)
