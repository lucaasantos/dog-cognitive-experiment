"""Animated state meters for fear, confidence, and stability."""

from PySide6.QtCore import Property, QEasingCurve, QPropertyAnimation, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QLabel, QProgressBar, QVBoxLayout, QWidget

from ui.styles.neon import CARD_ALT, DANGER, MUTED, PRIMARY, SUCCESS, TEXT, WARNING


class AnimatedMeter(QWidget):
    """Labelled progress bar with smooth numeric transitions."""

    def __init__(self, title, maximum=100, parent=None):
        super().__init__(parent)
        self._value = 0
        self.maximum = maximum

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        self.label = QLabel(title)
        self.label.setObjectName("metricLabel")
        self.value_label = QLabel("0%")
        self.value_label.setStyleSheet(f"color: {TEXT}; font-weight: 800;")
        self.bar = QProgressBar()
        self.bar.setRange(0, maximum)

        layout.addWidget(self.label)
        layout.addWidget(self.value_label)
        layout.addWidget(self.bar)

        self.animation = QPropertyAnimation(self, b"animatedValue", self)
        self.animation.setDuration(520)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)

    def get_animated_value(self):
        return self._value

    def set_animated_value(self, value):
        self._value = int(value)
        self.bar.setValue(self._value)
        self.value_label.setText(f"{self._value}%")

    animatedValue = Property(int, get_animated_value, set_animated_value)

    def set_value(self, value):
        value = max(0, min(self.maximum, int(round(value))))
        self.animation.stop()
        self.animation.setStartValue(self._value)
        self.animation.setEndValue(value)
        self.animation.start()


class CircularGauge(QWidget):
    """Circular neon gauge for dominant state intensity."""

    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.title = title
        self._value = 0
        self.setMinimumSize(132, 132)

        self.animation = QPropertyAnimation(self, b"value", self)
        self.animation.setDuration(650)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)

    def get_value(self):
        return self._value

    def set_value(self, value):
        self._value = max(0, min(100, int(value)))
        self.update()

    value = Property(int, get_value, set_value)

    def animate_to(self, value):
        self.animation.stop()
        self.animation.setStartValue(self._value)
        self.animation.setEndValue(max(0, min(100, int(round(value)))))
        self.animation.start()

    def paintEvent(self, _event):
        width = self.width()
        height = self.height()
        side = min(width, height) - 18
        x = (width - side) / 2
        y = 6

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        base_pen = QPen(QColor(CARD_ALT), 10, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(base_pen)
        painter.drawArc(int(x), int(y), int(side), int(side), 225 * 16, -270 * 16)

        color = PRIMARY
        if self._value >= 72:
            color = DANGER
        elif self._value >= 45:
            color = WARNING
        elif self._value < 24:
            color = SUCCESS

        value_pen = QPen(QColor(color), 10, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(value_pen)
        painter.drawArc(int(x), int(y), int(side), int(side), 225 * 16, int(-270 * 16 * (self._value / 100)))

        painter.setPen(QColor(TEXT))
        painter.drawText(self.rect().adjusted(0, 6, 0, -22), Qt.AlignCenter, f"{self._value}%")
        painter.setPen(QColor(MUTED))
        painter.drawText(self.rect().adjusted(0, 84, 0, 0), Qt.AlignHCenter | Qt.AlignTop, self.title)
