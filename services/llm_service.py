import os
import requests


class LLMService:
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

    def generate_summary(self, workout_data: dict, user_feedback: str) -> str:
        prompt = self._build_prompt(workout_data, user_feedback)

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.7, "num_predict": 300},
                },
                timeout=60,
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "No summary generated")
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            return f"Error generating summary: {e}"

    def _build_prompt(self, workout_data: dict, user_feedback: str) -> str:
        return f"""<system>
You are a concise fitness coach. Analyze this workout and provide a 2-3 sentence summary.
</system>

<workout>
    <type>{workout_data.get("type")}</type>
    <duration>{workout_data.get("duration_minutes", 0):.1f} minutes</duration>
    <distance>{workout_data.get("distance_km", 0):.2f} km</distance>
    <avg_hr>{workout_data.get("avg_hr")} bpm</avg_hr>
    <max_hr>{workout_data.get("max_hr")} bpm</max_hr>
    <calories>{workout_data.get("calories")}</calories>
</workout>

<feedback>
{user_feedback}
</feedback>

<instructions>
    <requirement>Acknowledge the effort level based on HR data</requirement>
    <requirement>Comment on the workout relative to the athlete's feedback</requirement>
    <requirement>Give one actionable tip for next time</requirement>
    <length>Keep it under 100 words</length>
</instructions>"""
