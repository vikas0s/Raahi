"""
Unified AI Orchestration Service for Raahi.
Coordinates multi-LLM providers:
1. Google Gemini (gemini-2.0-flash / gemini-1.5-flash) - Primary high-speed multilingual model
2. Sarvam AI (sarvam-105b) - Secondary Indian language specialist
3. Domain-Specific Cultural Knowledge Fallback - Zero-latency verified information for Braj/NCR/Mumbai/BLR
"""
import logging
from typing import List, Dict, Optional, Tuple
from .gemini_service import gemini_service_instance, GeminiAPIError, GeminiConfigurationError
from .sarvam_service import sarvam_service_instance, SarvamAPIError, SarvamConfigurationError

logger = logging.getLogger("raahi.ai_service")

# Curated local knowledge base for Mathura-Vrindavan, Delhi NCR, Mumbai & Bengaluru
CULTURAL_KNOWLEDGE = {
    "prem_mandir": {
        "hi": (
            "**प्रेम मंदिर (Prem Mandir, Vrindavan) - लाइट शो और दर्शन का समय:**\n\n"
            "✨ **म्यूजिकल फव्वारा व लेजर लाइट शो:**\n"
            "• **गर्मियों में**: शाम 7:30 PM से 8:00 PM तक\n"
            "• **सर्दियों में**: शाम 7:00 PM से 7:30 PM तक (निशुल्क प्रवेश)\n\n"
            "🛕 **मंदिर दर्शन समय:**\n"
            "• सुबह: 5:30 AM – 12:00 PM\n"
            "• शाम: 4:30 PM – 8:30 PM\n\n"
            "🚖 **मथुरा जंक्शन से कैसे पहुँचें (~12 km):**\n"
            "1. **ब्रज इलेक्ट्रिक AC ई-बस**: ₹25 - ₹35 किराया, मथुरा जंक्शन से सीधे प्रेम मंदिर गेट (छटीकरा रोड) तक (~25 मिनट)।\n"
            "2. **शेयरिंग टेम्पो**: ₹30 प्रति सीट छटीकरा तक, फिर ₹10 ई-रिक्शा।\n"
            "3. **डायरेक्ट ऑटो / कैब**: ₹180 - ₹250।"
        ),
        "en": (
            "**Prem Mandir (Vrindavan) — Light Show Timings & Transit Guide:**\n\n"
            "✨ **Musical Fountain & Light Show Timings:**\n"
            "• **Summer**: 7:30 PM to 8:00 PM daily\n"
            "• **Winter**: 7:00 PM to 7:30 PM daily (Free entry inside temple complex)\n\n"
            "🛕 **General Temple Darshan Timings:**\n"
            "• Morning: 5:30 AM to 12:00 PM\n"
            "• Evening: 4:30 PM to 8:30 PM\n\n"
            "🚖 **How to Reach from Mathura Junction (12 km):**\n"
            "1. **Braj Electric AC City Bus**: ₹25 - ₹35 direct from MTJ to Prem Mandir gate (~25 mins).\n"
            "2. **Shared CNG Tempo**: ₹30 per seat towards Chatikara / Attalla Chungi + ₹10 E-Rickshaw to gate.\n"
            "3. **Direct Reserved Auto / App Cab**: ₹180 - ₹250 doorstep drop."
        )
    },
    "bankey_bihari": {
        "hi": (
            "**श्री बांके बिहारी जी मंदिर (Vrindavan) दर्शन व आरती समय:**\n\n"
            "• **सुबह का दर्शन**: 7:45 AM से 12:00 PM (राजभोग आरती ~11:55 AM)\n"
            "• **शाम का दर्शन**: 5:30 PM से 9:30 PM (शयन आरती ~9:25 PM)\n\n"
            "🚖 **मथुरा जंक्शन से पहुँचने का तरीका:**\n"
            "मथुरा जंक्शन से ई-बस या शेयरिंग टेम्पो लेकर अटल्ला चुंगी / विद्यापीठ चौराहा पहुंचें, वहां से ई-रिक्शा (₹10) मंदिर की परिक्रमा मार्ग की ओर ले जाता है।"
        ),
        "en": (
            "**Shri Bankey Bihari Ji Temple (Vrindavan) Darshan & Aarti Timings:**\n\n"
            "• **Morning Darshan**: 7:45 AM – 12:00 PM (Rajbhog Aarti ~11:55 AM)\n"
            "• **Evening Darshan**: 5:30 PM – 9:30 PM (Shayan Aarti ~9:25 PM)\n\n"
            "🚖 **How to Reach from Mathura Junction:**\n"
            "Board Braj AC E-Bus or Shared Tempo from MTJ to Attalla Chungi (~₹30), then take a 5-min local E-Rickshaw (₹10) to Vidyapeeth entrance."
        )
    },
    "janmasthan": {
        "hi": (
            "**श्रीकृष्ण जन्मस्थान मंदिर (Mathura) समय व जानकारी:**\n\n"
            "• **ग्रीष्मकालीन दर्शन**: सुबह 5:00 AM – 12:00 PM | शाम 4:00 PM – 9:30 PM\n"
            "• **शीतकालीन दर्शन**: सुबह 5:30 AM – 12:00 PM | शाम 3:00 PM – 8:30 PM\n\n"
            "🚖 **मथुरा जंक्शन से केवल 3.5 km:**\n"
            "मथुरा जंक्शन के गेट 1 से ई-रिक्शा (₹10 - ₹20) या ऑटो (₹60 - ₹80) सीधे मुख्य द्वार तक 10 मिनट में पहुँचा देता है।"
        ),
        "en": (
            "**Shri Krishna Janmasthan Temple (Mathura) Timings & Guide:**\n\n"
            "• **Darshan Hours**: 5:00 AM – 12:00 PM & 4:00 PM – 9:30 PM daily.\n"
            "• **Location**: 3.5 km from Mathura Junction.\n"
            "• **Transit**: Take a local E-Rickshaw (Toto) for ₹10 - ₹20 directly from Mathura Junction Gate 1 (10 mins trip)."
        )
    }
}

