from __future__ import annotations

import html
import json
import math
import os
import subprocess
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent
REPORT_DIR = ROOT / "reports"
DEFAULT_REPORT = REPORT_DIR / "full_benchmark_report.html"


@dataclass
class BenchmarkComparison:
    path: str
    actual: object
    expected: object
    passed: bool
    difference: float | None = None
    relative_difference: float | None = None
    tolerance: float | None = None
    relative_tolerance: float | None = None
    message: str = ""


@dataclass
class BenchmarkCaseResult:
    module: str
    study: str
    benchmark_path: Path
    generator_path: Path
    comparisons: list[BenchmarkComparison] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(item.passed for item in self.comparisons)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def flatten_numbers(payload: object, prefix: str = "") -> dict[str, object]:
    if isinstance(payload, dict):
        result = {}
        for key, value in payload.items():
            child = f"{prefix}.{key}" if prefix else str(key)
            result.update(flatten_numbers(value, child))
        return result
    if isinstance(payload, list):
        result = {}
        for index, value in enumerate(payload):
            child = f"{prefix}[{index}]"
            result.update(flatten_numbers(value, child))
        return result
    return {prefix: payload}


def _is_missing_number(value) -> bool:
    return isinstance(value, float) and math.isnan(value)


def compare_payloads(
    actual: dict,
    expected: dict,
    tolerance: float = 1e-8,
    relative_tolerance: float | None = None,
) -> list[BenchmarkComparison]:
    flat_actual = flatten_numbers(actual)
    flat_expected = flatten_numbers(expected)
    paths = sorted(set(flat_actual) | set(flat_expected))
    comparisons = []
    for path in paths:
        if path not in flat_actual:
            comparisons.append(BenchmarkComparison(path, None, flat_expected[path], False, message="missing actual"))
            continue
        if path not in flat_expected:
            comparisons.append(BenchmarkComparison(path, flat_actual[path], None, False, message="missing benchmark"))
            continue

        actual_value = flat_actual[path]
        expected_value = flat_expected[path]
        if isinstance(actual_value, (int, float)) and isinstance(expected_value, (int, float)):
            if _is_missing_number(float(actual_value)) and _is_missing_number(float(expected_value)):
                passed = True
                diff = 0.0
                rel_diff = 0.0
            else:
                diff = abs(float(actual_value) - float(expected_value))
                denom = abs(float(expected_value))
                rel_diff = diff / denom if denom > 0 else (0.0 if diff == 0 else math.inf)
                passed = diff <= tolerance or (relative_tolerance is not None and rel_diff <= relative_tolerance)
            comparisons.append(
                BenchmarkComparison(
                    path,
                    actual_value,
                    expected_value,
                    passed,
                    diff,
                    rel_diff,
                    tolerance,
                    relative_tolerance,
                )
            )
        else:
            passed = actual_value == expected_value
            comparisons.append(BenchmarkComparison(path, actual_value, expected_value, passed))
    return comparisons


def _module_label(module: str) -> str:
    return module.replace("_", " ").title()


def _current_commit_hash() -> str:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=ROOT.parent.parent,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
    return completed.stdout.strip() or "unknown"


def _statprism_version() -> str:
    try:
        from src.about import version
    except ImportError:
        return "unknown"
    return str(version)


