# import json
# import os
# from abc import ABC, abstractmethod
# from typing import Dict, Any, Union
# from deep_translator import GoogleTranslator


# class TranslationService(ABC):
#     """Abstract base class for translation services"""
    
#     @abstractmethod
#     def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
#         pass
    
#     def translate_to_lao(self, text: str) -> str:
#         return self.translate_text(text, 'en', 'lo')
    
#     def translate_to_english(self, text: str) -> str:
#         return self.translate_text(text, 'lo', 'en')

# class FreeGoogleTranslator(TranslationService):
#     """Free Google Translate via deep-translator"""

#     def __init__(self):
#         self.available = True
#         self.translator = GoogleTranslator(source='en', target='lo')

#     def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
#         if not text or not text.strip():
#             return text
#         try:
#             # Update the translator dynamically
#             self.translator.source = source_lang
#             self.translator.target = target_lang
#             return self.translator.translate(text)
#         except Exception as e:
#             print(f"Free translation error: {e}")
#             return text


# # class FreeGoogleTranslator(TranslationService):
# #     """Free Google Translate implementation"""
    
# #     def __init__(self):
# #         try:
# #             from googletrans import Translator
# #             self.translator = Translator()
# #             self.available = True
# #         except ImportError:
# #             print("Warning: googletrans not installed. Install with: pip install googletrans==4.0.0rc1")
# #             self.available = False
    
# #     def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
# #         if not self.available:
# #             return text
        
# #         try:
# #             if not text or not text.strip():
# #                 return text
# #             result = self.translator.translate(text, src=source_lang, dest=target_lang)
# #             return result.text
# #         except Exception as e:
# #             print(f"Free translation error: {e}")
# #             return text

# class GoogleCloudTranslator(TranslationService):
#     """Official Google Cloud Translation API implementation"""
    
#     def __init__(self, credentials_path: str = None):
#         try:
#             from google.cloud import translate_v2 as translate
            
#             if credentials_path:
#                 os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
            
#             self.translate_client = translate.Client()
#             self.available = True
#         except ImportError:
#             print("Warning: google-cloud-translate not installed. Install with: pip install google-cloud-translate")
#             self.available = False
#         except Exception as e:
#             print(f"Google Cloud setup error: {e}")
#             self.available = False
    
#     def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
#         if not self.available:
#             return text
        
#         try:
#             if not text or not text.strip():
#                 return text
            
#             result = self.translate_client.translate(
#                 text,
#                 source_language=source_lang,
#                 target_language=target_lang
#             )
#             return result['translatedText']
#         except Exception as e:
#             print(f"Google Cloud translation error: {e}")
#             return text

# class TranslationManager:
#     """Manager class that handles translation service selection and JSON processing"""
    
#     def __init__(self, service_type: str = "free", **kwargs):
#         """
#         Initialize translation manager
        
#         Args:
#             service_type: "free" or "google_cloud"
#             **kwargs: Additional parameters for specific services
#         """
#         self.current_language = 'en'
        
#         if service_type == "free":
#             self.service = FreeGoogleTranslator()
#         elif service_type == "google_cloud":
#             credentials_path = kwargs.get('credentials_path')
#             self.service = GoogleCloudTranslator(credentials_path)
#         else:
#             raise ValueError(f"Unknown service type: {service_type}")
    
#     def translate_to_lao(self, content: Union[str, Dict]) -> Union[str, Dict]:
#         """Translate content to Lao language"""
#         if isinstance(content, dict):
#             return self._translate_json_structure(content, 'lo')
#         elif isinstance(content, str):
#             if content.strip().startswith('{') and content.strip().endswith('}'):
#                 try:
#                     json_data = json.loads(content)
#                     translated = self._translate_json_structure(json_data, 'lo')
#                     return json.dumps(translated, ensure_ascii=False, indent=2)
#                 except:
#                     return self.service.translate_to_lao(content)
#             else:
#                 return self.service.translate_to_lao(content)
#         return content
    
#     def translate_to_english(self, content: Union[str, Dict]) -> Union[str, Dict]:
#         """Translate content to English language"""
#         if isinstance(content, dict):
#             return self._translate_json_structure(content, 'en')
#         elif isinstance(content, str):
#             if content.strip().startswith('{') and content.strip().endswith('}'):
#                 try:
#                     json_data = json.loads(content)
#                     translated = self._translate_json_structure(json_data, 'en')
#                     return json.dumps(translated, ensure_ascii=False, indent=2)
#                 except:
#                     return self.service.translate_to_english(content)
#             else:
#                 return self.service.translate_to_english(content)
#         return content
    
#     def _translate_json_structure(self, obj: Any, target_lang: str) -> Any:
#         """Recursively translate JSON structure while preserving format"""
#         if isinstance(obj, dict):
#             return {key: self._translate_json_structure(value, target_lang) for key, value in obj.items()}
#         elif isinstance(obj, list):
#             return [self._translate_json_structure(item, target_lang) for item in obj]
#         elif isinstance(obj, str) and obj.strip():
#             if target_lang == 'lo':
#                 return self.service.translate_to_lao(obj)
#             else:
#                 return self.service.translate_to_english(obj)
#         else:
#             return obj

