"""Entry point for the AR Sports Coach application."""

import json

from integration.pipeline import process_metrics


def main() -> None:
    """Run a sample through the coaching pipeline."""
    sample_metrics = {
        "knee_angle": 90.0,
        "reps": 0,
        "state": "standing",
    }

    result = process_metrics(sample_metrics)

    print("=== AR Sports Coach ===")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
