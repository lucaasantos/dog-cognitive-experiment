"""Futuristic PySide6 cognitive dashboard."""

from html import escape

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from evaluator import (
    evaluate_state,
    generate_reflection,
    load_memory,
    process_experience,
    save_memory,
)
from ui.animations.pulse import attach_pulse
from ui.components.meters import AnimatedMeter, CircularGauge
from ui.components.panels import MetricBlock, NeonCard
from ui.ml_observer import append_and_retrain, dataset_stats, prediction_snapshot, top_tokens
from ui.styles.neon import ACCENT, BACKGROUND, CARD_ALT, MUTED, PRIMARY, TEXT, dashboard_stylesheet


class DogCognitiveApp:
    """Application wrapper matching the original Tkinter app contract."""

    def __init__(self):
        self.qt_app = QApplication.instance() or QApplication([])
        self.window = CognitiveDashboard()

    def run(self):
        self.window.show()
        self.qt_app.exec()


class CognitiveDashboard(QMainWindow):
    """Live dashboard for memory, belief state, and ML observability."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("DOG COGNITIVE EXPERIMENT V3")
        self.resize(1360, 860)
        self.setMinimumSize(1080, 720)

        self.memory = load_memory()
        self.memory["current_assessment"] = evaluate_state(self.memory.get("fear_total", 0))
        save_memory(self.memory)

        self.activity_seed = [
            "[SYSTEM ONLINE] Persistent cognitive memory loaded.",
            "[ML OBSERVER] CountVectorizer and Naive Bayes pipeline ready.",
            "[COGNITIVE STATE] Awaiting a new dog-related experience.",
        ]
        self.last_snapshot = None

        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        self.setStyleSheet(dashboard_stylesheet())

        self.root_layout = QVBoxLayout(root)
        self.root_layout.setContentsMargins(22, 18, 22, 22)
        self.root_layout.setSpacing(16)

        self._build_header()
        self._build_dashboard()
        self._start_timers()
        self.refresh_interface()

    def _build_header(self):
        header = QFrame()
        layout = QVBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(7)

        title_row = QHBoxLayout()
        title_col = QVBoxLayout()
        title_col.setSpacing(3)

        self.title = QLabel("DOG COGNITIVE EXPERIMENT V3")
        self.title.setObjectName("title")
        self.subtitle = QLabel("Hybrid Symbolic + Machine Learning Cognitive Agent")
        self.subtitle.setObjectName("subtitle")
        title_col.addWidget(self.title)
        title_col.addWidget(self.subtitle)

        self.status_label = QLabel("MODEL STATUS: SYNCHRONIZED")
        self.status_label.setStyleSheet(f"color: {PRIMARY}; font-weight: 800;")
        self.status_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        title_row.addLayout(title_col, 1)
        title_row.addWidget(self.status_label)

        line = QFrame()
        line.setObjectName("headerLine")

        layout.addLayout(title_row)
        layout.addWidget(line)
        self.root_layout.addWidget(header)
        self.header_pulse = attach_pulse(line, start=0.38, end=1.0, duration=1600)

    def _build_dashboard(self):
        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(16)
        grid.setColumnStretch(0, 4)
        grid.setColumnStretch(1, 5)
        self.root_layout.addLayout(grid, 1)

        left = QVBoxLayout()
        left.setSpacing(16)
        right = QVBoxLayout()
        right.setSpacing(16)
        grid.addLayout(left, 0, 0)
        grid.addLayout(right, 0, 1)

        self._build_input_panel(left)
        self._build_state_panel(left)
        self._build_belief_panel(left)
        self._build_reflection_panel(left)

        self._build_learning_panel(right)
        self._build_ml_panel(right)
        self._build_tokens_and_dataset(right)
        self._build_stream_panel(right)

    def _build_input_panel(self, parent):
        card = NeonCard("EXPERIENCE INPUT")
        self.input_text = QPlainTextEdit()
        self.input_text.setPlaceholderText("Describe a new dog-related experience...")
        self.input_text.setMinimumHeight(102)
        self.input_text.textChanged.connect(self.preview_prediction)

        self.send_button = QPushButton("SEND EXPERIENCE")
        self.send_button.clicked.connect(self.submit_experience)

        card.layout.addWidget(self.input_text)
        card.layout.addWidget(self.send_button, alignment=Qt.AlignRight)
        parent.addWidget(card)

    def _build_state_panel(self, parent):
        card = NeonCard("STATE VISUALIZATION")
        gauges = QHBoxLayout()
        gauges.setSpacing(12)
        self.fear_gauge = CircularGauge("Fear")
        self.confidence_gauge = CircularGauge("Confidence")
        self.stability_gauge = CircularGauge("Stability")
        gauges.addWidget(self.fear_gauge)
        gauges.addWidget(self.confidence_gauge)
        gauges.addWidget(self.stability_gauge)

        self.fear_meter = AnimatedMeter("FEAR LEVEL")
        self.confidence_meter = AnimatedMeter("BELIEF CONFIDENCE")
        self.stability_meter = AnimatedMeter("ADAPTATION STABILITY")

        card.layout.addLayout(gauges)
        card.layout.addWidget(self.fear_meter)
        card.layout.addWidget(self.confidence_meter)
        card.layout.addWidget(self.stability_meter)
        parent.addWidget(card)

    def _build_belief_panel(self, parent):
        card = NeonCard("CURRENT DOMINANT BELIEF")
        self.belief_text = QLabel()
        self.belief_text.setWordWrap(True)
        self.belief_text.setStyleSheet(f"color: {TEXT}; font-size: 18px; font-weight: 800;")
        self.belief_meta = QLabel()
        self.belief_meta.setStyleSheet(f"color: {MUTED}; font-size: 12px;")
        card.layout.addWidget(self.belief_text)
        card.layout.addWidget(self.belief_meta)
        parent.addWidget(card)

    def _build_reflection_panel(self, parent):
        card = NeonCard("COGNITIVE REFLECTION")
        self.reflection_text = QLabel()
        self.reflection_text.setWordWrap(True)
        self.reflection_text.setStyleSheet(f"color: {TEXT}; font-size: 14px; line-height: 140%;")
        card.layout.addWidget(self.reflection_text)
        parent.addWidget(card, 1)

    def _build_learning_panel(self, parent):
        card = NeonCard("LIVE LEARNING STREAM")
        self.learning_feed = QTextEdit()
        self.learning_feed.setReadOnly(True)
        self.learning_feed.setMinimumHeight(162)
        card.layout.addWidget(self.learning_feed)
        parent.addWidget(card)

    def _build_ml_panel(self, parent):
        card = NeonCard("ML ACTIVITY")
        metrics = QGridLayout()
        metrics.setHorizontalSpacing(14)
        metrics.setVerticalSpacing(10)

        self.predicted_class = MetricBlock("CURRENT PREDICTED CLASS")
        self.prediction_confidence = MetricBlock("PREDICTION CONFIDENCE")
        self.model_confidence = MetricBlock("MODEL CONFIDENCE")
        self.detected_tokens = MetricBlock("DETECTED IMPORTANT TOKENS")
        self.feature_evidence = MetricBlock("LEARNED FEATURE IMPORTANCE")

        metrics.addWidget(self.predicted_class, 0, 0)
        metrics.addWidget(self.prediction_confidence, 0, 1)
        metrics.addWidget(self.model_confidence, 1, 0)
        metrics.addWidget(self.detected_tokens, 1, 1)
        metrics.addWidget(self.feature_evidence, 2, 0, 1, 2)

        self.class_meter = AnimatedMeter("LIVE CLASSIFICATION CONFIDENCE")
        card.layout.addLayout(metrics)
        card.layout.addWidget(self.class_meter)
        parent.addWidget(card)

    def _build_tokens_and_dataset(self, parent):
        row = QHBoxLayout()
        row.setSpacing(16)

        tokens_card = NeonCard("TOP LEARNED TOKENS")
        tokens_layout = QHBoxLayout()
        self.aggressive_tokens = QListWidget()
        self.friendly_tokens = QListWidget()
        tokens_layout.addWidget(self._list_wrap("TOP AGGRESSIVE TOKENS", self.aggressive_tokens))
        tokens_layout.addWidget(self._list_wrap("TOP FRIENDLY TOKENS", self.friendly_tokens))
        tokens_card.layout.addLayout(tokens_layout)

        dataset_card = NeonCard("DATASET STATISTICS")
        self.total_experiences = MetricBlock("TOTAL LEARNED EXPERIENCES")
        self.class_distribution = MetricBlock("CLASS DISTRIBUTION")
        self.ratio = MetricBlock("AGGRESSIVE VS FRIENDLY RATIO")
        self.dataset_growth = MetricBlock("DATASET GROWTH")
        dataset_card.layout.addWidget(self.total_experiences)
        dataset_card.layout.addWidget(self.class_distribution)
        dataset_card.layout.addWidget(self.ratio)
        dataset_card.layout.addWidget(self.dataset_growth)

        row.addWidget(tokens_card, 1)
        row.addWidget(dataset_card, 1)
        parent.addLayout(row)

    def _list_wrap(self, title, widget):
        frame = QFrame()
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        label = QLabel(title)
        label.setObjectName("metricLabel")
        widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(label)
        layout.addWidget(widget)
        return frame

    def _build_stream_panel(self, parent):
        card = NeonCard("COGNITIVE ACTIVITY LOG")
        self.activity_log = QListWidget()
        card.layout.addWidget(self.activity_log)
        parent.addWidget(card, 1)

    def _start_timers(self):
        self.activity_timer = QTimer(self)
        self.activity_timer.timeout.connect(self._pulse_idle_activity)
        self.activity_timer.start(5000)

    def submit_experience(self):
        text = self.input_text.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Empty experience", "Enter an experience before submitting.")
            return

        self._add_activity("[NEW EXPERIENCE DETECTED] Input received for cognitive integration.")
        self.status_label.setText("MODEL STATUS: UPDATING")

        self.memory, result = process_experience(text, self.memory)
        label = result.get("prediction_label", "unavailable")

        try:
            append_and_retrain(text, label)
            self._add_activity("[MEMORY UPDATE] Persistent memory successfully updated.")
            self._add_activity("[ML UPDATE] Dataset appended and Naive Bayes model retrained.")
            self.status_label.setText("MODEL UPDATED")
        except Exception as exc:
            self._add_activity(f"[ML UPDATE] Retrain skipped: {exc}")
            self.status_label.setText("MODEL STATUS: MEMORY UPDATED")

        self.input_text.blockSignals(True)
        self.input_text.clear()
        self.input_text.blockSignals(False)

        self.refresh_interface(result=result, submitted_text=text)
        QTimer.singleShot(1800, lambda: self.status_label.setText("MODEL STATUS: SYNCHRONIZED"))

    def preview_prediction(self):
        text = self.input_text.toPlainText().strip()
        if len(text) < 3:
            return
        try:
            snapshot = prediction_snapshot(text)
        except Exception:
            return
        self.last_snapshot = snapshot
        self._apply_prediction_snapshot(snapshot)

    def refresh_interface(self, result=None, submitted_text=None):
        fear = float(self.memory.get("fear_total", 0))
        confidence = float(self.memory.get("belief_confidence", 0))
        assessment = self.memory.get("current_assessment") or evaluate_state(fear)
        stability = self._calculate_stability()

        fear_percent = min(100, fear * 2.6)
        self.fear_gauge.animate_to(fear_percent)
        self.confidence_gauge.animate_to(confidence)
        self.stability_gauge.animate_to(stability)
        self.fear_meter.set_value(fear_percent)
        self.confidence_meter.set_value(confidence)
        self.stability_meter.set_value(stability)

        self.belief_text.setText(f'"{assessment}"')
        self.belief_meta.setText(f"Fear total {fear:.2f} | Belief confidence {confidence:.1f}%")
        self.reflection_text.setText(generate_reflection(self.memory))

        if submitted_text and result:
            try:
                snapshot = prediction_snapshot(submitted_text)
            except Exception:
                snapshot = None
            self._render_learning_event(submitted_text, result, snapshot)
            if snapshot:
                self._apply_prediction_snapshot(snapshot)
        elif self.last_snapshot:
            self._apply_prediction_snapshot(self.last_snapshot)
        else:
            latest = self.memory.get("experiences", [])[-1:]
            if latest:
                self._apply_recent_experience(latest[0])

        self._refresh_tokens()
        self._refresh_dataset_stats()
        self._refresh_activity_seed()

    def _render_learning_event(self, text, result, snapshot):
        label = result.get("prediction_label", "unavailable").upper()
        confidence = result.get("prediction_confidence", 0) * 100
        tokens = snapshot.get("active_tokens", []) if snapshot else result.get("detected_events", [])
        token_lines = "".join(f"<li>{escape(str(token))}</li>" for token in tokens[:8]) or "<li>no active token matched</li>"
        impact = result.get("impact", 0)
        safe_text = escape(text)

        html = f"""
        <div style="color:{PRIMARY}; font-weight:800;">[NEW EXPERIENCE DETECTED]</div>
        <div style="margin-top:6px; color:{TEXT};">Input:<br><b>"{safe_text}"</b></div>
        <div style="margin-top:8px;">ML Classification:<br><b style="color:{ACCENT};">{label}</b></div>
        <div>Confidence:<br><b>{confidence:.1f}%</b></div>
        <div style="margin-top:8px;">Detected features:<ul>{token_lines}</ul></div>
        <div>Belief impact:<br><b>{impact:+.2f} fear</b></div>
        <div style="color:{PRIMARY}; margin-top:8px;">Memory updated successfully.</div>
        """
        self.learning_feed.setHtml(html)

    def _apply_prediction_snapshot(self, snapshot):
        confidence = snapshot.get("confidence", 0) * 100
        self.predicted_class.set_value(snapshot.get("label", "none").upper())
        self.prediction_confidence.set_value(f"{confidence:.1f}%")
        self.model_confidence.set_value(self._probability_line(snapshot.get("probabilities", {})))
        tokens = ", ".join(snapshot.get("active_tokens", [])[:6]) or "no active tokens"
        self.detected_tokens.set_value(tokens)
        evidence = ", ".join(token for token, _score in snapshot.get("evidence", [])[:5]) or "no learned evidence"
        self.feature_evidence.set_value(evidence)
        self.class_meter.set_value(confidence)

    def _apply_recent_experience(self, experience):
        label = experience.get("prediction_label", "none")
        confidence = experience.get("prediction_confidence", 0) * 100
        self.predicted_class.set_value(label.upper())
        self.prediction_confidence.set_value(f"{confidence:.1f}%")
        self.model_confidence.set_value("latest memory entry")
        self.detected_tokens.set_value(", ".join(experience.get("detected_events", [])) or "symbolic events unavailable")
        self.feature_evidence.set_value("type a new experience to inspect feature evidence")
        self.class_meter.set_value(confidence)

    def _probability_line(self, probabilities):
        if not probabilities:
            return "unavailable"
        ranked = sorted(probabilities.items(), key=lambda item: item[1], reverse=True)[:3]
        return " | ".join(f"{label}: {value * 100:.0f}%" for label, value in ranked)

    def _refresh_tokens(self):
        try:
            tokens = top_tokens()
        except Exception:
            tokens = {"aggressive": [], "friendly": []}

        self.aggressive_tokens.clear()
        self.friendly_tokens.clear()
        for token in tokens.get("aggressive", []):
            self.aggressive_tokens.addItem(token)
        for token in tokens.get("friendly", []):
            self.friendly_tokens.addItem(token)

    def _refresh_dataset_stats(self):
        stats = dataset_stats()
        distribution = stats.get("distribution", {})
        compact = ", ".join(f"{key}:{value}" for key, value in sorted(distribution.items())) or "empty"
        self.total_experiences.set_value(stats.get("total", 0))
        self.class_distribution.set_value(compact)
        self.ratio.set_value(stats.get("ratio", "0:0"))
        self.dataset_growth.set_value(f"+{len(self.memory.get('experiences', []))} memory events")

    def _refresh_activity_seed(self):
        if self.activity_log.count() == 0:
            for entry in self.activity_seed:
                self._add_activity(entry)

    def _add_activity(self, text):
        self.activity_log.insertItem(0, text)
        while self.activity_log.count() > 32:
            self.activity_log.takeItem(self.activity_log.count() - 1)

    def _pulse_idle_activity(self):
        if not self.memory.get("experiences"):
            return
        reflection = generate_reflection(self.memory)
        self._add_activity(f"[REFLECTION] {reflection}")

    def _calculate_stability(self):
        recent = self.memory.get("experiences", [])[-6:]
        if len(recent) < 2:
            return 72
        impacts = [abs(float(item.get("impact", 0))) for item in recent]
        volatility = min(100, sum(impacts) / len(impacts) * 7)
        return max(0, 100 - volatility)