class UnifiedAIService:
    """
    Intelligently orchestrates Gemini, Sarvam, and Local Knowledge fallback.
    """

    def get_active_provider_name(self) -> str:
        if gemini_service_instance.is_configured():
            return "Google Gemini"
        if sarvam_service_instance.is_configured():
            return "Sarvam AI"
        return "Raahi Intelligent Assistant"

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        system_instruction: Optional[str] = None,
        language: str = "en",
        temperature: float = 0.3,
        user_query: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Executes completion with tier priority:
        Tier 1: Google Gemini (if GEMINI_API_KEY present)
        Tier 2: Sarvam AI (if SARVAM_API_KEY present)
        Tier 3: Domain-specific verified knowledge base
        Returns: (reply_text, provider_name)
        """
        # 1. Try Google Gemini if configured
        if gemini_service_instance.is_configured():
            try:
                res = await gemini_service_instance.chat_completion(
                    messages=messages,
                    system_instruction=system_instruction,
                    temperature=temperature
                )
                if res and res.strip():
                    return res.strip(), "gemini"
            except Exception as e:
                logger.warning("Gemini completion failed or timed out: %s. Falling back to secondary provider.", e)

        # 2. Try Sarvam AI if configured
        if sarvam_service_instance.is_configured():
            try:
                # Merge system instruction into messages if not already present
                combined_msgs = []
                if system_instruction and not any(m.get("role") == "system" for m in messages):
                    combined_msgs.append({"role": "system", "content": system_instruction})
                combined_msgs.extend(messages)

                res = await sarvam_service_instance.chat_completion(
                    messages=combined_msgs,
                    temperature=temperature
                )
                if res and res.strip():
                    return res.strip(), "sarvam"
            except Exception as e:
                logger.warning("Sarvam AI completion failed: %s. Falling back to local knowledge.", e)

        # 3. Local Domain-Specific Knowledge Fallback
        q_low = (user_query or "").lower()
        if not q_low and messages:
            last_user = next((m.get("content", "") for m in reversed(messages) if m.get("role") == "user"), "")
            q_low = last_user.lower()

        lang_key = "hi" if language in ("hi", "hinglish") else "en"

        if any(w in q_low for w in ["prem mandir", "प्रेम मंदिर", "light show", "लाइट शो", "fountain", "फव्वारा"]):
            return CULTURAL_KNOWLEDGE["prem_mandir"][lang_key], "local_knowledge"
        elif any(w in q_low for w in ["bankey bihari", "बांके बिहारी", "bihari ji", "बिहारी जी"]):
            return CULTURAL_KNOWLEDGE["bankey_bihari"][lang_key], "local_knowledge"
        elif any(w in q_low for w in ["janmasthan", "जन्मस्थान", "janam sthan", "krishna janma", "कृष्ण जन्म"]):
            return CULTURAL_KNOWLEDGE["janmasthan"][lang_key], "local_knowledge"

        # General helpful greeting fallback
        if lang_key == "hi":
            return (
                "राधे-राधे! मैं राही AI हूँ। आप मुझसे किसी भी स्थान के सबसे तेज़ या सस्ते रूट, "
                "मंदिर दर्शन समय, और लाइव ट्रांजिट के बारे में पूछ सकते हैं।",
                "local_knowledge"
            )
        else:
            return (
                "Hello! I am Raahi AI. You can ask me for the fastest or cheapest routes, "
                "temple darshan & light show timings, or check transit options between any two places.",
                "local_knowledge"
            )

ai_service_instance = UnifiedAIService()
