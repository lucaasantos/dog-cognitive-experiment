# Dog Cognitive Experiment

Dog Cognitive Experiment is an adaptive cognitive system built with Python and Tkinter. It simulates memory-based adaptation by processing simple dog-related experiences, updating a persistent belief state, and showing how fear, confidence, context, and recent experience affect the system's current assessment.

This is not AGI and it is not conscious AI. It is a small cognitive architecture experiment focused on transparent rules, persistent memory, and behavioral simulation.

## Features

- Interactive Tkinter desktop interface
- Persistent JSON memory
- Rule-based event, breed, and context detection
- Emotional impact scoring
- Gradual emotional decay over time
- Belief confidence modeling
- Recent-history visualization
- Simple cognitive reflection messages
- No database, no LLM, and no web framework

## Concepts Explored

- Adaptive behavior
- Belief systems
- Memory-based adaptation
- Confidence modeling
- Contextual interpretation
- Behavioral simulation
- Cognitive architecture prototyping

## Tech Stack

- Python 3
- Tkinter
- JSON

Tkinter is included with most standard Python installations. The project has no external runtime dependencies.

## Project Structure

```text
dog_experiment/
├── assets/
│   └── .gitkeep
├── screenshots/
│   └── .gitkeep
├── evaluator.py
├── LICENSE
├── main.py
├── memory.json
├── README.md
├── requirements.txt
├── rules.py
└── ui.py
```

## Installation

Clone the repository:

```bash
git clone https://github.com/your-username/dog-cognitive-experiment.git
cd dog-cognitive-experiment
```

Optional: create and activate a virtual environment.

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Running

Start the application:

```bash
python main.py
```

On Windows, if `python` is not available but the Python launcher is installed:

```bash
py -B main.py
```

## How It Works

The application reads a user experience such as:

```text
Today a pitbull barked aggressively while alone.
```

It then:

1. Normalizes the text
2. Detects weighted events
3. Detects breed multipliers
4. Detects contextual modifiers
5. Calculates emotional impact
6. Applies emotional decay
7. Updates persistent memory
8. Recomputes the current assessment
9. Generates a cognitive reflection

Impact is calculated as:

```text
(event weights + context modifiers) * breed multiplier
```

## Screenshots

Add interface screenshots to the `screenshots/` folder.

```md
![Main interface](screenshots/main-interface.png)
```

## Future Improvements

- Local LLM integration
- Embeddings
- Semantic similarity
- Vector memory
- Goal modeling
- Autonomous-agent experiments
- Advanced generalization between breeds
- Continuous learning
- Semantic context classification
- Richer memory visualization

## License

This project is released under the MIT License. See [LICENSE](LICENSE).
