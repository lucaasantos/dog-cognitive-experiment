"""Panel widgets for the cognitive dashboard."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout


class NeonCard(QFrame):
    """Consistent card container with a title and body layout."""

    def __init__(self, title=None, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setFrameShape(QFrame.NoFrame)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(16, 14, 16, 16)
        self.layout.setSpacing(10)

        if title:
            label = QLabel(title)
            label.setObjectName("sectionTitle")
            label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.layout.addWidget(label)


class MetricBlock(QFrame):
    """Compact metric label/value pair."""

    def __init__(self, label, value="--", parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(3)

        self.label = QLabel(label)
        self.label.setObjectName("metricLabel")
        self.value = QLabel(value)
        self.value.setObjectName("metricValue")
        self.value.setWordWrap(True)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.value)

    def set_value(self, value):
        self.value.setText(str(value))
