"""
Language detection service using FastText and langdetect for higher accuracy
"""

import logging
import os
from typing import Dict, Optional

from app.core.config import get_settings

# Try to import fasttext, but make it optional
try:
    import fasttext

    FASTTEXT_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    FASTTEXT_AVAILABLE = False
    fasttext = None
    logging.warning(
        "FastText not available. Language detection will use langdetect or fallback method."
    )

# Try to import langdetect, but make it optional
try:
    from langdetect import detect, detect_langs, LangDetectException

    LANGDETECT_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    LANGDETECT_AVAILABLE = False
    detect = None
    detect_langs = None
    LangDetectException = None
    logging.warning(
        "langdetect not available. Language detection will use FastText or fallback method."
    )

logger = logging.getLogger(__name__)
settings = get_settings()


class LanguageService:
    """Service for detecting language in text using FastText."""

    def __init__(self, model_path: Optional[str] = None):
        self.model = None
        self.model_path = model_path or settings.language_model_path
        self.model_name = "lid.176.bin"
        self._load_model()

    def _load_model(self):
        """Load FastText language detection model (download if required)."""

        if not FASTTEXT_AVAILABLE:
            logger.info("FastText not available. Using fallback language detection.")
            self.model = None
            return

        try:
            possible_paths = [
                self.model_path,
                f"models/{self.model_name}",
                f"data/{self.model_name}",
                os.path.expanduser(f"~/.fasttext/{self.model_name}"),
            ]

            model_file = next(
                (path for path in possible_paths if path and os.path.exists(path)),
                None,
            )

            if not model_file:
                logger.info(
                    "FastText model not found. Attempting to download %s...",
                    self.model_name,
                )
                try:
                    import urllib.request

                    os.makedirs("models", exist_ok=True)
                    model_file = f"models/{self.model_name}"

                    url = (
                        "https://dl.fbaipublicfiles.com/fasttext/supervised-models/"
                        f"{self.model_name}"
                    )
                    logger.info("Downloading FastText model from %s", url)
                    urllib.request.urlretrieve(url, model_file)
                    logger.info("Downloaded FastText model to %s", model_file)

                except Exception as download_error:  # pragma: no cover - remote IO
                    logger.warning("Could not download FastText model: %s", download_error)
                    logger.info("Using fallback language detection (keyword-based)")
                    self.model = None
                    return

            logger.info("Loading FastText model from %s", model_file)
            self.model = fasttext.load_model(model_file)
            logger.info("FastText model loaded successfully")

        except Exception as exc:  # pragma: no cover - runtime protection
            logger.exception("Error loading FastText model: %s", exc)
            logger.info("Using fallback language detection")
            self.model = None

    def detect_language(self, text: str, prefer_langdetect: bool = False) -> Dict:
        """
        Detect the language of given text using FastText, langdetect, or fallback.
        
        Args:
            text (str): Input text to detect language for
            prefer_langdetect (bool): If True, prefer langdetect over FastText
            
        Returns:
            Dict: Language detection results with ISO code, confidence, and method
        """
        if not text or not text.strip():
            return {
                'language': 'English',
                'language_code': 'en',
                'confidence': 0.0,
                'method': 'fallback'
            }
        
        # Try langdetect first if preferred and available
        if prefer_langdetect and LANGDETECT_AVAILABLE:
            try:
                result = self._detect_with_langdetect(text)
                if result:
                    return result
            except Exception as e:
                logger.warning(f"langdetect detection failed: {str(e)}")
        
        # Use FastText if available
        if self.model:
            try:
                # FastText requires at least one word
                if len(text.strip().split()) == 0:
                    return self._try_fallbacks(text)
                
                # Predict language
                predictions = self.model.predict(text, k=1)
                
                # Extract language code (format: __label__en -> en)
                label = predictions[0][0].replace('__label__', '')
                confidence = float(predictions[1][0])
                
                # Map to ISO 639-1 code if needed
                language_code = self._normalize_language_code(label)
                language_name = self._get_language_name(language_code)
                
                return {
                    'language': language_name,
                    'language_code': language_code,
                    'confidence': round(confidence, 4),
                    'method': 'fasttext'
                }
                
            except Exception as e:
                logger.warning(f"FastText detection failed: {str(e)}")
                return self._try_fallbacks(text)
        else:
            # Try langdetect if FastText not available
            if LANGDETECT_AVAILABLE:
                try:
                    result = self._detect_with_langdetect(text)
                    if result:
                        return result
                except Exception as e:
                    logger.warning(f"langdetect detection failed: {str(e)}")
            
            # Fallback to keyword-based detection
            return self._fallback_detection(text)
    
    def _detect_with_langdetect(self, text: str) -> Optional[Dict]:
        """
        Detect language using langdetect library.
        
        Args:
            text (str): Input text
            
        Returns:
            Optional[Dict]: Language detection results or None if failed
        """
        if not LANGDETECT_AVAILABLE or not detect or not detect_langs:
            return None
        
        try:
            # langdetect requires at least a few words
            words = text.strip().split()
            if len(words) < 2:
                return None
            
            # Detect language
            language_code = detect(text)
            
            # Get confidence scores
            try:
                lang_probs = detect_langs(text)
                confidence = float(lang_probs[0].prob) if lang_probs else 0.8
            except Exception:
                confidence = 0.8  # Default confidence if can't get probabilities
            
            # Normalize language code
            language_code = self._normalize_language_code(language_code)
            language_name = self._get_language_name(language_code)
            
            return {
                'language': language_name,
                'language_code': language_code,
                'confidence': round(confidence, 4),
                'method': 'langdetect'
            }
            
        except LangDetectException as e:
            logger.warning(f"langdetect exception: {str(e)}")
            return None
        except Exception as e:
            logger.warning(f"Error in langdetect: {str(e)}")
            return None
    
    def _try_fallbacks(self, text: str) -> Dict:
        """
        Try fallback detection methods (langdetect, then keyword-based).
        
        Args:
            text (str): Input text
            
        Returns:
            Dict: Language detection results
        """
        # Try langdetect if available
        if LANGDETECT_AVAILABLE:
            result = self._detect_with_langdetect(text)
            if result:
                return result
        
        # Fallback to keyword-based detection
        return self._fallback_detection(text)
    
    def _normalize_language_code(self, code: str) -> str:
        """
        Normalize language code to ISO 639-1 format.
        
        Args:
            code (str): Language code from FastText
            
        Returns:
            str: Normalized ISO 639-1 code
        """
        # FastText uses ISO 639-1 codes, but some may need normalization
        code = code.lower()
        
        # Common mappings
        mappings = {
            'zh-cn': 'zh',
            'zh-tw': 'zh',
        }
        
        return mappings.get(code, code)
    
    def _get_language_name(self, code: str) -> str:
        """
        Get language name from ISO code.
        
        Args:
            code (str): ISO 639-1 language code
            
        Returns:
            str: Language name
        """
        language_names = {
            'en': 'English',
            'de': 'German',
            'fr': 'French',
            'es': 'Spanish',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'zh': 'Chinese',
            'ja': 'Japanese',
            'ko': 'Korean',
            'ar': 'Arabic',
            'hi': 'Hindi',
            'nl': 'Dutch',
            'sv': 'Swedish',
            'pl': 'Polish',
            'tr': 'Turkish',
        }
        
        return language_names.get(code, code.upper())
    
    def _fallback_detection(self, text: str) -> Dict:
        """
        Fallback language detection using keyword matching.
        
        Args:
            text (str): Input text
            
        Returns:
            Dict: Language detection results
        """
        # Very basic keyword-based detection
        text_lower = text.lower()
        
        # German indicators
        german_words = ['der', 'die', 'das', 'und', 'ist', 'für', 'mit', 'zu']
        german_count = sum(1 for word in german_words if word in text_lower)
        
        # French indicators
        french_words = ['le', 'la', 'les', 'et', 'est', 'pour', 'avec', 'de']
        french_count = sum(1 for word in french_words if word in text_lower)
        
        # Spanish indicators
        spanish_words = ['el', 'la', 'los', 'y', 'es', 'para', 'con', 'de']
        spanish_count = sum(1 for word in spanish_words if word in text_lower)
        
        # Determine language
        if german_count > french_count and german_count > spanish_count:
            return {
                'language': 'German',
                'language_code': 'de',
                'confidence': min(0.7, 0.5 + (german_count * 0.05)),
                'method': 'fallback'
            }
        elif french_count > spanish_count:
            return {
                'language': 'French',
                'language_code': 'fr',
                'confidence': min(0.7, 0.5 + (french_count * 0.05)),
                'method': 'fallback'
            }
        elif spanish_count > 0:
            return {
                'language': 'Spanish',
                'language_code': 'es',
                'confidence': min(0.7, 0.5 + (spanish_count * 0.05)),
                'method': 'fallback'
            }
        else:
            # Default to English
            return {
                'language': 'English',
                'language_code': 'en',
                'confidence': 0.6,
                'method': 'fallback'
            }
    
    def is_model_loaded(self) -> bool:
        """
        Check if FastText model is loaded.
        
        Returns:
            bool: True if model is loaded
        """
        return self.model is not None
    
    def get_model_info(self) -> Dict:
        """
        Get information about the language detection model.
        
        Returns:
            Dict: Model information
        """
        methods = []
        if self.is_model_loaded():
            methods.append('fasttext')
        if LANGDETECT_AVAILABLE:
            methods.append('langdetect')
        if not methods:
            methods.append('fallback')
        
        return {
            'model_loaded': self.is_model_loaded(),
            'model_name': self.model_name,
            'fasttext_available': FASTTEXT_AVAILABLE,
            'langdetect_available': LANGDETECT_AVAILABLE,
            'methods': methods,
            'primary_method': 'fasttext' if self.is_model_loaded() else ('langdetect' if LANGDETECT_AVAILABLE else 'fallback')
        }


# Global language service instance
language_service = LanguageService()

