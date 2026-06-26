#  Copyright (c) 2023 StatPrism Team. All rights reserved.
"""Snapshot review tool for StatPrism's HTML golden tests.

Two purposes, in one window:

  1. Review: run the suite and look at the rendered output for every case, so a
     developer can visually confirm what each test produces.
  2. Approve: when a case differs from its benchmark, the benchmark (left) and the
     new output (right) are shown side by side, and the developer records a verdict:

        * Approve as correct   -> output becomes the benchmark, verified correct
        * Approve as unchanged -> output becomes/stays the benchmark, not verified
                                  (default comment "No changes found")
        * Disapprove           -> output is wrong; it stays flagged

"Approve as correct" and "Disapprove" each require a confirmation dialog carrying
a comment (like a commit message), so they are hard to trigger by accident.
"Approve as unchanged" is the fast path: it skips the popup, records the inline
comment (or the default), and advances to the next case for quick sequential
review. Every verdict is appended to a per-test history.

Files live in ``tests/snapshots``:

  * ``<name>.approved.html`` -- the blessed benchmark
  * ``<name>.received.html`` -- last output that differed / awaits a verdict
  * ``<name>.history.json``  -- list of {time, action, comment} verdicts

Last status, derived from files + history:

  * NEW        -> no benchmark yet (and not disapproved).
  * FAILED     -> a differing output is pending, or the latest verdict is Disapprove.
  * CONSISTENT -> passing; only ever "approved as unchanged".
  * CORRECT    -> ever "approved as correct".

Run it with the project's interpreter:

    python tools/snapshot_review.py
"""

from __future__ import annotations

import base64
import html
import json
import re
import sys
from datetime import datetime
from pathlib import Path

from PySide6 import QtCore, QtGui, QtWidgets

REPO_ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT_DIR = REPO_ROOT / "tests" / "snapshots"

STATUS_NEW = "NEW"
STATUS_FAILED = "FAILED"
STATUS_CONSISTENT = "CONSISTENT"
STATUS_CORRECT = "CORRECT"

STATUS_COLOR = {
    STATUS_NEW: "#f9a825",         # amber
    STATUS_FAILED: "#c62828",      # red
    STATUS_CONSISTENT: "#1565c0",  # blue
    STATUS_CORRECT: "#2e7d32",     # green
}

# Statuses that still need the developer's attention.
NEEDS_REVIEW = {STATUS_NEW, STATUS_FAILED}

# Verdict actions.
ACT_CORRECT = "approved_correct"
ACT_UNCHANGED = "approved_unchanged"
ACT_DISAPPROVED = "disapproved"

ACTION_LABEL = {
    ACT_CORRECT: "Approved (correct)",
    ACT_UNCHANGED: "Approved (unchanged)",
    ACT_DISAPPROVED: "Disapproved",
}
ACTION_COLOR = {
    ACT_CORRECT: "#2e7d32",
    ACT_UNCHANGED: "#1565c0",
    ACT_DISAPPROVED: "#c62828",
}
# Dialog titles per action.
ACTION_TITLE = {
    ACT_CORRECT: "Approve as correct",
    ACT_UNCHANGED: "Approve as unchanged",
    ACT_DISAPPROVED: "Disapprove",
}

DEFAULT_UNCHANGED_COMMENT = "No changes found"


