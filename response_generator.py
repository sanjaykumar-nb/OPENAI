import openai

class ResponseGenerator:
    def __init__(self):
        self.counter_narrative_prompt = """
You are a crisis communication expert. Generate a factual counter-narrative to address this misinformation:

Original misinformation: "{text}"
Analysis: {analysis}

Create a clear, factual response that:
1. Addresses the false claims directly
2. Provides accurate information
3. Uses credible sources when possible
4. Maintains a calm, authoritative tone
5. Is under 200 words

Response:
"""

        self.alert_message_prompt = """
Generate an urgent alert message for emergency responders about this crisis:

Content: "{text}"
Crisis Level: {crisis_level}/10

Create a brief alert (under 100 words) that includes:
1. Nature of the misinformation threat
2. Potential impact on public safety
3. Recommended immediate actions

Alert:
"""

    def generate_counter_narrative(self, text, analysis):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{
                    "role": "user",
                    "content": self.counter_narrative_prompt.format(
                        text=text,
                        analysis=str(analysis)
                    )
                }],
                temperature=0.3,
                max_tokens=250
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Unable to generate counter-narrative. Error: {str(e)}"

    def generate_alert_message(self, text, crisis_level):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{
                    "role": "user",
                    "content": self.alert_message_prompt.format(
                        text=text,
                        crisis_level=crisis_level
                    )
                }],
                temperature=0.2,
                max_tokens=150
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Unable to generate alert. Error: {str(e)}"
