"""Neon stylesheet and color constants for the cognitive dashboard."""

BACKGROUND = "#0B1020"
CARD = "#111827"
CARD_ALT = "#0F172A"
PRIMARY = "#00F5FF"
HIGHLIGHT = "#38BDF8"
TEXT = "#E5E7EB"
MUTED = "#94A3B8"
ACCENT = "#00D9FF"
WARNING = "#F97316"
SUCCESS = "#22C55E"
DANGER = "#F43F5E"
BORDER = "#1E3A5F"

FONT_STACK = "'Orbitron', 'Rajdhani', 'Exo 2', 'Segoe UI'"


def dashboard_stylesheet():
    return f"""
    * {{
        font-family: {FONT_STACK};
        color: {TEXT};
        letter-spacing: 0px;
    }}

    QMainWindow, QWidget#root {{
        background: {BACKGROUND};
    }}

    QLabel#title {{
        color: {PRIMARY};
        font-size: 30px;
        font-weight: 800;
    }}

    QLabel#subtitle {{
        color: {MUTED};
        font-size: 13px;
        font-weight: 600;
    }}

    QLabel#sectionTitle {{
        color: {PRIMARY};
        font-size: 13px;
        font-weight: 800;
    }}

    QLabel#metricLabel {{
        color: {MUTED};
        font-size: 11px;
        font-weight: 700;
    }}

    QLabel#metricValue {{
        color: {TEXT};
        font-size: 17px;
        font-weight: 800;
    }}

    QFrame#card {{
        background: {CARD};
        border: 1px solid {BORDER};
        border-radius: 8px;
    }}

    QFrame#headerLine {{
        min-height: 2px;
        max-height: 2px;
        background: {PRIMARY};
        border: 0;
    }}

    QTextEdit, QPlainTextEdit {{
        background: {CARD_ALT};
        color: {TEXT};
        border: 1px solid {BORDER};
        border-radius: 8px;
        padding: 12px;
        selection-background-color: {PRIMARY};
        selection-color: {BACKGROUND};
        font-size: 13px;
    }}

    QTextEdit:focus, QPlainTextEdit:focus {{
        border: 1px solid {PRIMARY};
    }}

    QPushButton {{
        background: rgba(0, 245, 255, 0.12);
        color: {PRIMARY};
        border: 1px solid {PRIMARY};
        border-radius: 8px;
        padding: 10px 16px;
        font-size: 12px;
        font-weight: 800;
    }}

    QPushButton:hover {{
        background: rgba(0, 245, 255, 0.22);
        border-color: {ACCENT};
    }}

    QPushButton:pressed {{
        background: rgba(0, 245, 255, 0.32);
    }}

    QProgressBar {{
        background: {CARD_ALT};
        border: 1px solid {BORDER};
        border-radius: 6px;
        height: 12px;
        text-align: center;
        color: transparent;
    }}

    QProgressBar::chunk {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {HIGHLIGHT}, stop:1 {PRIMARY});
        border-radius: 5px;
    }}

    QListWidget {{
        background: {CARD_ALT};
        border: 1px solid {BORDER};
        border-radius: 8px;
        padding: 8px;
        font-size: 12px;
    }}

    QListWidget::item {{
        padding: 7px;
        border-bottom: 1px solid rgba(56, 189, 248, 0.12);
    }}

    QScrollBar:vertical {{
        background: {CARD_ALT};
        width: 10px;
    }}

    QScrollBar::handle:vertical {{
        background: {BORDER};
        border-radius: 5px;
    }}
    """