class HtmlView(QtWidgets.QTextBrowser):
    """QTextBrowser that renders inline ``data:image/...;base64,`` plots and keeps
    them sized to the pane.

    QTextBrowser's own zoom only scales text, and images otherwise render at their
    native pixel size (StatPrism's plots are ~1.5x their display size, so they come
    out huge). So before display we rewrite every ``<img>`` tag with an explicit
    width/height: fit to the pane width (never upscaling past native), times a user
    zoom factor, aspect ratio preserved. Ctrl+wheel changes the zoom; resizing the
    pane refits.
    """

    _IMG_RE = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
    _SRC_RE = re.compile(r'src\s*=\s*"([^"]+)"', re.IGNORECASE)
    _WH_RE = re.compile(r'\s+(?:width|height)\s*=\s*"[^"]*"', re.IGNORECASE)
    # Inline absolute font sizes (e.g. "font-size: 12pt"). Relative units (em/%) are
    # left alone -- they already follow the scaled base font, so scaling them too
    # would double-apply.
    _FONTSIZE_RE = re.compile(r"(font-size\s*:\s*)([\d.]+)\s*(pt|px)", re.IGNORECASE)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._raw_html = ""
        self._zoom = 1.0
        self._base_point = self.font().pointSizeF()
        if self._base_point <= 0:
            self._base_point = 12.0
        self._size_cache = {}  # src -> (natural_w, natural_h)
        self._refit_timer = QtCore.QTimer(self)
        self._refit_timer.setSingleShot(True)
        self._refit_timer.setInterval(120)
        self._refit_timer.timeout.connect(self._render)

    def loadResource(self, type_, url: QtCore.QUrl):
        text = url.toString()
        if text.startswith("data:image"):
            try:
                _, b64 = text.split(",", 1)
                image = QtGui.QImage()
                image.loadFromData(base64.b64decode(b64))
                return image
            except Exception:
                return QtGui.QImage()
        return super().loadResource(type_, url)

    def setHtml(self, html_text):
        self._raw_html = html_text or ""
        self._render()

    def _natural_size(self, src: str):
        if src in self._size_cache:
            return self._size_cache[src]
        size = None
        if src.startswith("data:image"):
            try:
                image = QtGui.QImage()
                image.loadFromData(base64.b64decode(src.split(",", 1)[1]))
                if not image.isNull():
                    size = (image.width(), image.height())
            except Exception:
                size = None
        self._size_cache[src] = size
        return size

    def _render(self):
        avail = max(100, self.viewport().width() - 24)

        def repl(match):
            tag = self._WH_RE.sub("", match.group(0))
            inner = tag[1:-1].rstrip()
            if inner.endswith("/"):
                inner = inner[:-1].rstrip()
            src_match = self._SRC_RE.search(tag)
            size = self._natural_size(src_match.group(1)) if src_match else None
            if size:
                nat_w, nat_h = size
                disp_w = min(nat_w, avail) * self._zoom
                scale = disp_w / nat_w if nat_w else 1.0
                return f'<{inner} width="{max(1, int(disp_w))}" height="{max(1, int(nat_h * scale))}">'
            return f'<{inner} width="{max(1, int(avail * self._zoom))}">'

        processed = self._IMG_RE.sub(repl, self._raw_html)
        processed = self._scale_fonts(processed)

        # Scale the base font too, for any text without an explicit size.
        base_font = self.font()
        base_font.setPointSizeF(self._base_point * self._zoom)
        self.setFont(base_font)

        position = self.verticalScrollBar().value()
        super().setHtml(processed)
        self.verticalScrollBar().setValue(position)

    def _scale_fonts(self, text: str) -> str:
        if self._zoom == 1.0:
            return text

        def repl(match):
            value = float(match.group(2)) * self._zoom
            return f"{match.group(1)}{value:.2f}{match.group(3)}"

        return self._FONTSIZE_RE.sub(repl, text)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._raw_html:
            self._refit_timer.start()

    def wheelEvent(self, event):
        if event.modifiers() & QtCore.Qt.ControlModifier:
            step = 1.1 if event.angleDelta().y() > 0 else 1 / 1.1
            self._zoom = max(0.2, min(5.0, self._zoom * step))
            self._render()
            event.accept()
        else:
            super().wheelEvent(event)


