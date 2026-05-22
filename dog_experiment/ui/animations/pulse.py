"""Reusable opacity pulse animation."""

from PySide6.QtCore import QEasingCurve, QPropertyAnimation
from PySide6.QtWidgets import QGraphicsOpacityEffect


def attach_pulse(widget, start=0.62, end=1.0, duration=1400):
    """Attach a looping opacity pulse to a widget and return the animation."""
    effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)

    animation = QPropertyAnimation(effect, b"opacity", widget)
    animation.setStartValue(start)
    animation.setEndValue(end)
    animation.setDuration(duration)
    animation.setEasingCurve(QEasingCurve.InOutSine)
    animation.setLoopCount(-1)
    animation.start()
    return animation
