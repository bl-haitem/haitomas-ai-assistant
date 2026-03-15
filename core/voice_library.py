
"""
HAITOMAS ASSISTANT — Voice Library
Pre-defined phrases for various situations in multiple languages.
"""

VOICE_LIB = {
    "startup": {
        "en": "HAITOMAS systems online. Ready for your commands, Commander.",
        "ar": "أنظمة هايتوماس متصلة بالإنترنت. جاهز لأوامرك يا قائد."
    },
    "thinking": {
        "en": [
            "Just a moment, Commander. I'm analyzing the telemetry.",
            "Processing your request through my neural core...",
            "Accessing global knowledge banks now.",
            "Analyzing data. Please stand by.",
            "Synthesizing information. Almost there.",
            "Engaging advanced reasoning protocols...",
            "Scanning sources for the most relevant data."
        ],
        "ar": [
            "لحظة واحدة يا قائد. أنا أقوم بتحليل البيانات.",
            "جاري معالجة طلبك عبر نواتي العصبية...",
            "أقوم بالوصول إلى بنوك المعرفة العالمية الآن.",
            "تحليل البيانات. يرجى الانتظار.",
            "تجميع المعلومات. اقتربنا من الوصول.",
            "تفعيل بروتوكولات التفكير المتقدمة...",
            "مسح المصادر للعثور على أدق البيانات."
        ]
    },
    "task_start": {
        "en": "Initiating the requested mission. Execution in progress.",
        "ar": "بدء المهمة المطلوبة. التنفيذ جاري."
    },
    "task_success": {
        "en": [
            "Mission accomplished. All parameters successfully executed.",
            "Task complete. All systems nominal.",
            "Successfully finished the requested operation.",
            "Execution successful, Commander."
        ],
        "ar": [
            "تمت المهمة بنجاح. تم تنفيذ جميع المعايير بنجاح.",
            "اكتملت المهمة. جميع الأنظمة تعمل بشكل طبيعي.",
            "تم الانتهاء من العملية المطلوبة بنجاح.",
            "تم التنفيذ بنجاح يا قائد."
        ]
    },
    "task_error": {
        "en": "Warning: Mission encountered a disruption in the processing pipeline.",
        "ar": "تحذير: واجهت المهمة انقطاعًا في خط معالجة البيانات."
    },
    "research_start": {
        "en": "I am initiating a deep search. I will analyze the best sources and provide you with organized insights.",
        "ar": "أنا أقوم ببدء بحث عميق. سأقوم بتحليل أفضل المصادر وأزودك برؤى منظمة."
    },
    "email_prep": {
        "en": "Preparing the communication transmission for the specified recipient.",
        "ar": "تجهيز إرسال الاتصال للمستلم المحدد."
    },
    "searching_resources": {
        "en": "Searching for the requested resources across all available networks.",
        "ar": "البحث عن الموارد المطلوبة عبر جميع الشبكات المتاحة."
    },
    "waiting": {
        "en": "Still working on it, Commander. Complex tasks require precision.",
        "ar": "ما زلت أعمل على ذلك يا قائد. المهام المعقدة تتطلب الدقة."
    }
}

import random

def get_phrase(key, lang="en"):
    """Get a random phrase for a given key and language."""
    if key not in VOICE_LIB:
        return ""
    
    options = VOICE_LIB[key]
    if lang not in options:
        lang = "en" # Fallback to English
    
    phrase = options[lang]
    if isinstance(phrase, list):
        return random.choice(phrase)
    return phrase