class Case:
    def __init__(self, name: str):
        self.name = name
        self.approved = SNAPSHOT_DIR / f"{name}.approved.html"
        self.received = SNAPSHOT_DIR / f"{name}.received.html"
        self.history_path = SNAPSHOT_DIR / f"{name}.history.json"

    @property
    def status(self) -> str:
        history = self.load_history()
        last_action = history[-1]["action"] if history else None
        has_approved = self.approved.exists()
        has_received = self.received.exists()

        # A pending output on disk (unreviewed change, or kept after a disapprove)
        # overrides history.
        if has_received:
            if last_action == ACT_DISAPPROVED:
                return STATUS_FAILED
            if not has_approved:
                return STATUS_NEW
            return STATUS_FAILED
        if not has_approved:
            return STATUS_NEW

        # No pending output: the status is the running result of the verdict
        # sequence. "correct" sets correct; "disapprove" sets failed; "unchanged"
        # keeps whatever came before (and only establishes "consistent" when it is
        # the first verdict). So only "correct" can clear a "failed".
        result = None
        for entry in history:
            action = entry.get("action")
            if action == ACT_CORRECT:
                result = STATUS_CORRECT
            elif action == ACT_DISAPPROVED:
                result = STATUS_FAILED
            elif action == ACT_UNCHANGED and result is None:
                result = STATUS_CONSISTENT
        return result if result is not None else STATUS_CONSISTENT

    def benchmark_html(self) -> str:
        if self.approved.exists():
            return self.approved.read_text(encoding="utf-8")
        return "<p style='color:#888'>— no benchmark yet —</p>"

    def output_html(self) -> str:
        # The "output" is the last received; when nothing differed, the approved
        # file *is* the current output.
        source = self.received if self.received.exists() else self.approved
        if source.exists():
            return source.read_text(encoding="utf-8")
        return "<p style='color:#888'>— no output —</p>"

    def promote_received(self):
        """received -> approved (the new benchmark). No-op if nothing is pending."""
        if self.received.exists():
            self.approved.write_text(self.received.read_text(encoding="utf-8"), encoding="utf-8")
            self.received.unlink()

    def load_history(self) -> list:
        if self.history_path.exists():
            try:
                return json.loads(self.history_path.read_text(encoding="utf-8"))
            except Exception:
                return []
        return []

    def add_history(self, action: str, comment: str):
        history = self.load_history()
        history.append(
            {
                "time": datetime.now().isoformat(timespec="seconds"),
                "action": action,
                "comment": comment,
            }
        )
        self.history_path.write_text(
            json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8"
        )


def render_history_html(history: list) -> str:
    if not history:
        return "<p style='color:#888'>No history yet.</p>"
    blocks = []
    for entry in reversed(history):  # newest first
        action = entry.get("action", "")
        label = ACTION_LABEL.get(action, action)
        color = ACTION_COLOR.get(action, "#000")
        raw_comment = entry.get("comment", "")
        if not raw_comment or raw_comment == DEFAULT_UNCHANGED_COMMENT:
            text = raw_comment or "(no comment)"
            comment = f"<i style='color:#888'>{html.escape(text)}</i>"
        else:
            comment = html.escape(raw_comment)
        blocks.append(
            "<div style='margin-bottom:10px;'>"
            f"<span style='color:{color}; font-weight:bold;'>{label}</span> "
            f"<span style='color:#999; font-size:small;'>{html.escape(entry.get('time', ''))}</span>"
            f"<div style='margin-top:2px;'>{comment}</div>"
            "</div>"
        )
    return "".join(blocks)


class ReviewWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("StatPrism — Snapshot Review")
        self.resize(1360, 860)
        self._build_ui()
        self.reload_cases()

    def _build_ui(self):
        toolbar = self.addToolBar("Main")
        toolbar.setMovable(False)

        self.run_action = QtGui.QAction("Run tests", self)
        self.run_action.triggered.connect(self.run_tests)
        toolbar.addAction(self.run_action)

        self.refresh_action = QtGui.QAction("Refresh", self)
        self.refresh_action.triggered.connect(self.reload_cases)
        toolbar.addAction(self.refresh_action)

        # Left: case list. Right: everything else.
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)

        self.case_list = QtWidgets.QListWidget()
        self.case_list.setMinimumWidth(260)
        self.case_list.currentItemChanged.connect(self.on_case_changed)
        splitter.addWidget(self.case_list)

        right = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)

        self.header = QtWidgets.QLabel("")
        self.header.setContentsMargins(8, 6, 8, 6)
        self.header.setStyleSheet("font-weight: bold;")
        right_layout.addWidget(self.header)

        vsplit = QtWidgets.QSplitter(QtCore.Qt.Vertical)

        # Top: benchmark | output.
        panes = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        panes.addWidget(self._titled_view("Benchmark (approved)", "benchmark_view"))
        panes.addWidget(self._titled_view("Output (received)", "output_view"))
        panes.setSizes([680, 680])
        vsplit.addWidget(panes)

        # Bottom: review controls | history.
        bottom = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        bottom.addWidget(self._build_controls())
        bottom.addWidget(self._build_history())
        bottom.setSizes([820, 540])
        vsplit.addWidget(bottom)

        vsplit.setSizes([640, 200])
        right_layout.addWidget(vsplit, 1)

        splitter.addWidget(right)
        splitter.setSizes([280, 1080])
        self.setCentralWidget(splitter)

        self.status_bar = self.statusBar()

    def _titled_view(self, title: str, attr: str) -> QtWidgets.QWidget:
        container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)
        label = QtWidgets.QLabel(title)
        label.setStyleSheet("color:#555; padding:2px;")
        layout.addWidget(label)
        view = HtmlView()
        view.setOpenExternalLinks(False)
        layout.addWidget(view, 1)
        setattr(self, attr, view)
        return container

    def _build_controls(self) -> QtWidgets.QWidget:
        box = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(box)
        layout.setContentsMargins(8, 4, 8, 8)

        hint = QtWidgets.QLabel("Comment (you can write while reviewing; confirmed on the popup):")
        hint.setStyleSheet("color:#555;")
        layout.addWidget(hint)

        self.comment_edit = QtWidgets.QPlainTextEdit()
        self.comment_edit.setPlaceholderText(
            f"Optional. 'Approve as unchanged' defaults to “{DEFAULT_UNCHANGED_COMMENT}”."
        )
        self.comment_edit.setFixedHeight(72)
        layout.addWidget(self.comment_edit)

        buttons = QtWidgets.QHBoxLayout()
        self.btn_correct = QtWidgets.QPushButton("✓  Approve as correct")
        self.btn_correct.setStyleSheet("color:#2e7d32; font-weight:bold;")
        self.btn_correct.clicked.connect(lambda: self.do_action(ACT_CORRECT))

        self.btn_unchanged = QtWidgets.QPushButton("=  Approve as unchanged")
        self.btn_unchanged.setStyleSheet("color:#1565c0; font-weight:bold;")
        self.btn_unchanged.clicked.connect(lambda: self.do_action(ACT_UNCHANGED))

        self.btn_disapprove = QtWidgets.QPushButton("✗  Disapprove")
        self.btn_disapprove.setStyleSheet("color:#c62828; font-weight:bold;")
        self.btn_disapprove.clicked.connect(lambda: self.do_action(ACT_DISAPPROVED))

        for btn in (self.btn_correct, self.btn_unchanged, self.btn_disapprove):
            buttons.addWidget(btn)
        layout.addLayout(buttons)
        layout.addStretch(1)
        return box

    def _build_history(self) -> QtWidgets.QWidget:
        box = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(box)
        layout.setContentsMargins(4, 4, 8, 8)
        layout.addWidget(QtWidgets.QLabel("History:"))
        self.history_view = QtWidgets.QTextBrowser()
        layout.addWidget(self.history_view, 1)
        return box

    # ----- data -----
    def discover_cases(self):
        if not SNAPSHOT_DIR.exists():
            return []
        names = set()
        for path in SNAPSHOT_DIR.glob("*.approved.html"):
            names.add(path.name[: -len(".approved.html")])
        for path in SNAPSHOT_DIR.glob("*.received.html"):
            names.add(path.name[: -len(".received.html")])
        for path in SNAPSHOT_DIR.glob("*.history.json"):
            names.add(path.name[: -len(".history.json")])
        return [Case(n) for n in sorted(names)]

    def reload_cases(self):
        previous = self.current_case().name if self.current_case() else None
        self.case_list.blockSignals(True)
        self.case_list.clear()
        cases = self.discover_cases()
        for case in cases:
            item = QtWidgets.QListWidgetItem(f"[{case.status}]  {case.name}")
            item.setData(QtCore.Qt.UserRole, case.name)
            item.setForeground(QtGui.QColor(STATUS_COLOR[case.status]))
            self.case_list.addItem(item)
        self.case_list.blockSignals(False)

        if self.case_list.count():
            target = 0
            if previous:
                for i in range(self.case_list.count()):
                    if self.case_list.item(i).data(QtCore.Qt.UserRole) == previous:
                        target = i
                        break
            self.case_list.setCurrentRow(target)
            self.on_case_changed()
        else:
            self.header.setText("No snapshots found. Run the tests first.")
            self.benchmark_view.clear()
            self.output_view.clear()
            self.history_view.clear()
            self._set_buttons_enabled(False)

        needing = sum(1 for c in cases if c.status in NEEDS_REVIEW)
        self.status_bar.showMessage(
            f"{len(cases)} case(s), {needing} needing review — {SNAPSHOT_DIR}"
        )

    def _reload_and_advance(self):
        """Reload the list, then move selection to the next case (clamped at the end).

        Used by the unchanged fast path: the just-approved case keeps its place in the
        (name-sorted) list, so row+1 is the next one to review.
        """
        row = self.case_list.currentRow()
        self.reload_cases()
        count = self.case_list.count()
        if count:
            self.case_list.setCurrentRow(min(row + 1, count - 1))

    def current_case(self):
        item = self.case_list.currentItem()
        if item is None:
            return None
        return Case(item.data(QtCore.Qt.UserRole))

    def _set_buttons_enabled(self, enabled: bool):
        for btn in (self.btn_correct, self.btn_unchanged, self.btn_disapprove):
            btn.setEnabled(enabled)

    def on_case_changed(self, *_):
        case = self.current_case()
        if case is None:
            return
        color = STATUS_COLOR[case.status]
        self.header.setText(f"{case.name}   ·   {case.status}")
        self.header.setStyleSheet(f"font-weight:bold; color:{color};")
        self.benchmark_view.setHtml(case.benchmark_html())
        self.output_view.setHtml(case.output_html())
        self.history_view.setHtml(render_history_html(case.load_history()))
        self._set_buttons_enabled(True)

    def do_action(self, action: str):
        case = self.current_case()
        if case is None:
            return

        # Fast path: "approve as unchanged" skips the confirmation popup, records the
        # inline comment (or the default), and advances to the next case so a reviewer
        # can sweep through the consistent ones quickly.
        if action == ACT_UNCHANGED:
            comment = self.comment_edit.toPlainText().strip() or DEFAULT_UNCHANGED_COMMENT
            case.promote_received()  # accept the pending output as benchmark (no-op if none)
            case.add_history(action, comment)
            self.comment_edit.clear()
            self._reload_and_advance()
            self.status_bar.showMessage(f"{ACTION_LABEL[action]}: {case.name}")
            return

        # Confirmation popup carrying the comment, so a verdict can't be a stray click.
        # It is pre-filled with whatever was typed inline while reviewing.
        default = self.comment_edit.toPlainText().strip()
        if action == ACT_UNCHANGED and not default:
            default = DEFAULT_UNCHANGED_COMMENT
        comment, ok = QtWidgets.QInputDialog.getMultiLineText(
            self,
            ACTION_TITLE[action],
            f"Comment for “{case.name}” (this will be recorded):",
            default,
        )
        if not ok:
            return
        comment = comment.strip()
        if action == ACT_UNCHANGED and not comment:
            comment = DEFAULT_UNCHANGED_COMMENT

        if action in (ACT_CORRECT, ACT_UNCHANGED):
            case.promote_received()  # accept the pending output as benchmark (no-op if none)
        # Disapprove leaves the received output in place so it stays flagged.

        case.add_history(action, comment)
        self.comment_edit.clear()
        self.reload_cases()
        self.status_bar.showMessage(f"{ACTION_LABEL[action]}: {case.name}")

    # ----- running -----
    def run_tests(self):
        self.run_action.setEnabled(False)
        self.status_bar.showMessage("Running pytest…")
        self.process = QtCore.QProcess(self)
        self.process.setWorkingDirectory(str(REPO_ROOT))
        self.process.setProcessChannelMode(QtCore.QProcess.MergedChannels)
        self.process.finished.connect(self.on_tests_finished)
        # Use the same interpreter that launched this tool.
        self.process.start(sys.executable, ["-m", "pytest", "-q"])

    def on_tests_finished(self, *_):
        output = bytes(self.process.readAll()).decode(errors="replace")
        self.run_action.setEnabled(True)
        self.reload_cases()
        last_line = output.strip().splitlines()[-1] if output.strip() else "done"
        self.status_bar.showMessage(f"pytest: {last_line}")


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = ReviewWindow()
    window.showMaximized()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
