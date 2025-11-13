"""
OCR Service - Multi-provider OCR with fallback strategy

Providers (in priority order):
    1. Azure Computer Vision (primary)
    2. EasyOCR (secondary)
    3. Tesseract (fallback)

Supported documents:
    - 履歴書 (Rirekisho/Resume)
    - 在留カード (Zairyu Card)
    - 運転免許証 (Driver's License)
    - タイムカード (Timer Card)
"""
import base64
import io
import re
import time
from typing import Optional, Dict, Any, List
from PIL import Image
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class OCRService:
    """Multi-provider OCR service with automatic fallback"""

    def __init__(self):
        self.azure_available = bool(settings.AZURE_CV_ENDPOINT and settings.AZURE_CV_KEY)
        self.easyocr_reader = None
        self.tesseract_available = self._check_tesseract()

    def _check_tesseract(self) -> bool:
        """Check if Tesseract is available"""
        try:
            import pytesseract
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False

    def _init_easyocr(self):
        """Lazy initialization of EasyOCR"""
        if self.easyocr_reader is None:
            try:
                import easyocr
                self.easyocr_reader = easyocr.Reader(['ja', 'en'], gpu=False)
                logger.info("EasyOCR initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize EasyOCR: {e}")

    async def process_image(
        self,
        image_data: bytes,
        document_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Process image with OCR using fallback strategy

        Args:
            image_data: Image data as bytes
            document_type: Type of document (general, rirekisho, zairyu_card, timer_card)

        Returns:
            Dict with extracted text and metadata
        """
        result = {
            "text": "",
            "confidence": 0.0,
            "provider": None,
            "fields": {},
            "success": False,
            "error": None
        }

        # Try Azure Computer Vision first
        if self.azure_available:
            try:
                azure_result = await self._process_with_azure(image_data)
                if azure_result["success"]:
                    result.update(azure_result)
                    result["provider"] = "azure"
                    return result
            except Exception as e:
                logger.warning(f"Azure OCR failed: {e}")

        # Fallback to EasyOCR
        try:
            self._init_easyocr()
            if self.easyocr_reader:
                easyocr_result = self._process_with_easyocr(image_data)
                if easyocr_result["success"]:
                    result.update(easyocr_result)
                    result["provider"] = "easyocr"
                    return result
        except Exception as e:
            logger.warning(f"EasyOCR failed: {e}")

        # Final fallback to Tesseract
        if self.tesseract_available:
            try:
                tesseract_result = self._process_with_tesseract(image_data)
                if tesseract_result["success"]:
                    result.update(tesseract_result)
                    result["provider"] = "tesseract"
                    return result
            except Exception as e:
                logger.error(f"Tesseract OCR failed: {e}")
                result["error"] = str(e)

        # All providers failed
        if not result["success"]:
            result["error"] = "All OCR providers failed"

        return result

    async def _process_with_azure(self, image_data: bytes) -> Dict[str, Any]:
        """Process image with Azure Computer Vision"""
        from azure.cognitiveservices.vision.computervision import ComputerVisionClient
        from msrest.authentication import CognitiveServicesCredentials

        client = ComputerVisionClient(
            settings.AZURE_CV_ENDPOINT,
            CognitiveServicesCredentials(settings.AZURE_CV_KEY)
        )

        # Read text from image
        read_response = client.read_in_stream(
            io.BytesIO(image_data),
            raw=True
        )

        # Get operation location
        operation_location = read_response.headers["Operation-Location"]
        operation_id = operation_location.split("/")[-1]

        # Wait for result (with timeout)
        max_attempts = 30  # 30 seconds timeout
        attempts = 0

        while attempts < max_attempts:
            result = client.get_read_result(operation_id)
            if result.status.lower() not in ['notstarted', 'running']:
                break
            time.sleep(1)
            attempts += 1

        if attempts >= max_attempts:
            raise TimeoutError("Azure OCR timeout after 30 seconds")

        # Extract text
        text_lines = []
        confidence_scores = []

        if result.status.lower() == 'succeeded':
            for page in result.analyze_result.read_results:
                for line in page.lines:
                    text_lines.append(line.text)
                    if hasattr(line, 'confidence'):
                        confidence_scores.append(line.confidence)

        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0

        return {
            "text": "\n".join(text_lines),
            "confidence": avg_confidence,
            "success": bool(text_lines),
            "lines": text_lines
        }

    def _process_with_easyocr(self, image_data: bytes) -> Dict[str, Any]:
        """Process image with EasyOCR"""
        image = Image.open(io.BytesIO(image_data))

        # Convert to numpy array
        import numpy as np
        image_np = np.array(image)

        # Perform OCR
        results = self.easyocr_reader.readtext(image_np)

        # Extract text and confidence
        text_lines = []
        confidence_scores = []

        for (bbox, text, confidence) in results:
            text_lines.append(text)
            confidence_scores.append(confidence)

        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0

        return {
            "text": "\n".join(text_lines),
            "confidence": avg_confidence,
            "success": bool(text_lines),
            "lines": text_lines
        }

    def _process_with_tesseract(self, image_data: bytes) -> Dict[str, Any]:
        """Process image with Tesseract OCR"""
        import pytesseract

        image = Image.open(io.BytesIO(image_data))

        # Perform OCR with Japanese and English
        custom_config = r'--oem 3 --psm 6 -l jpn+eng'
        text = pytesseract.image_to_string(image, config=custom_config)

        # Get confidence data
        data = pytesseract.image_to_data(image, config=custom_config, output_type=pytesseract.Output.DICT)
        confidences = [int(conf) for conf in data['conf'] if conf != '-1']
        avg_confidence = sum(confidences) / len(confidences) / 100 if confidences else 0.0

        return {
            "text": text,
            "confidence": avg_confidence,
            "success": bool(text.strip()),
            "lines": text.split('\n')
        }

    def extract_rirekisho_fields(self, ocr_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract structured fields from 履歴書 (Rirekisho) OCR result

        Returns dict with candidate fields
        """
        text = ocr_result.get("text", "")
        lines = ocr_result.get("lines", [])

        fields = {
            "full_name_kanji": None,
            "full_name_kana": None,
            "date_of_birth": None,
            "phone": None,
            "email": None,
            "current_address": None,
        }

        # Simple pattern matching (this should be enhanced with ML/regex)
        for i, line in enumerate(lines):
            line_lower = line.lower()

            # Look for name (氏名, 名前)
            if "氏名" in line or "名前" in line:
                if i + 1 < len(lines):
                    fields["full_name_kanji"] = lines[i + 1].strip()

            # Look for kana (フリガナ)
            if "フリガナ" in line or "ふりがな" in line:
                if i + 1 < len(lines):
                    fields["full_name_kana"] = lines[i + 1].strip()

            # Look for phone (電話, TEL)
            if "電話" in line or "TEL" in line_lower:
                # Extract phone number pattern
                phone_match = re.search(r'[\d\-]{10,}', line)
                if phone_match:
                    fields["phone"] = phone_match.group()

            # Look for email
            if "@" in line:
                email_match = re.search(r'[\w\.-]+@[\w\.-]+', line)
                if email_match:
                    fields["email"] = email_match.group()

            # Look for address (住所)
            if "住所" in line:
                if i + 1 < len(lines):
                    fields["current_address"] = lines[i + 1].strip()

        return fields

    def extract_timer_card_data(self, ocr_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract time card entries from OCR result

        Returns list of daily records with clock in/out times
        """
        lines = ocr_result.get("lines", [])
        records = []

        for line in lines:
            # Look for date pattern (YYYY/MM/DD or MM/DD)
            date_match = re.search(r'(\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2})', line)

            # Look for time patterns (HH:MM)
            time_matches = re.findall(r'\d{1,2}:\d{2}', line)

            if date_match and len(time_matches) >= 2:
                record = {
                    "date": date_match.group(),
                    "clock_in": time_matches[0],
                    "clock_out": time_matches[1],
                    "confidence": ocr_result.get("confidence", 0.0)
                }
                records.append(record)

        return records


# Singleton instance
ocr_service = OCRService()
