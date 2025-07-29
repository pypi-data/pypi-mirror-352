import json
import os

def load_translations():
    translations = {}
    locales_dir = os.path.join(os.path.dirname(__file__), 'locales')
    
    for filename in os.listdir(locales_dir):
        if filename.endswith('.json'):
            lang = filename.split('.')[0]
            with open(os.path.join(locales_dir, filename), 'r', encoding='utf-8') as f:
                translations[lang] = json.load(f)
    
    return translations

TRANSLATIONS = load_translations()

def t(key, lang='ru', **kwargs):
    """Get translation for a key with optional formatting"""
    try:
        # Support nested keys like "buttons.start"
        keys = key.split('.')
        value = TRANSLATIONS[lang]
        for k in keys:
            value = value[k]
        
        return value.format(**kwargs) if kwargs else value
    except KeyError:
        # Fallback to English if translation missing
        if lang != 'en':
            return t(key, 'en', **kwargs)
        return key  # Return the key itself as last resort