#!/usr/bin/env python
"""
Terminal-based chat loop for AI Health Coach.
Loads intent classifier, vectorizer, and handles user queries.
"""

import os
import sys

import joblib
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from src.chatbot.entity_extractor import extract_metric, extract_time_range
from src.chatbot.response_generator import generate_response

# Initialize rich console
console = Console()


def load_classifier():
    """Load trained vectorizer and intent classifier."""
    vectorizer_path = os.path.join('models', 'vectorizer.pkl')
    classifier_path = os.path.join('models', 'intent_classifier.pkl')

    if not os.path.exists(vectorizer_path) or not os.path.exists(classifier_path):
        console.print("[red]Error: Model files not found. Please run train_intent_classifier.py first.[/red]")
        sys.exit(1)

    vectorizer = joblib.load(vectorizer_path)
    classifier = joblib.load(classifier_path)
    return vectorizer, classifier


def predict_intent(vectorizer, classifier, query: str) -> str:
    """Predict intent of the query."""
    query_vec = vectorizer.transform([query])
    intent = classifier.predict(query_vec)[0]
    return intent


def main():
    console.print(Panel.fit(
        "[bold cyan]AI Health Coach[/bold cyan]\n"
        "Ask me about your Ultrahuman data! Type 'quit' or 'exit' to stop.",
        border_style="green"
    ))

    # Load classifier
    vectorizer, classifier = load_classifier()

    while True:
        try:
            query = Prompt.ask("[bold yellow]You[/bold yellow]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[bold red]Goodbye![/bold red]")
            break

        if query.lower() in ['quit', 'exit', 'bye']:
            console.print("[bold red]Goodbye![/bold red]")
            break

        if not query.strip():
            continue

        # Process query
        with console.status("[bold green]Thinking...[/bold green]"):
            # Predict intent
            intent = predict_intent(vectorizer, classifier, query)

            # Extract entities
            metric = extract_metric(query)
            time_info = extract_time_range(query)

            # Generate response
            response = generate_response(intent, metric, time_info, query)

        # Display response
        console.print(Panel(
            response,
            title=f"[bold blue]{intent.replace('_', ' ').title()}[/bold blue]",
            border_style="blue",
            width=80
        ))


if __name__ == "__main__":
    main()
