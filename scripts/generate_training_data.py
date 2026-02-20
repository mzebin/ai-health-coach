#!/usr/bin/env python
"""
Generate synthetic training data for intent classification using templates.
Output: data/intent_training.csv
"""

import csv
import os
import random
import sys

# Add project root to path to import templates
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.chatbot.templates import (
    METRIC_SYNONYMS,
    TIME_RANGES,
    COMPARE_PAIRS,
    TEMPLATES
)

INTENTS = list(TEMPLATES.keys())


def generate_queries_for_intent(intent, num_samples=150):
    queries = []
    templates = TEMPLATES[intent]

    for _ in range(num_samples):
        template = random.choice(templates)

        # For advice templates that might have {metric} placeholder
        if '{metric}' in template:
            metric_key = random.choice(list(METRIC_SYNONYMS.keys()))
            metric_phrase = random.choice(METRIC_SYNONYMS[metric_key])
            template = template.replace('{metric}', metric_phrase)

        if '{time_range}' in template:
            time_range = random.choice(TIME_RANGES)
            template = template.replace('{time_range}', time_range)

        if '{time1}' in template and '{time2}' in template:
            time1, time2 = random.choice(COMPARE_PAIRS)
            template = template.replace('{time1}', time1).replace('{time2}', time2)

        queries.append(template)

    return queries


def main():
    random.seed(42)  # for reproducibility
    num_per_intent = 200  # increase to get more variety

    all_queries = []
    for intent in INTENTS:
        queries = generate_queries_for_intent(intent, num_per_intent)
        for q in queries:
            all_queries.append((q, intent))

    # Shuffle
    random.shuffle(all_queries)

    # Ensure output directory exists
    os.makedirs('data', exist_ok=True)

    # Write CSV
    with open('data/intent_training.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['query', 'intent'])
        writer.writerows(all_queries)

    print(f"Generated {len(all_queries)} training examples.")
    print("Sample:")
    for q, i in all_queries[:10]:
        print(f"  [{i}] {q}")


if __name__ == '__main__':
    main()