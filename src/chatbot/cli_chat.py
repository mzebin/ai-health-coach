#!/usr/bin/env python
"""
Terminal-based chat loop for AI Health Coach.
Loads intent classifier, vectorizer, and handles user queries.
"""

import datetime
import os
import sys

import joblib
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from src.chatbot.entity_extractor import extract_metric, extract_time_range
from src.chatbot.llm_client import OllamaClient
from src.chatbot.response_generator import generate_response
from src.data.cache import get_latest_metrics

FALLBACK_LOG = 'data/fallback_queries.csv'
os.makedirs(os.path.dirname(FALLBACK_LOG), exist_ok=True)

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


def predict_intent_with_confidence(vectorizer, classifier, query: str, threshold=0.5):
    query_vec = vectorizer.transform([query])
    proba = classifier.predict_proba(query_vec)[0]
    max_prob = max(proba)
    if max_prob < threshold:
        return None, max_prob, None
    intent = classifier.classes_[proba.argmax()]
    return intent, max_prob, proba


def ask_ai(query, llm_client):
    """Get AI response with latest metrics as context."""
    from src.data.cache import get_latest_metrics
    latest = get_latest_metrics()
    context = None
    if latest:
        # Convert row to dict to avoid sqlite3.Row issues
        context = f"Latest metrics: {dict(latest)}"
    return llm_client.generate(query, context=context)


def main():
    console.print(Panel.fit(
        "[bold cyan]AI Health Coach[/bold cyan]\n"
        "Ask me about your Ultrahuman data!\n"
        "• Normal questions: 'How was my sleep yesterday?'\n"
        "• [bold magenta]@ai[/bold magenta] prefix: ask anything using AI, e.g., '@ai What trends do you see in my recovery?'\n"
        "• Type 'quit' or 'exit' to stop.",
        border_style="green"
    ))

    # Load classifier
    vectorizer, classifier = load_classifier()

    # Initial LLM client
    llm_client = OllamaClient()

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

        # Check for @ai prefix
        if query.lower().startswith(('@ai', '@ai ', '@ai?')):
            clean_query = query[4:].strip()
            if not clean_query:
                console.print("[yellow]Please ask a question after @ai[/yellow]")
                continue
            with console.status("[bold green]Consulting AI...[/bold green]"):
                response = ask_ai(clean_query, llm_client)
            console.print(Panel(
                response,
                title="[bold magenta]AI Assistant[/bold magenta]",
                border_style="magenta",
                width=80
            ))
            continue

        # Process query
        with console.status("[bold green]Thinking...[/bold green]"):
            # Predict intent
            intent, confidence, proba = predict_intent_with_confidence(vectorizer, classifier, query)
            console.print(f"[dim]Predicted: {intent} with confidence {confidence:.2f}[/dim]")

            if intent is None:
                # Log fallback query
                with open(FALLBACK_LOG, 'a') as f:
                    f.write(f"{datetime.datetime.now().isoformat()},{query},{confidence:.2f}\n")

                # Fallback to AI
                response = ask_ai(query, llm_client)
                console.print(Panel(
                    response,
                    title="[bold magenta]AI Assistant[/bold magenta]",
                    border_style="magenta",
                    width=80
                ))
                continue

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
