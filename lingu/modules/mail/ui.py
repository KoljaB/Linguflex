from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QStackedWidget,
    QSizePolicy
)
from qfluentwidgets import (
    InfoBadge,
    InfoLevel,
    setTheme,
    Theme,
    TextEdit,
    SegmentedWidget
)
from lingu import UI, Line, StretchLine
from dateutil.parser import parse
from datetime import datetime
from PyQt6.QtCore import Qt, QUrl, pyqtSlot
from PyQt6.QtGui import QDesktopServices
import chardet
import codecs


def safe_decode_escaped_string(escaped_str: str) -> str:
    """
    Safely decodes a string containing escape sequences,
    handling errors gracefully.

    Args:
        escaped_str (str): The string containing escape sequences.

    Returns:
        str: The decoded string, with incomplete escape sequences handled.
    """
    try:
        # First attempt to decode the entire string
        return codecs.decode(escaped_str, 'unicode_escape')
    except UnicodeDecodeError:
        # If an error occurs, try removing characters from the end, one by one
        for i in range(1, 11):  # Limit to removing up to 10 characters
            try:
                return codecs.decode(escaped_str[:-i], 'unicode_escape')
            except UnicodeDecodeError:
                continue

    # Return the original string if all attempts fail
    return escaped_str


def decode(text):
    if not text:
        return ""
    byte_data = text.encode('raw_unicode_escape')
    detected_encoding = chardet.detect(byte_data)['encoding']
    if detected_encoding and detected_encoding == "ascii":
        text = safe_decode_escaped_string(text)
    return text


class MailUI(UI):
    def __init__(self):
        super().__init__()

        setTheme(Theme.DARK)

        self. mail_index = 0

        label = UI.headerlabel("📪 Mail")
        self.header(label, nostyle=True)

        self.buttons = self.add_buttons({
            "prev":
                ("◀", self.prev_char),
            "next":
                ("▶", self.next_char),
        })

        self.mail_position = UI.headerlabel("# 0/0 ")
        self.header(self.mail_position, align="right", nostyle=True)

        line = StretchLine()

        label_from = UI.label("From")
        line.add(label_from)
        self.mail_from = UI.label("")
        self.mail_from.setObjectName("content")
        line.add(self.mail_from)

        label_subject = UI.label("Subject")
        line.add(label_subject)
        self.mail_subject = UI.label()
        self.mail_subject.setMinimumHeight(60)
        self.mail_subject.setObjectName("content")
        line.add(self.mail_subject)

        label_time = UI.label("Time")
        line.add(label_time, align="right", subalign="right")
        self.mail_time = UI.label("")
        self.mail_time.setObjectName("content")
        line.add(self.mail_time, align="right", subalign="right")
        label_importance = UI.label("Importance")
        line.add(label_importance, align="right", subalign="right")
        self.importance = InfoBadge.info(" 1 ")
        self.importance.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Preferred)
        line.add(self.importance, align="right", subalign="right")

        self.add(line)

        self.add(Line())

        self.tab = QWidget(self)

        self.tab.pivot = SegmentedWidget(self.tab)
        self.tab.stackedWidget = QStackedWidget(self.tab)
        self.tab.vBoxLayout = QVBoxLayout(self.tab)

        self.tab.ai_summary = AISummaryWidget()

        oc_widget = QWidget(self)
        oc_layout = QVBoxLayout(oc_widget)
        oc_layout.setContentsMargins(0, 0, 0, 0)
        self.original_content = TextEdit(oc_widget)
        self.original_content.setFixedHeight(330)
        self.original_content.setReadOnly(True)
        self.original_content.setContentsMargins(0, 0, 0, 0)
        oc_layout.addWidget(self.original_content)
        self.tab.original = oc_widget

        # add items to pivot
        self.addSubInterface(
            self.tab.ai_summary,
            "songInterface",
            "AI Summary",
            self.tab)
        self.addSubInterface(
            self.tab.original,
            "albumInterface",
            "Original",
            self.tab)

        self.tab.vBoxLayout.addWidget(self.tab.pivot)
        self.tab.vBoxLayout.addWidget(self.tab.stackedWidget)
        self.tab.vBoxLayout.setContentsMargins(0, 0, 0, 0)

        self.tab.stackedWidget.setCurrentWidget(self.tab.ai_summary)
        self.tab.pivot.setCurrentItem(self.tab.ai_summary.objectName())

        self.add(self.tab)

        self.add_ui_listener(
            self,
            "module_state_saved",
            "mail",
            "update_current_mail")

        self.add_spacer()

        self.update_current_mail()

    def addSubInterface(self, widget: QLabel, objectName, text, base_widget):
        widget.setObjectName(objectName)
        base_widget.stackedWidget.addWidget(widget)
        base_widget.pivot.addItem(
            routeKey=objectName,
            text=text,
            onClick=lambda: base_widget.stackedWidget.setCurrentWidget(widget),
        )

    def setImportance(self, importance: int):
        self.importance.setText(f" {importance} ")
        if importance < 5:
            self.importance.setLevel(InfoLevel.INFOAMTION)
        elif importance < 6:
            self.importance.setLevel(InfoLevel.ATTENTION)
        elif importance < 7:
            self.importance.setLevel(InfoLevel.SUCCESS)
        elif importance < 8:
            self.importance.setLevel(InfoLevel.WARNING)
        else:
            self.importance.setLevel(InfoLevel.ERROR)

    @pyqtSlot()
    def update_current_mail(self):
        self.mails = self.state.processed_mails

        self.mails.sort(
            key=lambda mail:
            parse(mail['raw_date'][:-6]),
                reverse=True)

        if len(self.mails) == 0:
            return
        if self.mail_index >= len(self.mails):
            self.mail_index = len(self.mails) - 1
        current_mail = self.mails[self.mail_index]
        self.mail_position.setText(
            f"# {self.mail_index + 1}/{len(self.mails)} "
        )

        mail_time = parse(current_mail['raw_date'])
        today = datetime.now().date()
        difference = today - mail_time.date()
        difference_days = difference.days

        if difference_days == 0:
            fullstring = f"🕒{mail_time.strftime('%H:%M')}"
        else:
            fullstring = f"🌛{difference_days} 🕒{mail_time.strftime('%H:%M')}"

        self.mail_time.setText(fullstring)
        self.mail_from.setText(current_mail['sender'])
        self.mail_subject.setText(decode(current_mail['subject']))
        self.original_content.setMarkdown(current_mail['content'])

        self.tab.ai_summary.setText(current_mail['summary'])
        self.setImportance(current_mail['importance'])
        self.tab.ai_summary.setLinks(current_mail['links'])

        self.buttons["prev"].setEnabled(self.mail_index > 0)
        self.buttons["next"].setEnabled(self.mail_index < len(self.mails) - 1)

    def prev_char(self):
        if self.mail_index > 0:
            self.mail_index -= 1
            self.update_current_mail()

    def next_char(self):
        if self.mail_index < len(self.mails) - 1:
            self.mail_index += 1
            self.update_current_mail()


class AISummaryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        line = StretchLine()
        label_summary = UI.label("Summary")
        line.add(label_summary)

        self.mail_content = TextEdit(self)
        self.mail_content.setFixedHeight(330)
        self.mail_content.setReadOnly(True)
        self.mail_content.setContentsMargins(0, 0, 0, 0)
        line.add(self.mail_content)
        self.label_links = UI.label()
        self.label_links.setContentsMargins(0, 15, 0, 0)
        line.add(self.label_links, align="right", subalign="right")

        self.links_container = QWidget()
        self.links_layout = QVBoxLayout(self.links_container)
        self.links_layout.setContentsMargins(0, 0, 0, 0)
        self.links_layout.setSpacing(0)

        line.add(self.links_container, align="right", subalign="right")

        layout.addWidget(line, alignment=Qt.AlignmentFlag.AlignTop)

        self.setLayout(layout)

    def setText(self, text):
        self.mail_content.setMarkdown(decode(text))

    def setLinks(self, links):
        # Clear the existing links
        while self.links_layout.count():
            child = self.links_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Remove duplicate hrefs
        unique_links = {link['url']: link for link in links}.values()

        # Sort links and select the top 3
        sorted_links = sorted(
            unique_links,
            key=lambda link: link['name'],
            reverse=True)[:3]

        # Create new labels for the top 3 sorted links with HTML formatting
        self.label_links.setText("Links" if sorted_links else "")
        for link in sorted_links:
            link_name = decode(link['name'])
            link_text = f"<a href='{link['url']}'>{link_name}</a>"

            link_label = QLabel(link_text, self)
            link_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            link_label.setMaximumWidth(200)
            link_label.setTextFormat(Qt.TextFormat.RichText)
            link_label.setWordWrap(True)
            link_label.setTextInteractionFlags(
                Qt.TextInteractionFlag.LinksAccessibleByMouse)
            link_label.linkActivated.connect(
                lambda url=link['url']: self.openLink(url))
            self.links_layout.addWidget(
                link_label,
                alignment=Qt.AlignmentFlag.AlignRight)

    def openLink(self, url):
        QDesktopServices.openUrl(QUrl(url))
