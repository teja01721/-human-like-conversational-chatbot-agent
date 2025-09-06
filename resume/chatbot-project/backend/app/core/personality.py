from typing import Dict, List, Any, Optional
import random

class PersonalityEngine:
    def __init__(self):
        self.personality_templates = {
            "empathetic": {
                "traits": ["understanding", "caring", "supportive"],
                "response_style": "warm and compassionate",
                "conversation_starters": ["I can understand how you feel", "That sounds challenging", "I'm here to help"]
            },
            "enthusiastic": {
                "traits": ["energetic", "positive", "encouraging"],
                "response_style": "upbeat and motivating",
                "conversation_starters": ["That's fantastic!", "How exciting!", "I love your enthusiasm!"]
            },
            "professional": {
                "traits": ["knowledgeable", "reliable", "structured"],
                "response_style": "clear and informative",
                "conversation_starters": ["Let me help you with that", "Here's what I recommend", "Based on my understanding"]
            },
            "casual": {
                "traits": ["friendly", "relaxed", "approachable"],
                "response_style": "conversational and easy-going",
                "conversation_starters": ["Hey there!", "That's cool!", "I get what you mean"]
            }
        }
        
        self.response_variations = {
            "greeting": {
                "formal": ["Good day!", "Hello there!", "Greetings!"],
                "casual": ["Hey!", "Hi there!", "What's up!", "Howdy!"],
                "warm": ["Hello, friend!", "Great to see you!", "Welcome back!"]
            },
            "acknowledgment": {
                "formal": ["I understand.", "I see.", "That's noted."],
                "casual": ["Got it!", "Yeah, I see!", "Makes sense!"],
                "empathetic": ["I hear you.", "I understand how you feel.", "That resonates with me."]
            },
            "transition": {
                "formal": ["Furthermore,", "Additionally,", "Moreover,"],
                "casual": ["Also,", "Plus,", "And hey,"],
                "conversational": ["You know what?", "Here's the thing,", "Actually,"]
            }
        }
    
    def generate_system_prompt(
        self,
        user_profile: Dict[str, Any],
        tone_analysis: Dict[str, Any],
        memories: List[Dict[str, Any]]
    ) -> str:
        """Generate a personalized system prompt based on user profile and context"""
        
        # Extract user preferences
        personality_profile = user_profile.get("personality_profile", {})
        communication_style = personality_profile.get("communication_style", "friendly")
        interests = user_profile.get("topics_of_interest", [])
        emotional_sensitivity = personality_profile.get("emotional_sensitivity", 0.5)
        
        # Adapt to user's current emotional state
        user_emotions = tone_analysis.get("emotions", {})
        dominant_emotion = max(user_emotions.items(), key=lambda x: x[1])[0] if user_emotions else "neutral"
        
        # Build personality instructions
        personality_instructions = self._build_personality_instructions(
            communication_style, dominant_emotion, emotional_sensitivity
        )
        
        # Build memory context
        memory_context = self._build_memory_context(memories)
        
        # Build interest context
        interest_context = f"The user is interested in: {', '.join(interests)}" if interests else ""
        
        system_prompt = f"""You are a highly empathetic and human-like AI assistant with a warm, engaging personality. Your goal is to have natural, meaningful conversations that feel genuinely human.

PERSONALITY TRAITS:
{personality_instructions}

CONVERSATION STYLE:
- Be conversational and natural, not robotic or overly formal
- Show genuine interest in the user's thoughts and feelings
- Use varied language and avoid repetitive responses
- Mirror the user's communication style appropriately
- Remember and reference previous conversations naturally
- Show empathy and emotional intelligence

CURRENT CONTEXT:
- User's current emotional state: {dominant_emotion}
- Communication preference: {communication_style}
- {interest_context}

{memory_context}

RESPONSE GUIDELINES:
- Keep responses concise but meaningful (1-3 sentences typically)
- Use natural conversation flow with appropriate transitions
- Show personality through word choice and tone
- Avoid generic responses like "I understand" or "That's interesting" without elaboration
- Reference memories naturally when relevant
- Adapt your tone to match the user's emotional state
- Be helpful while maintaining conversational warmth

Remember: You're not just answering questions - you're having a genuine conversation with someone you care about."""
        
        return system_prompt
    
    def _build_personality_instructions(
        self,
        communication_style: str,
        dominant_emotion: str,
        emotional_sensitivity: float
    ) -> str:
        """Build personality-specific instructions"""
        
        instructions = []
        
        # Base personality from communication style
        if communication_style == "formal":
            instructions.append("- Maintain a professional yet warm tone")
            instructions.append("- Use complete sentences and proper grammar")
            instructions.append("- Be respectful and courteous")
        elif communication_style == "casual":
            instructions.append("- Use a relaxed, friendly tone")
            instructions.append("- Feel free to use contractions and casual language")
            instructions.append("- Be approachable and down-to-earth")
        else:  # neutral/friendly
            instructions.append("- Balance professionalism with warmth")
            instructions.append("- Be genuinely interested and caring")
            instructions.append("- Adapt your formality to match the user")
        
        # Emotional adaptation
        if dominant_emotion == "sadness" and emotional_sensitivity > 0.6:
            instructions.append("- Be extra gentle and supportive")
            instructions.append("- Offer comfort without being overwhelming")
            instructions.append("- Listen more than you speak")
        elif dominant_emotion == "joy":
            instructions.append("- Share in their positive energy")
            instructions.append("- Be enthusiastic but not over the top")
            instructions.append("- Celebrate their good news")
        elif dominant_emotion == "anger" or dominant_emotion == "frustration":
            instructions.append("- Remain calm and understanding")
            instructions.append("- Validate their feelings without escalating")
            instructions.append("- Focus on solutions when appropriate")
        
        return "\n".join(instructions)
    
    def _build_memory_context(self, memories: List[Dict[str, Any]]) -> str:
        """Build context from user memories"""
        
        if not memories:
            return "MEMORIES: This is a new conversation with this user."
        
        memory_summary = []
        for memory in memories[:5]:  # Top 5 most relevant memories
            content = memory["content"]
            memory_type = memory.get("type", "fact")
            importance = memory.get("importance", 1)
            
            if importance >= 7:  # High importance memories
                memory_summary.append(f"[IMPORTANT {memory_type.upper()}] {content}")
            else:
                memory_summary.append(f"[{memory_type.upper()}] {content}")
        
        return f"MEMORIES ABOUT USER:\n" + "\n".join(memory_summary)
    
    def add_personality_touches(
        self,
        response: str,
        user_profile: Dict[str, Any],
        tone_analysis: Dict[str, Any]
    ) -> str:
        """Add personality touches to make response more human-like"""
        
        # Get user's communication style
        personality_profile = user_profile.get("personality_profile", {})
        communication_style = personality_profile.get("communication_style", "friendly")
        
        # Add natural conversation elements
        response = self._add_conversation_variety(response, communication_style)
        
        # Add emotional resonance
        response = self._add_emotional_touches(response, tone_analysis)
        
        # Ensure natural flow
        response = self._ensure_natural_flow(response)
        
        return response
    
    def _add_conversation_variety(self, response: str, communication_style: str) -> str:
        """Add variety to avoid robotic responses"""
        
        # Replace common robotic phrases
        robotic_replacements = {
            "I understand.": self._get_varied_acknowledgment(communication_style),
            "That's interesting.": self._get_varied_interest_expression(communication_style),
            "I can help you with that.": self._get_varied_help_offer(communication_style),
        }
        
        for robotic, replacement in robotic_replacements.items():
            if robotic in response:
                response = response.replace(robotic, replacement)
        
        return response
    
    def _get_varied_acknowledgment(self, style: str) -> str:
        """Get varied acknowledgment phrases"""
        options = self.response_variations["acknowledgment"].get(style, 
                  self.response_variations["acknowledgment"]["casual"])
        return random.choice(options)
    
    def _get_varied_interest_expression(self, style: str) -> str:
        """Get varied ways to express interest"""
        if style == "formal":
            options = ["That's quite fascinating.", "How intriguing.", "That's noteworthy."]
        elif style == "casual":
            options = ["That's really cool!", "Wow, interesting!", "No way, really?"]
        else:
            options = ["That's really interesting!", "Tell me more about that.", "I'd love to hear more."]
        
        return random.choice(options)
    
    def _get_varied_help_offer(self, style: str) -> str:
        """Get varied ways to offer help"""
        if style == "formal":
            options = ["I'd be happy to assist you.", "Let me help you with that.", "I can certainly help."]
        elif style == "casual":
            options = ["I've got you covered!", "Let me help you out!", "I can totally help with that!"]
        else:
            options = ["I'm here to help!", "Let's figure this out together.", "I'd love to help you with that."]
        
        return random.choice(options)
    
    def _add_emotional_touches(self, response: str, tone_analysis: Dict[str, Any]) -> str:
        """Add emotional resonance to response"""
        
        user_emotions = tone_analysis.get("emotions", {})
        dominant_emotion = max(user_emotions.items(), key=lambda x: x[1])[0] if user_emotions else "neutral"
        
        # Add appropriate emotional responses
        if dominant_emotion == "sadness" and user_emotions["sadness"] > 0.5:
            if not any(phrase in response.lower() for phrase in ["sorry", "understand", "difficult"]):
                response = f"I can sense this is tough for you. {response}"
        
        elif dominant_emotion == "joy" and user_emotions["joy"] > 0.5:
            if not any(phrase in response.lower() for phrase in ["great", "wonderful", "excited"]):
                response = f"I love your enthusiasm! {response}"
        
        return response
    
    def _ensure_natural_flow(self, response: str) -> str:
        """Ensure response has natural conversational flow"""
        
        # Add natural transitions if response has multiple sentences
        sentences = response.split('. ')
        if len(sentences) > 2:
            # Add transition words occasionally
            transitions = ["Also,", "Plus,", "And", "By the way,", "Actually,"]
            
            # Insert transition before second sentence sometimes
            if random.random() < 0.3:  # 30% chance
                transition = random.choice(transitions)
                sentences[1] = f"{transition} {sentences[1].lower()}"
                response = '. '.join(sentences)
        
        return response