# # Usage Examples:

# # For development (free):
# # translation_manager = TranslationManager(service_type="free")

# # For production (Google Cloud):
# # translation_manager = TranslationManager(
# #     service_type="google_cloud", 
# #     credentials_path="/path/to/credentials.json"
# # )














#15-09-2025

import json
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Union

class TranslationService(ABC):
    """Abstract base class for translation services"""
    
    @abstractmethod
    def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        pass
    
    def translate_to_lao(self, text: str) -> str:
        return self.translate_text(text, 'en', 'lo')
    
    def translate_to_english(self, text: str) -> str:
        return self.translate_text(text, 'lo', 'en')

class FreeGoogleTranslator(TranslationService):
    """Free Google Translate via deep-translator"""

    def __init__(self):
        try:
            from deep_translator import GoogleTranslator
            self.GoogleTranslator = GoogleTranslator
            self.available = True
        except ImportError:
            print("Warning: deep-translator not installed. Install with: pip install deep-translator")
            self.available = False

    def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        if not self.available or not text or not text.strip():
            return text
        
        try:
            # Create translator instance with dynamic languages
            translator = self.GoogleTranslator(source=source_lang, target=target_lang)
            return translator.translate(text)
        except Exception as e:
            print(f"Free translation error: {e}")
            return text

class GoogleCloudTranslator(TranslationService):
    """Official Google Cloud Translation API implementation"""
    
    def __init__(self, credentials_path: str = None):
        try:
            from google.cloud import translate_v2 as translate
            
            if credentials_path:
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
            
            self.translate_client = translate.Client()
            self.available = True
        except ImportError:
            print("Warning: google-cloud-translate not installed. Install with: pip install google-cloud-translate")
            self.available = False
        except Exception as e:
            print(f"Google Cloud setup error: {e}")
            self.available = False
    
    def translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        if not self.available:
            return text
        
        try:
            if not text or not text.strip():
                return text
            
            result = self.translate_client.translate(
                text,
                source_language=source_lang,
                target_language=target_lang
            )
            return result['translatedText']
        except Exception as e:
            print(f"Google Cloud translation error: {e}")
            return text

class TranslationManager:
    """Manager class that handles translation service selection and JSON processing"""
    
    def __init__(self, service_type: str = "free", **kwargs):
        """
        Initialize translation manager
        
        Args:
            service_type: "free" or "google_cloud"
            **kwargs: Additional parameters for specific services
        """
        self.current_language = 'en'
        
        if service_type == "free":
            self.service = FreeGoogleTranslator()
        elif service_type == "google_cloud":
            credentials_path = kwargs.get('credentials_path')
            self.service = GoogleCloudTranslator(credentials_path)
        else:
            raise ValueError(f"Unknown service type: {service_type}")
    
    def translate_to_lao(self, content: Union[str, Dict]) -> Union[str, Dict]:
        """Translate content to Lao language"""
        if isinstance(content, dict):
            return self._translate_json_structure(content, 'lo')
        elif isinstance(content, str):
            if content.strip().startswith('{') and content.strip().endswith('}'):
                try:
                    json_data = json.loads(content)
                    translated = self._translate_json_structure(json_data, 'lo')
                    return json.dumps(translated, ensure_ascii=False, indent=2)
                except:
                    return self.service.translate_to_lao(content)
            else:
                return self.service.translate_to_lao(content)
        return content
    
    def translate_to_english(self, content: Union[str, Dict]) -> Union[str, Dict]:
        """Translate content to English language"""
        if isinstance(content, dict):
            return self._translate_json_structure(content, 'en')
        elif isinstance(content, str):
            if content.strip().startswith('{') and content.strip().endswith('}'):
                try:
                    json_data = json.loads(content)
                    translated = self._translate_json_structure(json_data, 'en')
                    return json.dumps(translated, ensure_ascii=False, indent=2)
                except:
                    return self.service.translate_to_english(content)
            else:
                return self.service.translate_to_english(content)
        return content
    
    def _translate_json_structure(self, obj: Any, target_lang: str) -> Any:
        """Recursively translate JSON structure while preserving format"""
        if isinstance(obj, dict):
            return {key: self._translate_json_structure(value, target_lang) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._translate_json_structure(item, target_lang) for item in obj]
        elif isinstance(obj, str) and obj.strip():
            if target_lang == 'lo':
                return self.service.translate_to_lao(obj)
            else:
                return self.service.translate_to_english(obj)
        else:
            return obj

# Usage Examples:

# For development (free):
# translation_manager = TranslationManager(service_type="free")

# For production (Google Cloud):
# translation_manager = TranslationManager(
#     service_type="google_cloud", 
#     credentials_path="/path/to/credentials.json"
# )