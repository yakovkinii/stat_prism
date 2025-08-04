#  Copyright (c) 2023 StatPrism Team. All rights reserved.
import re
import sys

from PySide6.QtCore import QMimeData
from PySide6.QtGui import QContextMenuEvent, QGuiApplication
from PySide6.QtWidgets import QApplication, QTextBrowser


def clean_fragment(html: str) -> str:
    """Remove Qt's fragment markers and extract body content."""
    html = re.sub(r"<!--StartFragment-->|<!--EndFragment-->", "", html)
    match = re.search(r"<body[^>]*>(.*?)</body>", html, re.DOTALL | re.IGNORECASE)
    if match:
        html = match.group(1).strip()
    html = re.sub(r"^\s*<p[^>]*><br\s*/?></p>", "", html, flags=re.IGNORECASE)
    return html.strip()


def build_cf_html(fragment: str) -> bytes:
    """Wrap HTML fragment in CF_HTML format."""
    # Build full HTML
    header = "<html><head><meta charset='utf-8'></head><body>"
    footer = "</body></html>"
    html = f"{header}<!--StartFragment-->{fragment}<!--EndFragment-->{footer}"

    # Calculate byte offsets
    prefix_template = (
        "Version:1.0\r\n"
        "StartHTML:{starthtml:08d}\r\n"
        "EndHTML:{endhtml:08d}\r\n"
        "StartFragment:{startfrag:08d}\r\n"
        "EndFragment:{endfrag:08d}\r\n"
    )
    prefix_len = len(prefix_template.format(starthtml=0, endhtml=0, startfrag=0, endfrag=0).encode("utf-8"))

    startfrag = html.index("<!--StartFragment-->") + len("<!--StartFragment-->")
    endfrag = html.index("<!--EndFragment-->")
    starthtml = prefix_len
    endhtml = starthtml + len(html.encode("utf-8"))
    startfrag += starthtml
    endfrag += starthtml

    prefix = prefix_template.format(starthtml=starthtml, endhtml=endhtml, startfrag=startfrag, endfrag=endfrag)
    cf_html = (prefix + html).encode("utf-8")
    return cf_html


class HtmlCopyTextBrowser(QTextBrowser):
    def contextMenuEvent(self, event: QContextMenuEvent):
        menu = self.createStandardContextMenu()
        for action in menu.actions():
            if action.text().lower().startswith("copy"):
                menu.removeAction(action)
                break
        menu.addAction("Copy as Word-Compatible HTML", self.copy_as_cf_html)
        menu.exec(event.globalPos())

    def copy_as_cf_html(self):
        html = self.textCursor().selection().toHtml()
        if not html.strip():
            html = self.toHtml()
        fragment = clean_fragment(html)
        mime = QMimeData()
        mime.setData("text/html", build_cf_html(fragment))  # No plain text!
        QGuiApplication.clipboard().setMimeData(mime)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    browser = HtmlCopyTextBrowser()
    browser.setHtml(
        """
        <table border="1" cellspacing="0" cellpadding="4">
            <tr><th>Variable</th><th>Value</th></tr>
            <tr><td>Age</td><td>54.6</td></tr>
            <tr><td>Height</td><td>149.5</td></tr>
        </table>
    """
    )
    browser.setWindowTitle("QTextBrowser Word-Compatible Copy Example")
    browser.resize(600, 300)
    browser.show()
    sys.exit(app.exec())
