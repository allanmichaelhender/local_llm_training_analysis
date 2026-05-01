import os
import requests


class LLMService:
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

    def generate_summary(self, garmin_data: dict, user_feedback: str) -> str:
        prompt = self._build_prompt(garmin_data, user_feedback)

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

    def _build_prompt(self, garmin_data: dict, user_feedback: str) -> str:
        return f"""You are a concise fitness coach. Analyze this workout and provide a 2-3 sentence summary.

WORKOUT DATA:
- Type: {garmin_data.get("type")}
- Duration: {garmin_data.get("duration_minutes", 0):.1f} minutes
- Distance: {garmin_data.get("distance_km", 0):.2f} km
- Avg Heart Rate: {garmin_data.get("avg_hr")} bpm
- Max Heart Rate: {garmin_data.get("max_hr")} bpm
- Calories: {garmin_data.get("calories")}

ATHLETE FEEDBACK:
{user_feedback}

Provide a brief summary that:
1. Acknowledges the effort level based on HR data
2. Comments on the workout relative to the athlete's feedback
3. Gives one actionable tip for next time

Keep it under 100 words."""
