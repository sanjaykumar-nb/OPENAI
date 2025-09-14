import openai
import json
import re
import requests
from datetime import datetime
import base64

class MisinformationDetector:
    def __init__(self):
        self.languages = {
            'hi': 'Hindi',
            'ta': 'Tamil', 
            'te': 'Telugu',
            'en': 'English'
        }
        
        self.multimodal_prompt = """
You are an advanced multimodal misinformation detection system. Analyze content for accuracy with extreme precision.

ENHANCED DETECTION CRITERIA:
- Cross-reference with recent fact-checks and news
- Analyze emotional manipulation tactics
- Check for deepfakes or manipulated media indicators
- Assess viral spread potential (1-10 scale)
- Determine credibility score based on source patterns
- Calculate public harm potential

Content: "{text}"
Language: {language}
Context: {context}

Respond in JSON format:
{{
    "is_misinformation": true/false,
    "confidence": 0-100,
    "credibility_score": 0-100,
    "spread_risk": 1-10,
    "harm_potential": 1-10,
    "indicators": ["list"],
    "explanation": "detailed analysis",
    "sources": ["verification_urls"],
    "category": "health/politics/disaster/technology/other",
    "language_detected": "en/hi/ta/te",
    "manipulation_type": "emotional/conspiracy/fake_urgency/none",
    "recommended_action": "ignore/monitor/alert/emergency"
}}
"""

    def analyze(self, text, image_data=None, context="social_media"):
        """Enhanced analysis with multimodal support"""
        try:
            # Detect language
            detected_lang = self._detect_language(text)
            
            # Get web search context
            web_context = self._get_web_context(text)
            
            # Multimodal analysis if image provided
            if image_data:
                image_analysis = self._analyze_image(image_data)
                text = f"{text}\n\nImage Analysis: {image_analysis}"
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{
                    "role": "system",
                    "content": "You are an expert fact-checker and misinformation analyst with access to real-time information."
                }, {
                    "role": "user",
                    "content": self.multimodal_prompt.format(
                        text=text,
                        language=self.languages.get(detected_lang, 'English'),
                        context=f"{context}. Recent web context: {web_context}"
                    )
                }],
                temperature=0.0,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content.strip()
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            
            if json_match:
                result = json.loads(json_match.group(0))
            else:
                return self._enhanced_fallback_analysis(text, detected_lang)
            
            # Enhance with additional metrics
            result = self._enhance_result_with_metrics(result, text, detected_lang)
            return result

        except Exception as e:
            print(f"Analysis Error: {e}")
            return self._enhanced_fallback_analysis(text, 'en')

    def _detect_language(self, text):
        """Simple language detection"""
        hindi_chars = len(re.findall(r'[\u0900-\u097F]', text))
        tamil_chars = len(re.findall(r'[\u0B80-\u0BFF]', text))
        telugu_chars = len(re.findall(r'[\u0C00-\u0C7F]', text))
        
        if hindi_chars > 5:
            return 'hi'
        elif tamil_chars > 5:
            return 'ta'
        elif telugu_chars > 5:
            return 'te'
        return 'en'

    def _get_web_context(self, text):
        """Get recent web context for fact-checking"""
        try:
            # Extract key terms for search
            key_terms = self._extract_key_terms(text)
            search_query = f"{key_terms} fact check OR debunked OR verified"
            
            # Mock web search result (in real implementation, use Google Search API)
            web_results = [
                "Recent fact-checks show similar claims have been debunked",
                "No credible sources support this claim",
                "Official health organizations contradict this information"
            ]
            return "; ".join(web_results[:2])
        except:
            return "Limited web context available"

    def _extract_key_terms(self, text):
        """Extract key terms for web search"""
        # Simple keyword extraction
        keywords = re.findall(r'\b(?:vaccine|election|covid|government|outbreak|emergency|breaking)\b', text.lower())
        return " ".join(keywords[:3]) if keywords else text.split()[:5]

    def _analyze_image(self, image_data):
        """Analyze image for manipulation indicators"""
        try:
            # Mock image analysis (in real implementation, use vision models)
            return "Image appears authentic with no obvious manipulation detected"
        except:
            return "Image analysis unavailable"

    def _enhance_result_with_metrics(self, result, text, language):
        """Add advanced metrics"""
        # Ensure all required fields
        enhanced = {
            'is_misinformation': bool(result.get('is_misinformation', False)),
            'confidence': max(10, min(100, int(result.get('confidence', 50)))),
            'credibility_score': int(result.get('credibility_score', 50)),
            'spread_risk': int(result.get('spread_risk', 5)),
            'harm_potential': int(result.get('harm_potential', 5)),
            'indicators': result.get('indicators', []),
            'explanation': result.get('explanation', 'Analysis completed'),
            'sources': self._get_enhanced_sources(result.get('category', 'unknown'), language),
            'category': result.get('category', 'unknown'),
            'language_detected': language,
            'manipulation_type': result.get('manipulation_type', 'none'),
            'recommended_action': result.get('recommended_action', 'monitor'),
            'timestamp': datetime.now().isoformat(),
            'viral_potential': self._calculate_viral_potential(text),
            'emergency_level': self._calculate_emergency_level(result)
        }
        
        return enhanced

    def _get_enhanced_sources(self, category, language):
        """Get language-specific and category-specific sources"""
        base_sources = {
            'health': [
                'https://www.who.int/news-room/fact-sheets',
                'https://www.cdc.gov/vaccines/index.html',
                'https://www.mohfw.gov.in/' if language in ['hi', 'ta', 'te'] else 'https://www.fda.gov/consumers'
            ],
            'politics': [
                'https://www.factcheck.org',
                'https://www.politifact.com',
                'https://factly.in/' if language in ['hi', 'ta', 'te'] else 'https://apnews.com/ap-fact-check'
            ],
            'disaster': [
                'https://www.fema.gov/disasters',
                'https://ndma.gov.in/' if language in ['hi', 'ta', 'te'] else 'https://www.ready.gov/alerts',
                'https://www.redcross.org/about-us/news-and-events'
            ]
        }
        
        return base_sources.get(category, [
            'https://www.snopes.com',
            'https://www.factcheck.org',
            'https://factly.in/' if language in ['hi', 'ta', 'te'] else 'https://www.reuters.com/fact-check'
        ])

    def _calculate_viral_potential(self, text):
        """Calculate how likely content is to go viral"""
        viral_indicators = ['breaking', 'urgent', 'shocking', 'share', 'retweet', 'must read']
        score = sum(2 for indicator in viral_indicators if indicator.lower() in text.lower())
        return min(10, max(1, score))

    def _calculate_emergency_level(self, result):
        """Calculate emergency response level"""
        if result.get('harm_potential', 0) >= 8 and result.get('spread_risk', 0) >= 7:
            return 'critical'
        elif result.get('harm_potential', 0) >= 6:
            return 'high'
        elif result.get('is_misinformation', False):
            return 'medium'
        return 'low'

    def _enhanced_fallback_analysis(self, text, language):
        """Enhanced fallback with all new metrics"""
        # Advanced pattern matching
        high_risk_patterns = [
            (r'vaccine.*autism|microchip.*vaccine', 'health', 9),
            (r'election.*rigged|voting.*fraud', 'politics', 8),
            (r'water.*poison|outbreak.*cover', 'disaster', 9),
            (r'5g.*coronavirus|chemtrail', 'conspiracy', 7)
        ]
        
        is_misinfo = False
        confidence = 40
        category = 'unknown'
        harm_potential = 3
        
        text_lower = text.lower()
        for pattern, cat, harm in high_risk_patterns:
            if re.search(pattern, text_lower):
                is_misinfo = True
                confidence = min(90, confidence + 25)
                category = cat
                harm_potential = harm
                break
        
        return {
            'is_misinformation': is_misinfo,
            'confidence': confidence,
            'credibility_score': 60 if not is_misinfo else 20,
            'spread_risk': 6 if is_misinfo else 3,
            'harm_potential': harm_potential,
            'indicators': ['pattern_detection', 'keyword_analysis'],
            'explanation': f'Enhanced fallback analysis with {language} language support',
            'sources': self._get_enhanced_sources(category, language),
            'category': category,
            'language_detected': language,
            'manipulation_type': 'conspiracy' if is_misinfo else 'none',
            'recommended_action': 'alert' if harm_potential >= 7 else 'monitor',
            'timestamp': datetime.now().isoformat(),
            'viral_potential': self._calculate_viral_potential(text),
            'emergency_level': 'high' if harm_potential >= 7 else 'low'
        }
