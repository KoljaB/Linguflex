from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTableWidgetItem,
    QStyleOptionViewItem,
    QAbstractItemView,
    QHeaderView
)
from qfluentwidgets import (
    TableWidget,
    isDarkTheme,
    setTheme,
    Theme,
    TableItemDelegate,
    # setCustomStyleSheet
)
from PyQt6.QtCore import pyqtSignal, QModelIndex, Qt, QTimer
from PyQt6.QtGui import QFont, QPalette
import copy


class CustomTableItemDelegate(TableItemDelegate):
    """ Custom table item delegate """

    def initStyleOption(
            self,
            option: QStyleOptionViewItem,
            index: QModelIndex
    ):
        super().initStyleOption(option, index)
        if index.column() != 1:
            return

        if isDarkTheme():
            option.palette.setColor(
                QPalette.ColorRole.Text, Qt.GlobalColor.white)
            option.palette.setColor(
                QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
        else:
            option.palette.setColor(
                QPalette.ColorRole.Text, Qt.GlobalColor.red)
            option.palette.setColor(
                QPalette.ColorRole.HighlightedText, Qt.GlobalColor.red)


class PlayerWidget(QWidget):
    rowClicked = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.last_playlist = None
        self.current_playing_row = -1

        setTheme(Theme.DARK)

        self.normal_font = QFont()
        self.normal_font.setPointSize(14)  # Set the desired font size

        self.bold_font = QFont()
        self.bold_font.setPointSize(14)  # Set the desired font size
        self.bold_font.setBold(True)

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.playlist = TableWidget()

        self.playlist.verticalHeader().hide()
        self.playlist.setBorderRadius(8)
        self.playlist.setBorderVisible(True)
        self.playlist.setItemDelegate(CustomTableItemDelegate(self.playlist))

        self.playlist.setColumnCount(3)
        self.playlist.setHorizontalHeaderLabels([
            self.tr('#'),
            self.tr('Duration'),
            self.tr('Title')
        ])
        self.playlist.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.playlist.itemClicked.connect(self.on_item_clicked)

        self.playlist.resizeColumnsToContents()

        self.layout.addWidget(self.playlist)

    def format_duration(self, seconds):
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)

        s = int(s)
        m = int(m)
        h = int(h)

        if h:
            return f"{h}:{m:02d}:{s:02d}"
        else:
            return f"{m}:{s:02d}"

    def on_item_clicked(self, item):
        self.current_playing_row = item.row()
        self.playlist.update()
        self.rowClicked.emit(item.row())

    def display(self, audio_information):

        if audio_information:

            playlist_changed = (
                self.last_playlist != audio_information["playlist"]
            )

            audio_index_changed = (
                "audio_index" in audio_information and
                (
                    not hasattr(self, 'current_playing_row') or
                    self.current_playing_row != audio_information[
                        "audio_index"]
                )
            )

            if playlist_changed or audio_index_changed:
                self.playlist.blockSignals(True)
                self.playlist.setRowCount(0)

                for pos, entry in enumerate(audio_information["playlist"]):
                    self.playlist.insertRow(pos)

                    if isinstance(entry, str):
                        self.playlist.setItem(pos, 2, QTableWidgetItem(entry))
                    else:
                        duration = self.format_duration(entry["length"])

                        pos_item = QTableWidgetItem(str(pos + 1) + " ")
                        self.playlist.setItem(pos, 0, pos_item)

                        duration_item = QTableWidgetItem(duration + " ")
                        self.playlist.setItem(pos, 1, duration_item)

                        title_item = QTableWidgetItem(entry["title"])

                        # current playing audio => bold font
                        if "audio_index" in audio_information and \
                                audio_information["audio_index"] == pos:

                            pos_item.setFont(self.bold_font)
                            duration_item.setFont(self.bold_font)
                            title_item.setFont(self.bold_font)
                        else:
                            pos_item.setFont(self.normal_font)
                            duration_item.setFont(self.normal_font)
                            title_item.setFont(self.normal_font)

                        self.playlist.setItem(pos, 2, title_item)

                self.last_playlist = copy.deepcopy(
                    audio_information["playlist"])

                self.playlist.blockSignals(False)

                if audio_index_changed:
                    self.current_playing_row = audio_information["audio_index"]
                    self.playlist.update()

                    # Scroll to the current playing song
                    current_song_index = self.playlist.model().index(
                        audio_information["audio_index"], 0)

                    # Set the current index and select the item
                    self.playlist.delegate.setSelectedRows([
                        current_song_index])

                    self.playlist.scrollTo(
                        current_song_index,
                        QAbstractItemView.ScrollHint.EnsureVisible
                    )
                    self.playlist.viewport().update()

                # Solution 1: Call resizeColumnsToContents after a short delay
                # QTimer.singleShot(100, self.playlist.resizeColumnsToContents)

                # Solution 2: Set a minimum width for the "Title" column
                self.playlist.setColumnWidth(2, 150)

                # Solution 3: Use QHeaderView stretch mode for the "Title" column
                header = self.playlist.horizontalHeader()
                header.setSectionResizeMode(
                    0,
                    QHeaderView.ResizeMode.ResizeToContents)
                header.setSectionResizeMode(
                    1,
                    QHeaderView.ResizeMode.ResizeToContents)
                header.setSectionResizeMode(
                    2,
                    QHeaderView.ResizeMode.Stretch)