def render_report(results: Iterable[BenchmarkCaseResult], output_path: Path = DEFAULT_REPORT) -> Path:
    results = list(results)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    passed = sum(1 for result in results if result.passed)
    total = len(results)
    tested_date = date.today().isoformat()
    commit_hash = _current_commit_hash()
    statprism_version = _statprism_version()
    module_passed = {}
    for result in results:
        module_passed.setdefault(result.module, True)
        module_passed[result.module] = module_passed[result.module] and result.passed

    parts = [
        "<!doctype html><meta charset='utf-8'>",
        "<title>StatPrism Benchmark Report</title>",
        "<style>",
        "body{font-family:Arial,sans-serif;margin:24px;line-height:1.35}",
        "h2.module{display:flex;align-items:center;justify-content:space-between;gap:16px;margin-top:34px;"
        "padding:10px 12px;background:#1f2937;color:white}",
        ".module-status{padding:4px 10px;border-radius:4px;background:#f3f4f6;color:#111827;font-size:16px;"
        "letter-spacing:0;font-weight:bold}",
        ".module-status.pass{color:#0a6b22}.module-status.fail{color:#a40000}",
        "details.study{margin:12px 0 18px}",
        "details.study>summary{cursor:pointer;font-size:1.05em;font-weight:bold;margin:10px 0 4px}",
        "details.study>summary::marker{color:#555}",
        "table{border-collapse:collapse;width:auto;max-width:1100px;margin:8px 0 24px;font-size:11px}",
        "th,td{border:1px solid #ccc;padding:3px 5px;text-align:left}",
        "th{background:#f4f4f4}",
        ".pass{color:#0a6b22;font-weight:bold}.fail{color:#a40000;font-weight:bold}",
        ".meta{color:#555;font-size:12px}",
        "</style>",
        f"<h1>StatPrism Benchmark Report</h1><p><b>{passed}/{total}</b> studies passed.</p>",
        "<p class='meta'>"
        f"Tested date: {html.escape(tested_date)}<br>"
        f"StatPrism version: <code>{html.escape(statprism_version)}</code><br>"
        f"Commit hash: <code>{html.escape(commit_hash)}</code>"
        "</p>",
    ]
    current_module = None
    for result in results:
        if result.module != current_module:
            current_module = result.module
            module_status = "PASS" if module_passed[current_module] else "FAIL"
            module_cls = "pass" if module_passed[current_module] else "fail"
            parts.append(
                f"<h2 class='module'><span>{html.escape(_module_label(current_module))}</span>"
                f"<span class='module-status {module_cls}'>{module_status}</span></h2>"
            )
        status = "PASS" if result.passed else "FAIL"
        cls = "pass" if result.passed else "fail"
        benchmark_href = Path(os.path.relpath(result.benchmark_path, output_path.parent)).as_posix()
        generator_href = Path(os.path.relpath(result.generator_path, output_path.parent)).as_posix()
        benchmark_label = result.benchmark_path.as_posix()
        generator_label = result.generator_path.as_posix()
        open_attr = "" if result.passed else " open"
        parts.append(f"<details class='study'{open_attr}>")
        parts.append(f"<summary>{html.escape(result.study)} " f"<span class='{cls}'>{status}</span></summary>")
        parts.append(
            "<p class='meta'>"
            f"Benchmark: <a href='{html.escape(benchmark_href)}'>{html.escape(benchmark_label)}</a><br>"
            f"R generator: <a href='{html.escape(generator_href)}'>{html.escape(generator_label)}</a>"
            "</p>"
        )
        parts.append(
            "<table><tr><th>Number</th><th>Actual</th><th>R benchmark</th>"
            "<th>Diff</th><th>Rel diff</th><th>Status</th></tr>"
        )
        for comparison in result.comparisons:
            if comparison.path == "error" and comparison.actual == "" and comparison.expected == "":
                continue
            row_cls = "pass" if comparison.passed else "fail"
            diff = "" if comparison.difference is None else f"{comparison.difference:.3g}"
            rel_diff = "" if comparison.relative_difference is None else f"{comparison.relative_difference:.3g}"
            parts.append(
                "<tr>"
                f"<td>{html.escape(comparison.path)}</td>"
                f"<td>{html.escape(str(comparison.actual))}</td>"
                f"<td>{html.escape(str(comparison.expected))}</td>"
                f"<td>{html.escape(diff)}</td>"
                f"<td>{html.escape(rel_diff)}</td>"
                f"<td class='{row_cls}'>{'PASS' if comparison.passed else 'FAIL'}"
                f"{': ' + html.escape(comparison.message) if comparison.message else ''}</td>"
                "</tr>"
            )
        parts.append("</table>")
        parts.append("</details>")
    output_path.write_text("\n".join(parts), encoding="utf-8")
    return output_path
