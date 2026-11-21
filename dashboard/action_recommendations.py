
def get_action_recommendations(risk_level):

    recommendations = {
        "Low": {
            "priority": "Routine",
            "team": "Ward Monitoring Team",
            "timeframe": "Regular monitoring",
            "actions": [
                "Continue routine mosquito breeding site inspections.",
                "Monitor stagnant water in drains and containers.",
                "Continue community awareness campaigns."
            ]
        },

        "Medium": {
            "priority": "Moderate",
            "team": "Ward Inspection Team",
            "timeframe": "Within 3 days",
            "actions": [
                "Inspect potential mosquito breeding sites.",
                "Identify areas with stagnant water.",
                "Arrange targeted community awareness activities."
            ]
        },

        "High": {
            "priority": "High",
            "team": "Vector Control Team",
            "timeframe": "Within 24–48 hours",
            "actions": [
                "Prioritize drain cleaning and stagnant water removal.",
                "Inspect and treat identified breeding sites.",
                "Conduct targeted larval surveillance."
            ]
        },

        "Critical": {
            "priority": "Emergency",
            "team": "Emergency Vector Control Team",
            "timeframe": "Immediate coordination",
            "actions": [
                "Coordinate urgent vector-control activities.",
                "Prioritize high-risk breeding sites for inspection and treatment.",
                "Notify local health facilities for preparedness.",
                "Increase ward-level surveillance and monitoring."
            ]
        }
    }

    return recommendations.get(risk_level)
