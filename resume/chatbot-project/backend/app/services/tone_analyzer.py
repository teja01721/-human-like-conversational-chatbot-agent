import asyncio
import re
from typing import Dict, List, Any
from textblob import TextBlob
from app.services.ai_client import AIClient

class ToneAnalyzer:
    def __init__(self):
        self.ai_client = AIClient()
        
        # Predefined emotion patterns
        self.emotion_patterns = {
            "joy": ["happy", "excited", "great", "awesome", "wonderful", "amazing", "love", "fantastic"],
            "sadness": ["sad", "depressed", "down", "upset", "disappointed", "hurt", "crying"],
            "anger": ["angry", "mad", "furious", "annoyed", "frustrated", "irritated", "hate"],
            "fear": ["scared", "afraid", "worried", "anxious", "nervous", "terrified", "panic"],
            "surprise": ["wow", "amazing", "incredible", "unbelievable", "shocking", "unexpected"],
            "disgust": ["disgusting", "gross", "awful", "terrible", "horrible", "nasty"]
        }
        
        self.formality_indicators = {
            "formal": ["please", "thank you", "would you", "could you", "I would like", "I appreciate"],
            "casual": ["hey", "hi", "yeah", "cool", "awesome", "lol", "omg", "btw", "gonna", "wanna"]
        }
    
    async def analyze_tone(self, text: str) -> Dict[str, Any]:
        """Comprehensive tone analysis of user input"""
        
        # Basic sentiment analysis
        blob = TextBlob(text)
        sentiment_polarity = blob.sentiment.polarity
        sentiment_subjectivity = blob.sentiment.subjectivity
        
        # Emotion detection
        emotions = self._detect_emotions(text)
        
        # Formality analysis
        formality = self._analyze_formality(text)
        
        # Urgency detection
        urgency = self._detect_urgency(text)
        
        # Primary tone determination
        primary_tone = self._determine_primary_tone(sentiment_polarity, emotions, formality)
        
        # Confidence calculation
        confidence = self._calculate_confidence(emotions, sentiment_subjectivity)
        
        return {
            "primary_tone": primary_tone,
            "confidence": confidence,
            "emotions": emotions,
            "formality_level": formality,
            "urgency": urgency,
            "sentiment_polarity": sentiment_polarity,
            "sentiment_subjectivity": sentiment_subjectivity,
            "text_length": len(text),
            "question_count": text.count("?"),
            "exclamation_count": text.count("!")
        }
    
    def _detect_emotions(self, text: str) -> Dict[str, float]:
        """Detect emotions using pattern matching"""
        text_lower = text.lower()
        emotions = {}
        
        for emotion, patterns in self.emotion_patterns.items():
            score = 0.0
            for pattern in patterns:
                if pattern in text_lower:
                    score += 0.2
            
            # Boost score for multiple occurrences
            word_count = sum(1 for word in text_lower.split() if word in patterns)
            score = min(1.0, score + (word_count * 0.1))
            
            emotions[emotion] = score
        
        # Normalize emotions
        total_score = sum(emotions.values())
        if total_score > 0:
            emotions = {k: v / total_score for k, v in emotions.items()}
        else:
            # Default neutral emotions
            emotions = {emotion: 1.0/len(self.emotion_patterns) for emotion in self.emotion_patterns}
        
        return emotions
    
    def _analyze_formality(self, text: str) -> str:
        """Analyze formality level of text"""
        text_lower = text.lower()
        
        formal_score = 0
        casual_score = 0
        
        for indicator in self.formality_indicators["formal"]:
            if indicator in text_lower:
                formal_score += 1
        
        for indicator in self.formality_indicators["casual"]:
            if indicator in text_lower:
                casual_score += 1
        
        # Additional formality indicators
        if len([word for word in text.split() if len(word) > 6]) > len(text.split()) * 0.3:
            formal_score += 1  # Long words indicate formality
        
        if text.count(".") > text.count("!") + text.count("?"):
            formal_score += 0.5  # More periods than exclamations/questions
        
        if casual_score > formal_score * 1.5:
            return "casual"
        elif formal_score > casual_score * 1.5:
            return "formal"
        else:
            return "neutral"
    
    def _detect_urgency(self, text: str) -> float:
        """Detect urgency level in text"""
        urgency_indicators = [
            "urgent", "asap", "immediately", "now", "quickly", "fast", 
            "emergency", "help", "please help", "right away", "soon"
        ]
        
        text_lower = text.lower()
        urgency_score = 0.0
        
        for indicator in urgency_indicators:
            if indicator in text_lower:
                urgency_score += 0.2
        
        # Boost for multiple exclamation marks
        exclamation_count = text.count("!")
        if exclamation_count > 1:
            urgency_score += min(0.3, exclamation_count * 0.1)
        
        # Boost for all caps words
        caps_words = [word for word in text.split() if word.isupper() and len(word) > 2]
        urgency_score += min(0.2, len(caps_words) * 0.05)
        
        return min(1.0, urgency_score)
    
    def _determine_primary_tone(
        self, 
        sentiment_polarity: float, 
        emotions: Dict[str, float], 
        formality: str
    ) -> str:
        """Determine the primary tone of the message"""
        
        # Find dominant emotion
        dominant_emotion = max(emotions.items(), key=lambda x: x[1])
        
        # Map emotions to tones
        if dominant_emotion[1] > 0.3:  # Strong emotion detected
            if dominant_emotion[0] == "joy":
                return "happy" if formality == "casual" else "pleased"
            elif dominant_emotion[0] == "sadness":
                return "sad"
            elif dominant_emotion[0] == "anger":
                return "frustrated"
            elif dominant_emotion[0] == "fear":
                return "worried"
            elif dominant_emotion[0] == "surprise":
                return "surprised"
        
        # Fall back to sentiment analysis
        if sentiment_polarity > 0.3:
            return "positive"
        elif sentiment_polarity < -0.3:
            return "negative"
        else:
            return "neutral"
    
    def _calculate_confidence(self, emotions: Dict[str, float], subjectivity: float) -> float:
        """Calculate confidence in tone analysis"""
        
        # Higher confidence if there's a clear dominant emotion
        max_emotion_score = max(emotions.values())
        emotion_confidence = max_emotion_score * 2  # Scale to 0-2 range
        
        # Higher confidence for more subjective text
        subjectivity_confidence = subjectivity
        
        # Combine and normalize
        total_confidence = (emotion_confidence + subjectivity_confidence) / 2
        return min(1.0, max(0.1, total_confidence))
    
    async def analyze_conversation_tone_shift(
        self, 
        previous_messages: List[str], 
        current_message: str
    ) -> Dict[str, Any]:
        """Analyze how tone has shifted in conversation"""
        
        if not previous_messages:
            current_analysis = await self.analyze_tone(current_message)
            return {
                "current_tone": current_analysis,
                "tone_shift": "none",
                "shift_magnitude": 0.0,
                "conversation_trend": "stable"
            }
        
        # Analyze recent messages
        recent_analyses = []
        for msg in previous_messages[-3:]:  # Last 3 messages
            analysis = await self.analyze_tone(msg)
            recent_analyses.append(analysis)
        
        current_analysis = await self.analyze_tone(current_message)
        
        # Calculate tone shift
        if recent_analyses:
            prev_sentiment = recent_analyses[-1]["sentiment_polarity"]
            current_sentiment = current_analysis["sentiment_polarity"]
            
            shift_magnitude = abs(current_sentiment - prev_sentiment)
            
            if shift_magnitude > 0.4:
                if current_sentiment > prev_sentiment:
                    tone_shift = "positive_shift"
                else:
                    tone_shift = "negative_shift"
            else:
                tone_shift = "stable"
        else:
            tone_shift = "none"
            shift_magnitude = 0.0
        
        # Determine conversation trend
        if len(recent_analyses) >= 2:
            sentiments = [a["sentiment_polarity"] for a in recent_analyses]
            if all(s1 <= s2 for s1, s2 in zip(sentiments, sentiments[1:])):
                trend = "improving"
            elif all(s1 >= s2 for s1, s2 in zip(sentiments, sentiments[1:])):
                trend = "declining"
            else:
                trend = "variable"
        else:
            trend = "stable"
        
        return {
            "current_tone": current_analysis,
            "tone_shift": tone_shift,
            "shift_magnitude": shift_magnitude,
            "conversation_trend": trend,
            "previous_analyses": recent_analyses
        }
