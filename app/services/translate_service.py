# Author: Mangesh Wagh
# Email: mangeshwagh2722@gmail.com


"""
Google Cloud Translation Service
Provides dynamic translation of user-generated content, event descriptions,
and food menus into local languages (Hindi, Marathi).
"""

import logging
from typing import Optional, List
from google.cloud import translate_v2 as translate

logger = logging.getLogger(__name__)


class TranslationService:
    """
    Google Cloud Translation integration.
    Supports dynamic language switching for a localized stadium experience.
    """

    def __init__(self, project_id: str):
        self.project_id = project_id
        try:
            self.client = translate.Client()
            logger.info("Google Cloud Translation client initialized")
        except Exception as e:
            logger.warning(f"Translation client failed to initialize: {e}")
            self.client = None

    def translate_text(
        self,
        text: str,
        target_lang: str,
        source_lang: str = "en"
    ) -> str:
        """
        Translate a single string of text.

        Args:
            text:        The text to translate
            target_lang: Target language code (e.g., 'hi', 'mr')
            source_lang: Source language code (default 'en')

        Returns:
            Translated text, or original text if translation fails
        """
        if not self.client or not text or target_lang == source_lang:
            return text

        try:
            result = self.client.translate(
                text,
                target_language=target_lang,
                source_language=source_lang
            )
            return result.get("translatedText", text)
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return text

    def translate_list(
        self,
        texts: List[str],
        target_lang: str,
        source_lang: str = "en"
    ) -> List[str]:
        """
        Translate a list of strings in a single batch.

        Args:
            texts:       List of strings to translate
            target_lang: Target language code
            source_lang: Source language code

        Returns:
            List of translated strings
        """
        if not self.client or not texts or target_lang == source_lang:
            return texts

        try:
            # Batch translation
            results = self.client.translate(
                texts,
                target_language=target_lang,
                source_language=source_lang
            )
            return [res.get("translatedText", "") for res in results]
        except Exception as e:
            logger.error(f"Batch translation failed: {e}")
            return texts
