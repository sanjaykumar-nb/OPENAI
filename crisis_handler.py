import openai

class CrisisHandler:
    def __init__(self):
        self.crisis_assessment_prompt = """
You are a crisis communication expert. Assess the crisis level of this content:

Content: "{text}"
Misinformation Analysis: {analysis}

Rate the crisis level from 1-10 where:
- 1-3: Low risk (normal misinformation)
- 4-6: Medium risk (spreading false information)  
- 7-8: High risk (potential public harm)
- 9-10: Critical (immediate danger to public safety)

Consider factors:
- Urgency of language
- Potential for public harm
- Credibility appearance
- Spread potential

Respond with just the number (1-10).
"""

    def assess_crisis(self, text, detection_result):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{
                    "role": "user",
                    "content": self.crisis_assessment_prompt.format(
                        text=text,
                        analysis=str(detection_result)
                    )
                }],
                temperature=0.1,
                max_tokens=10
            )
            crisis_level = int(response.choices[0].message.content.strip())
            return max(1, min(10, crisis_level))
        except:
            return self._fallback_crisis_assessment(text, detection_result)

    def _fallback_crisis_assessment(self, text, detection_result):
        base_score = 3 if detection_result['is_misinformation'] else 1
        urgent_words = ['urgent', 'emergency', 'immediately', 'breaking', 'warning']
        urgency_boost = sum(2 for word in urgent_words if word.lower() in text.lower())
        confidence_boost = detection_result['confidence'] // 20
        return min(10, base_score + urgency_boost + confidence_boost)
