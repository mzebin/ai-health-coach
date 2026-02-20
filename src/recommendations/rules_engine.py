from typing import Dict, Optional, Tuple


class RecommendationEngine:
    """
    Provides workout and diet recommendations based on recovery score and other metrics.
    """

    # Thresholds for recovery score categories
    RECOVERY_THRESHOLDS = {
        'low': 40,
        'medium': 60,
        'good': 80,
        'excellent': 100  # anything above 80 is excellent
    }

    def __init__(self):
        pass

    def categorize_recovery(self, recovery_score: Optional[float]) -> str:
        """
        Categorize recovery score into low, medium, good, excellent.
        If score is None, return 'unknown'.
        """
        if recovery_score is None:
            return 'unknown'
        if recovery_score < self.RECOVERY_THRESHOLDS['low']:
            return 'low'
        elif recovery_score < self.RECOVERY_THRESHOLDS['medium']:
            return 'medium'
        elif recovery_score < self.RECOVERY_THRESHOLDS['good']:
            return 'good'
        else:
            return 'excellent'

    def suggest_workout(self, recovery_score: Optional[float], metrics: Dict = None) -> str:
        """
        Suggest a workout based on recovery category and optionally other metrics.
        """
        category = self.categorize_recovery(recovery_score)

        if category == 'low':
            return ("Your recovery is low. Consider taking a rest day or doing light activities like "
                    "walking, stretching, or yoga. Focus on recovery and sleep.")
        elif category == 'medium':
            return ("Your recovery is moderate. A moderate workout like a steady run, bike ride, "
                    "or strength training is fine, but avoid pushing too hard. Listen to your body.")
        elif category == 'good':
            return ("Your recovery is good. You can engage in a more intense workout today, such as "
                    "HIIT, heavy strength training, or a long run. Stay hydrated and warm up properly.")
        elif category == 'excellent':
            return ("Your recovery is excellent! This is a great day to challenge yourself with high-intensity "
                    "training, personal best attempts, or a new workout routine. Go for it!")
        else:
            return ("Unable to determine recovery status. Please check your latest metrics. "
                    "In the meantime, a balanced workout is recommended.")

    def suggest_diet(self, recovery_score: Optional[float], metrics: Dict = None) -> str:
        """
        Suggest diet recommendations based on recovery category and optionally other metrics.
        """
        category = self.categorize_recovery(recovery_score)

        if category == 'low':
            return ("Focus on anti-inflammatory foods: berries, fatty fish, nuts, and leafy greens. "
                    "Ensure adequate protein intake to support muscle repair, and stay well hydrated. "
                    "Consider increasing your intake of complex carbs for energy.")
        elif category == 'medium':
            return ("Maintain a balanced diet with lean proteins, healthy fats, and complex carbs. "
                    "Include plenty of vegetables and fruits. Hydration is key; aim for 2-3 liters of water.")
        elif category == 'good':
            return ("You're recovering well. Keep up with a balanced diet rich in whole foods. "
                    "You might benefit from a slightly higher carb intake to fuel your workouts. "
                    "Don't forget post-workout nutrition: protein and carbs within 30-60 minutes.")
        elif category == 'excellent':
            return ("Your recovery is optimal. Continue with your current nutrition plan. "
                    "Consider timing your meals to maximize performance. Hydrate well and listen to your body.")
        else:
            return ("A balanced diet with plenty of whole foods, lean protein, healthy fats, and "
                    "complex carbs is always a good choice. Stay hydrated.")

    def get_advice(self, recovery_score: Optional[float], metrics: Dict = None) -> Tuple[str, str]:
        """
        Return both workout and diet advice as a tuple.
        """
        workout = self.suggest_workout(recovery_score, metrics)
        diet = self.suggest_diet(recovery_score, metrics)
        return workout, diet


# Example usage
# if __name__ == "__main__":
#     engine = RecommendationEngine()
#     # Test with various scores
#     for score in [None, 35, 55, 75, 95]:
#         workout, diet = engine.get_advice(score)
#         print(f"Recovery score: {score}")
#         print(f"Workout: {workout}")
#         print(f"Diet: {diet}\n")
