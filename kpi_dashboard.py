import sys
from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QStackedWidget,
    QPushButton,
)

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


def label(text, object_name=None, alignment=None, word_wrap=False):
    widget = QLabel(text)
    if object_name:
        widget.setObjectName(object_name)
    if alignment:
        widget.setAlignment(alignment)
    widget.setWordWrap(word_wrap)
    return widget


class ClickableFrame(QFrame):
    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()


class DashboardSummaryCard(ClickableFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("summaryCard")
        self.setFixedSize(360, 272)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 32, 36, 32)
        layout.setSpacing(14)

        layout.addWidget(label("Beschikbaarheid\nShuttlebus", "summaryTitle"))
        layout.addWidget(label("92,6%", "summaryValue"))
        layout.addWidget(label("Gemiddelde beschikbaarheid", "summarySubtitle"))
        layout.addWidget(label(
            "De gemiddelde beschikbaarheid is 92,6%. "
            "De meeste chauffeurs zitten op of boven de norm; "
            "medewerker 36 vraagt extra aandacht.",
            "summaryBody",
            word_wrap=True,
        ))
        layout.addStretch()


class MetricCard(QFrame):
    def __init__(self, icon, title, value):
        super().__init__()
        self.setObjectName("metricCard")
        self.setFixedHeight(118)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 18)
        layout.setSpacing(10)

        top = QHBoxLayout()
        top.setSpacing(12)

        icon_box = label(icon, "metricIcon", Qt.AlignmentFlag.AlignCenter)
        icon_box.setFixedSize(30, 30)
        icon_box.setStyleSheet("""
            background: #f6b000;
            color: #111111;
            border-radius: 4px;
        """)

        top.addWidget(icon_box)
        top.addWidget(label(title, "cardLabel"))
        top.addStretch()

        layout.addLayout(top)
        layout.addWidget(label(value, "cardValue"))


class AvailabilityChart(FigureCanvas):
    def __init__(self):
        self.figure = Figure(figsize=(9, 3.6), dpi=100)
        super().__init__(self.figure)
        self.setMinimumHeight(360)
        self.draw_chart()

    def draw_chart(self):
        rows = [
            ("Medewerker 33", 91),
            ("Medewerker 34", 100),
            ("Medewerker 35", 100),
            ("Medewerker 36", 80),
        ]

        ax = self.figure.add_subplot(111)
        names = [name for name, _ in rows]
        values = [value for _, value in rows]
        positions = range(len(rows))

        self.figure.patch.set_facecolor("#f1f2f4")
        ax.set_facecolor("#ffffff")

        for start in (0, 50):
            ax.axvspan(start, start + 25, color="#eeeeee", zorder=0)

        ax.barh(positions, values, height=0.78, color="#243b70", zorder=3)
        ax.set_xlim(0, 100)
        ax.set_xticks([0, 25, 50, 75, 100])
        ax.set_yticks(list(positions))
        ax.set_yticklabels(names)
        ax.invert_yaxis()

        ax.grid(axis="x", color="#d6dbe2", linewidth=1, zorder=1)
        ax.tick_params(axis="x", colors="#243b70", labelsize=9, length=0, pad=8)
        ax.tick_params(axis="y", colors="#243b70", labelsize=10, length=0, pad=8)

        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)

        ax.spines["bottom"].set_color("#d6dbe2")
        ax.margins(x=0, y=0.18)
        self.figure.subplots_adjust(left=0.125, right=0.948, top=0.86, bottom=0.18)
        self.draw()


class DashboardScreen(QWidget):
    open_details = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setObjectName("screen")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 32)
        layout.setSpacing(54)

        title = label("Dashboard", "dashboardTitle", Qt.AlignmentFlag.AlignCenter)
        card = DashboardSummaryCard()
        card.clicked.connect(self.open_details.emit)

        row = QHBoxLayout()
        row.addWidget(card)
        row.addStretch()

        layout.addWidget(title)
        layout.addLayout(row)
        layout.addStretch()


class ShuttleDashboard(QWidget):
    back_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setObjectName("screen")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 8, 50, 28)
        layout.setSpacing(28)

        layout.addLayout(self.header())
        layout.addLayout(self.cards())
        layout.addWidget(self.chart_card())

    def header(self):
        row = QHBoxLayout()

        back = QPushButton("←")
        back.setObjectName("backButton")
        back.setFixedSize(48, 44)
        back.clicked.connect(self.back_requested.emit)

        title = label(
            "Beschikbaarheid Shuttlebus",
            "title",
            Qt.AlignmentFlag.AlignCenter,
        )

        row.addWidget(back)
        row.addStretch()
        row.addWidget(title)
        row.addStretch()
        row.addSpacing(48)

        return row

    def cards(self):
        row = QHBoxLayout()
        row.setSpacing(16)

        data = [
            ("✓", "Technische status", "In orde"),
            ("!", "Incidenten", "1 vandaag"),
            ("◷", "Huidige chauffeur", "Medewerker 33"),
            ("▣", "volgende aankomst", "10:15"),
        ]

        for item in data:
            row.addWidget(MetricCard(*item))

        return row

    def chart_card(self):
        card = QFrame()
        card.setObjectName("chartCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 24, 24, 18)
        layout.setSpacing(18)

        header = QHBoxLayout()
        header.addWidget(label("Beschikbaarheid per medewerker", "sectionTitle"))
        header.addStretch()
        header.addWidget(label("gemiddelde: 92.6% | klik voor meer details", "chartSubtitle"))

        layout.addLayout(header)
        layout.addWidget(AvailabilityChart())

        return card


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dashboard")
        self.resize(1230, 760)

        stack = QStackedWidget()
        dashboard = DashboardScreen()
        details = ShuttleDashboard()

        stack.addWidget(dashboard)
        stack.addWidget(details)

        dashboard.open_details.connect(lambda: stack.setCurrentWidget(details))
        details.back_requested.connect(lambda: stack.setCurrentWidget(dashboard))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(stack)


def load_qss(app, path):
    qss_path = Path(path)
    if not qss_path.exists():
        raise FileNotFoundError(f"Missing stylesheet: {qss_path.resolve()}")
    app.setStyleSheet(qss_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    load_qss(app, "style.qss")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())