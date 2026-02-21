# src/chatbot/templates.py
"""
Templates and synonyms for generating training data.
"""

METRIC_SYNONYMS = {
    'recovery_score': [
        'recovery', 'recovery score', 'recovery index',
        'recovery level', 'readiness', 'recovery rating'
    ],
    'movement_score': [
        'movement', 'movement score', 'movement index',
        'activity score', 'daily movement'
    ],
    'sleep_score': [
        'sleep', 'sleep score', 'sleep quality',
        'sleep rating', 'sleep performance'
    ],
    'total_sleep_min': [
        'total sleep', 'sleep time', 'sleep duration',
        'hours slept', 'sleep length', 'time asleep'
    ],
    'sleep_efficiency': [
        'sleep efficiency', 'efficiency',
        'sleep quality percentage'
    ],
    'deep_sleep_min': [
        'deep sleep', 'deep sleep minutes',
        'deep sleep duration'
    ],
    'rem_sleep_min': [
        'rem sleep', 'rem', 'rem duration'
    ],
    'light_sleep_min': [
        'light sleep', 'light sleep minutes'
    ],
    'avg_temperature': [
        'temperature', 'skin temperature',
        'body temperature', 'avg temp'
    ],
    'total_steps': [
        'steps', 'step count', 'steps taken',
        'daily steps', 'how many steps'
    ],
    'hrv_avg': [
        'hrv', 'heart rate variability',
        'hrv average'
    ],
    'rhr_avg': [
        'resting heart rate', 'rhr',
        'resting hr', 'night rhr'
    ],
    'active_minutes': [
        'active minutes', 'activity minutes',
        'active time', 'exercise time'
    ],
    'vo2_max': [
        'vo2 max', 'vo2',
        'cardio fitness', 'fitness level'
    ],
}

TIME_RANGES = [
    'last 3 days',
    'last 5 days',
    'last week',
    'last 2 weeks',
    'last month',
    'this week',
    'this month',
    'past week',
    'past 10 days',
    'previous 7 days',
    'last 30 days',
    'this year',
    'yesterday',
    'today',
    'last night',
    'this morning',
    'the past few days',
    'the last couple of weeks',
    'over the weekend',
    '2 days ago',
    '3 weeks ago',
]

COMPARE_PAIRS = [
    ('today', 'yesterday'),
    ('this week', 'last week'),
    ('this month', 'last month'),
    ('Monday', 'Tuesday'),
    ('last 7 days', 'previous 7 days'),
    ('last week', 'the week before'),
    ('this week', 'the previous week'),
]

TEMPLATES = {
    'get_current': [
        # Standard questions
        "What is my {metric} today?",
        "What’s my {metric} right now?",
        "How is my {metric}?",
        "How is my {metric} doing today?",
        "What is my current {metric}?",
        "Tell me my {metric}",
        "Show me today's {metric}",
        "Give me my {metric} for today",
        "Is my {metric} good today?",
        "Did I do well on {metric} today?",
        "What is the value of {metric} today?",
        "Can you check my {metric}?",
        "Do you have my {metric} for today?",

        # Command style
        "Check my {metric}",
        "Get my {metric}",
        "Pull up my {metric}",
        "Open {metric}",
        "Display {metric}",
        "Fetch {metric}",
        "Load my {metric}",
        "View {metric}",
        "Show current {metric}",

        # Fragment style
        "{metric} today",
        "{metric} now",
        "current {metric}",
        "{metric} status",
        "{metric} value?",
        "today {metric}",
        "my {metric}",
        "{metric} update",
        "{metric} stats",
        "how {metric} today",

        # Casual
        "How’s my {metric} looking?",
        "Is my {metric} okay?",
        "Is {metric} bad today?",
    ],

    'get_history': [
        # Standard
        "How was my {metric} {time_range}?",
        "What was my {metric} over {time_range}?",
        "Show my {metric} for {time_range}",
        "Give me {metric} data for {time_range}",
        "Tell me my {metric} during {time_range}",
        "What happened to my {metric} {time_range}?",
        "How did my {metric} perform {time_range}?",
        "What values did {metric} have {time_range}?",
        "Can I see my {metric} {time_range}?",
        "During {time_range}, what was my {metric}?",
        "Show history of {metric} for {time_range}",

        # Trend focused
        "Did my {metric} improve {time_range}?",
        "Did my {metric} decline {time_range}?",
        "Was my {metric} stable {time_range}?",
        "Show trend of {metric} {time_range}",
        "Graph {metric} {time_range}",
        "Analyze my {metric} {time_range}",
        "Summary of {metric} {time_range}",
        "Average {metric} {time_range}",
        "How did my {metric} change {time_range}?",

        # Fragment
        "{metric} last week",
        "{metric} last month",
        "{metric} yesterday",
        "{metric} past 7 days",
        "{time_range} {metric}",
        "{metric} history",
        "{metric} over {time_range}",
        "stats for {metric} {time_range}",

        # Casual
        "How’s my {metric} been {time_range}?",
        "Was {metric} good {time_range}?",
        "Any change in {metric} {time_range}?",
    ],

    'compare': [
        # Standard
        "Compare my {metric} {time1} vs {time2}",
        "How does my {metric} compare between {time1} and {time2}?",
        "What’s the difference in {metric} between {time1} and {time2}?",
        "Is my {metric} better {time1} or {time2}?",
        "Which had higher {metric}, {time1} or {time2}?",
        "Show {metric} comparison for {time1} and {time2}",
        "How much did {metric} change from {time2} to {time1}?",
        "Did {metric} improve from {time2} to {time1}?",
        "Difference in {metric}: {time1} vs {time2}",
        "Analyze {metric} {time1} against {time2}",

        # Command style
        "Compare {metric} {time1} {time2}",
        "{metric} {time1} vs {time2}",
        "{time1} vs {time2} {metric}",
        "{metric} difference {time1} {time2}",
        "check {metric} {time1} and {time2}",
        "show {metric} {time1} {time2}",

        # Fragment / messy
        "today vs yesterday {metric}",
        "{metric} today yesterday",
        "{metric} this week last week",
        "{metric} difference today yesterday",
    ],

    'advice': [
        # Why
        "Why is my {metric} low?",
        "Why did my {metric} drop?",
        "Why has my {metric} decreased?",
        "What caused my {metric} to go down?",
        "Why is my {metric} worse than usual?",
        "{metric} low why?",
        "why {metric} bad",
        "Why is {metric} bad today?",
        "Why has my {metric} been declining?",
        "What affects my {metric} negatively?",

        # Improve
        "How can I improve my {metric}?",
        "How do I increase my {metric}?",
        "Tips to improve {metric}",
        "Ways to boost {metric}",
        "What helps increase {metric}?",
        "How to optimize {metric}?",
        "Improve {metric}",
        "boost {metric}",
        "How can I make my {metric} better?",
        "How to get higher {metric}?",

        # General fitness queries
        "Should I train today?",
        "Do I need rest?",
        "What workout should I do?",
        "What should I eat today?",
        "Any recovery advice?",
        "Is today a rest day?",
        "What activity do you suggest?",
        "Give me health tips",
        "How is my overall performance?",
        "Am I improving overall?",
    ]
}