"""Cognitive evaluation and persistent memory logic.

This module does not use an LLM. It combines rule-based interpretation,
persistent JSON memory, emotional decay, and confidence modeling to simulate
adaptive behavior over repeated dog-related experiences.
"""

import json
import re
import unicodedata
from pathlib import Path

from rules import BREED_MULTIPLIERS, CONTEXT_MODIFIERS, EVENT_WEIGHTS


MEMORY_FILE = Path(__file__).with_name("memory.json")
EMOTIONAL_DECAY = 0.98
REFLECTION_WINDOW = 5

INITIAL_MEMORY = {
    "fear_total": 0,
    "belief_confidence": 100,
    "current_assessment": "Dogs seem safe.",
    "experiences": [],
}

# Aliases recognize common English variations while keeping the rule tables
# compact and readable.
PHRASE_ALIASES = {
    "bit": ["bit", "bites"],
    "attacked": ["attacked"],
    "charged": ["charged", "lunged"],
    "growled": ["growled"],
    "barked_aggressively": ["barked aggressively"],
    "chased": ["chased", "ran after me"],
    "played": ["played"],
    "wagged_tail": ["wagged tail", "wagged its tail"],
    "friendly": ["friendly", "was friendly"],
    "received_affection": ["received affection", "received petting"],
    "ignored": ["ignored"],
    "german_shepherd": ["german shepherd"],
    "alone": ["alone"],
    "on_leash": ["on leash", "on a leash"],
    "with_owner": ["with owner", "with its owner"],
    "at_night": ["at night"],
    "puppy": ["puppy"],
}


def evaluate_state(fear_total):
    """Translate numeric fear into a readable cognitive assessment."""
    if 0 <= fear_total <= 4:
        return "Dogs seem safe."
    if 5 <= fear_total <= 10:
        return "Some dogs may represent risk."
    if 11 <= fear_total <= 20:
        return "There is moderate concern about dogs."
    if 21 <= fear_total <= 35:
        return "Dogs are frequently perceived as dangerous."
    return "There is strong aversion and fear toward dogs."


def load_memory():
    """Load persistent JSON memory and normalize missing fields."""
    if not MEMORY_FILE.exists():
        memory = INITIAL_MEMORY.copy()
        save_memory(memory)
        return memory

    with MEMORY_FILE.open("r", encoding="utf-8") as file:
        memory = json.load(file)

    return normalize_memory(memory)


def save_memory(memory):
    """Persist memory so adaptation survives between application sessions."""
    with MEMORY_FILE.open("w", encoding="utf-8") as file:
        json.dump(memory, file, ensure_ascii=False, indent=4)


def normalize_memory(memory):
    """Make sure the persistent memory file contains the expected fields."""
    normalized = dict(memory)
    normalized.setdefault("fear_total", 0)
    normalized.setdefault("belief_confidence", 100)
    normalized.setdefault("experiences", [])
    normalized["current_assessment"] = evaluate_state(normalized["fear_total"])
    return normalized


def normalize_text(text):
    """Lowercase text, remove accents, and keep only searchable word tokens."""
    text = text.lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(char for char in text if unicodedata.category(char) != "Mn")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return f" {text.strip()} "


def phrase_to_regex(phrase):
    parts = [re.escape(part) for part in normalize_text(phrase).strip().split()]
    return r"\b" + r"\s+".join(parts) + r"\b"


def aliases_for(key):
    return PHRASE_ALIASES.get(key, [key.replace("_", " ")])


def detect_weights(normalized_text, table):
    detected = []
    total = 0

    for key, weight in table.items():
        if any(re.search(phrase_to_regex(alias), normalized_text) for alias in aliases_for(key)):
            detected.append(key)
            total += weight

    return detected, total


def detect_breed(normalized_text):
    for breed, multiplier in BREED_MULTIPLIERS.items():
        if any(re.search(phrase_to_regex(alias), normalized_text) for alias in aliases_for(breed)):
            return breed, multiplier
    return "unknown", 1.0


def calculate_impact(text):
    """Calculate final impact: (events + contexts) * breed multiplier."""
    normalized_text = normalize_text(text)
    events, event_total = detect_weights(normalized_text, EVENT_WEIGHTS)
    contexts, context_total = detect_weights(normalized_text, CONTEXT_MODIFIERS)
    breed, breed_multiplier = detect_breed(normalized_text)
    impact = (event_total + context_total) * breed_multiplier

    return {
        "detected_events": events,
        "detected_contexts": contexts,
        "detected_breed": breed,
        "breed_multiplier": breed_multiplier,
        "event_total": event_total,
        "context_total": context_total,
        "impact": round(impact, 2),
    }


def apply_decay(memory):
    """Apply gradual emotional decay before a new experience is integrated."""
    memory["fear_total"] = round(memory.get("fear_total", 0) * EMOTIONAL_DECAY, 2)
    return memory


def classify_impact(impact):
    if impact < 0:
        return "positive"
    if impact > 0:
        return "negative"
    return "neutral"


def update_belief_confidence(current_confidence, impact):
    """Update confidence in the fear belief based on the latest experience."""
    if impact > 0:
        current_confidence += impact * 2
    elif impact < 0:
        current_confidence -= abs(impact) * 4
    else:
        current_confidence *= 0.995

    return round(min(100, max(0, current_confidence)), 1)


def process_experience(text, memory=None):
    """Integrate one experience into memory and persist the updated belief state."""
    memory = normalize_memory(memory or load_memory())
    memory = apply_decay(memory)
    result = calculate_impact(text)
    impact = result["impact"]

    fear_total = round(max(0, memory["fear_total"] + impact), 2)
    belief_confidence = update_belief_confidence(memory["belief_confidence"], impact)
    current_assessment = evaluate_state(fear_total)

    # Each experience stores both detection details and the resulting belief state.
    experience = {
        "text": text,
        "impact": impact,
        "resulting_fear": fear_total,
        "type": classify_impact(impact),
        "detected_events": result["detected_events"],
        "detected_contexts": result["detected_contexts"],
        "detected_breed": result["detected_breed"],
    }

    memory["fear_total"] = fear_total
    memory["belief_confidence"] = belief_confidence
    memory["current_assessment"] = current_assessment
    memory["experiences"].append(experience)
    save_memory(memory)

    return memory, result


def generate_reflection(memory):
    """Generate a simple self-questioning statement from recent experiences."""
    experiences = memory.get("experiences", [])
    recent = experiences[-REFLECTION_WINDOW:]
    positives = sum(1 for item in recent if item.get("type") == "positive")
    negatives = sum(1 for item in recent if item.get("type") == "negative")
    fear_total = memory.get("fear_total", 0)

    if not experiences:
        return "Memory is empty. The system is waiting for experiences."
    if positives > negatives and fear_total > 8:
        return "Recent experiences contradict part of the previous belief state."
    if positives > negatives:
        return "Recent experiences appear positive."
    if negatives > positives and fear_total > 20:
        return "The system still has high caution about dogs."
    if negatives > positives:
        return "Recent experiences reinforce moderate caution."
    return "Recent memory is balanced between caution and safety."


def generate_cognitive_summary(memory):
    experiences = memory.get("experiences", [])
    negatives = sum(1 for item in experiences if item.get("type") == "negative")
    positives = sum(1 for item in experiences if item.get("type") == "positive")
    neutrals = sum(1 for item in experiences if item.get("type") == "neutral")

    return (
        f"Recorded experiences: {len(experiences)}\n"
        f"Negative: {negatives} | Positive: {positives} | Neutral: {neutrals}\n"
        f"Reflection: {generate_reflection(memory)}"
    )
