#!/usr/bin/env python
"""
Terminal-based chat loop for AI Health Coach.
Loads intent classifier, vectorizer, and handles user queries.
"""

import os
import sys
from datetime import datetime, timedelta

import joblib
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from src.chatbot.entity_extractor import extract_metric, extract_time_range, resolve_time_range
from src.chatbot.llm_client import OllamaClient
from src.chatbot.response_generator import generate_response
from src.data.cache import get_latest_metrics
from src.data.fetcher import fetch_recent_days
from src.data.cache import fetch_metrics

# Chat history
chat_history = []
MAX_HISTORY = 50

# Initialize rich console
console = Console()


def clear_screen():
    """Clear terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_help():
    help_text = """
[bold cyan]Available commands:[/bold cyan]
  @ai          - To ask AI anything
  /clear       - Clear the screen
  /new_chat    - Clear screen and reset conversation history
  /update \[n]  - Fetch last n days of data (default: 7)
  /history     - Show recent chat history
  /metrics     - Show available metrics
  /help        - Show this help message
  /exit        - Exit the application (also 'quit' or 'exit')"""
    console.print(Panel(help_text, title="Help", border_style="cyan"))

def show_history():
    if not chat_history:
        console.print("[yellow]No chat history yet.[/yellow]")
        return
    history_text = ""
    for role, msg in chat_history[-10:]:  # show last 10 messages
        prefix = "[bold green]You:[/bold green]" if role == "user" else "[bold blue]Assistant:[/bold blue]"
        history_text += f"{prefix} {msg}\n"
    console.print(Panel(history_text, title="Recent Chat History", border_style="cyan"))


def show_metrics():
    metrics_desc = {
        'recovery_score': 'Recovery score (0-100) indicating how well you recovered',
        'movement_score': 'Movement score based on activity',
        'sleep_score': 'Overall sleep quality score',
        'total_sleep_min': 'Total sleep time in minutes',
        'sleep_efficiency': 'Sleep efficiency percentage',
        'deep_sleep_min': 'Deep sleep minutes',
        'rem_sleep_min': 'REM sleep minutes',
        'light_sleep_min': 'Light sleep minutes',
        'avg_temperature': 'Average skin temperature during sleep',
        'total_steps': 'Daily step count',
        'hrv_avg': 'Average heart rate variability',
        'rhr_avg': 'Resting heart rate',
        'active_minutes': 'Active minutes',
        'vo2_max': 'VO2 max estimate',
    }
    text = "\n".join([f"[bold]{k}[/bold]: {v}" for k, v in metrics_desc.items()])
    console.print(Panel(text, title="Available Metrics", border_style="cyan"))


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


def get_recent_history(history, n=5):
    """Return last n exchanges (each exchange = user+assistant)."""
    max_entries = n * 2
    return history[-max_entries:] if len(history) > max_entries else history


def ask_ai(query, llm_client, max_tokens=300):
    """Get AI response with latest metrics as context."""
    latest = get_latest_metrics()
    context = None
    if latest:
        context = f"Latest metrics: {dict(latest)}"
    recent = get_recent_history(chat_history, n=5) if chat_history else None
    return llm_client.generate(query, history=recent, context=context, max_tokens=max_tokens)


def generate_advice_with_ai(query, metric, time_range_info, llm_client):
    """Generate advice using AI, incorporating data from the specified time range."""
    today = datetime.today()
    # Resolve time range
    if time_range_info:
        try:
            start, end = resolve_time_range(time_range_info, today)
        except Exception:
            start, end = None, None
    else:
        # Default to last 7 days (excluding today)
        end = today - timedelta(days=1)
        start = end - timedelta(days=6)

    # Fetch data for the range
    rows = []
    if start and end:
        rows = fetch_metrics(start, end)

    # Summarize key metrics
    summary = ""
    if rows:
        rows_dict = [dict(row) for row in rows]
        # Metrics to summarize
        key_metrics = ['recovery_score', 'sleep_score', 'hrv_avg', 'rhr_avg', 'total_steps', 'active_minutes']
        values = {m: [] for m in key_metrics}
        for row in rows_dict:
            for m in key_metrics:
                val = row.get(m)
                if val is not None:
                    values[m].append(val)
        summary_parts = []
        for m in key_metrics:
            if values[m]:
                avg = sum(values[m]) / len(values[m])
                summary_parts.append(f"{m}: {avg:.1f} (avg over {len(values[m])} days)")
        if summary_parts:
            summary = "Based on your data:\n" + "\n".join(summary_parts)
        else:
            summary = "No recent data available for key metrics."
    else:
        summary = "No data available for the specified period."

    # Build the prompt
    if metric:
        prompt = f"The user asks about '{metric}': {query}\n\n{summary}\n\nProvide helpful advice related to their query and the data."
    else:
        prompt = f"{query}\n\n{summary}\n\nProvide helpful health advice based on the data."

    # Get recent history for context
    recent = get_recent_history(chat_history, n=5) if chat_history else None
    # Also include latest metrics as extra context
    from src.data.cache import get_latest_metrics
    latest = get_latest_metrics()
    context = None
    if latest:
        context = f"Latest metrics: {dict(latest)}"
    response = llm_client.generate(prompt, history=recent, context=context, max_tokens=500)
    return response


def main():
    global chat_history

    console.print(Panel.fit(
        "[bold cyan]AI Health Coach[/bold cyan]\n"
        "Ask me about your Ultrahuman data!\n"
        "• Normal questions: 'How was my sleep yesterday?'\n"
        "• [bold magenta]@ai[/bold magenta] prefix: ask anything using AI\n"
        "• Type [bold]/help[/bold] for available commands\n"
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

        # Check for commands
        if query.startswith('/'):
            cmd_parts = query.split()
            cmd = cmd_parts[0].lower()

            if cmd == '/clear':
                clear_screen()
                continue
            elif cmd == '/new_chat':
                clear_screen()
                chat_history.clear()
                console.print("[green]Started a new chat.[/green]")
                continue
            elif cmd == '/update':
                days = 7
                if len(cmd_parts) > 1:
                    try:
                        days = int(cmd_parts[1])
                    except ValueError:
                        console.print("[red]Invalid number of days. Using default 7.[/red]")
                with console.status(f"[bold green]Fetching last {days} days..."):
                    success, total = fetch_recent_days(days)
                console.print(f"[green]Fetched {success}/{total} days successfully.[/green]")
                continue
            elif cmd == '/history':
                show_history()
                continue
            elif cmd == '/metrics':
                show_metrics()
                continue
            elif cmd == '/help':
                print_help()
                continue
            elif cmd in ['/exit', '/quit']:
                console.print("[bold red]Goodbye![/bold red]")
                break
            else:
                console.print(f"[red]Unknown command: {cmd}. Type /help for available commands.[/red]")
                continue

        # Check for @ai prefix
        if query.lower().startswith(('@ai', '@ai ', '@ai?')):
            clean_query = query[4:].strip()
            if not clean_query:
                console.print("[yellow]Please ask a question after @ai[/yellow]")
                continue
            with console.status("[bold green]Consulting AI...[/bold green]"):
                response = ask_ai(clean_query, llm_client, max_tokens=300)

                # Track History
                chat_history.append(("user", query))
                chat_history.append(("assistant", response))

                # Trim if exceeds MAX_HISTORY
                if len(chat_history) > MAX_HISTORY * 2:
                    chat_history = chat_history[-(MAX_HISTORY * 2):]
            console.print(Panel(
                Markdown(response),
                title="[bold magenta]AI Assistant[/bold magenta]",
                border_style="magenta"
            ))
            continue

        # Process query
        with console.status("[bold green]Thinking...[/bold green]"):
            # Predict intent
            intent, confidence, proba = predict_intent_with_confidence(vectorizer, classifier, query)
            console.print(f"[dim]Predicted: {intent} with confidence {confidence:.2f}[/dim]")

            if intent is not None and intent != 'advice':
                # Extract entities
                metric = extract_metric(query)
                time_info = extract_time_range(query)

                # Generate response
                response = generate_response(intent, metric, time_info)

                # Track History
                chat_history.append(("user", query))
                chat_history.append(("assistant", response))

                # Trim if exceeds MAX_HISTORY
                if len(chat_history) > MAX_HISTORY * 2:
                    chat_history = chat_history[-(MAX_HISTORY * 2):]

                console.print(Panel(
                    Markdown(response),
                    title=f"[bold blue]{intent.replace('_', ' ').title()}[/bold blue]",
                    border_style="blue",
                ))
                continue

        with console.status("[bold green]Consulting AI...[/bold green]"):
            # Extract entities
            metric = extract_metric(query)
            time_info = extract_time_range(query)

            response = generate_advice_with_ai(query, metric, time_info, llm_client)

            # Track history
            chat_history.append(("user", query))
            chat_history.append(("assistant", response))

            if len(chat_history) > MAX_HISTORY * 2:
                chat_history = chat_history[-(MAX_HISTORY * 2):]

        # Display response
        console.print(Panel(
            Markdown(response),
            title="[bold magenta]AI Assistant[/bold magenta]",
            border_style="magenta"
        ))


if __name__ == "__main__":
    main()
