"""Rule tables for the Dog Cognitive Experiment.

Positive weights increase perceived risk. Negative weights reduce perceived risk.
The dictionaries below are intentionally simple so the cognitive behavior remains
transparent and easy to adjust.
"""

EVENT_WEIGHTS = {
    # Negative events reinforce the belief that a dog-related situation may be risky.
    "bit": 10,
    "attacked": 10,
    "charged": 8,
    "growled": 6,
    "barked_aggressively": 5,
    "chased": 7,

    # Positive events reduce fear and weaken confidence in fearful beliefs.
    "played": -6,
    "wagged_tail": -4,
    "friendly": -8,
    "received_affection": -6,
    "ignored": -2,
}

BREED_MULTIPLIERS = {
    "pitbull": 1.5,
    "rottweiler": 1.4,
    "german_shepherd": 1.3,
    "golden": 0.7,
    "labrador": 0.6,
    "pug": 0.4,
}

CONTEXT_MODIFIERS = {
    "alone": 2,
    "on_leash": -3,
    "with_owner": -2,
    "at_night": 3,
    "puppy": -5,
}
