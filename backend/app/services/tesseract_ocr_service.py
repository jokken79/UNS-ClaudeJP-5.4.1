"""
Tesseract OCR Service - UNS-ClaudeJP 5.4
Fallback OCR service using Tesseract for document processing
"""
import os
import logging
import re
from typing import Dict, Any, Optional
from io import BytesIO
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)


class TesseractOCRService:
    """Tesseract OCR service - Fallback for Azure and EasyOCR"""

    def __init__(self):
        """Initialize Tesseract OCR service"""
        self.tesseract_available = False
        self._check_tesseract_availability()
        logger.info(f"TesseractOCRService initialized - Available: {self.tesseract_available}")

    def _check_tesseract_availability(self):
        """Check if Tesseract is available on the system"""
        try:
            import pytesseract

            # Try to get Tesseract version
            version = pytesseract.get_tesseract_version()
            self.tesseract_available = True
            logger.info(f"Tesseract OCR is available - Version: {version}")

            # Check for Japanese language support
            try:
                languages = pytesseract.get_languages()
                if 'jpn' in languages:
                    logger.info("Tesseract: Japanese language support detected")
                else:
                    logger.warning("Tesseract: Japanese language NOT found. Install with: apt-get install tesseract-ocr-jpn")
            except Exception as e:
                logger.warning(f"Could not check Tesseract languages: {e}")

        except ImportError:
            logger.error("pytesseract module not installed. Install with: pip install pytesseract==0.3.10")
            self.tesseract_available = False
        except Exception as e:
            logger.error(f"Tesseract not available: {e}")
            self.tesseract_available = False

    def process_document(self, image_data: bytes, document_type: str = "zairyu_card") -> Dict[str, Any]:
        """
        Process document image with Tesseract OCR

        Args:
            image_data: Image bytes
            document_type: Type of document (zairyu_card, rirekisho, license, etc.)

        Returns:
            Dictionary with extracted data
        """
        if not self.tesseract_available:
            return {
                "success": False,
                "error": "Tesseract OCR is not available",
                "ocr_method": "tesseract",
                "raw_text": ""
            }

        try:
            logger.info(f"Processing document with Tesseract: {document_type}")

            # Process with Tesseract
            result = self._process_with_tesseract(image_data, document_type)

            logger.info(f"Tesseract processing completed: {document_type}")
            return result

        except Exception as e:
            logger.error(f"Error processing document with Tesseract: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "ocr_method": "tesseract",
                "raw_text": f"Error: {str(e)}"
            }

    def _process_with_tesseract(self, image_data: bytes, document_type: str) -> Dict[str, Any]:
        """Process image with Tesseract OCR"""
        try:
            import pytesseract
            from PIL import Image

            # Open image
            image = Image.open(BytesIO(image_data))

            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Preprocess image for better OCR results
            image = self._preprocess_image(image)

            # Configure Tesseract for Japanese + English
            # --psm 6: Assume uniform block of text
            # --oem 3: Use best available OCR engine mode (LSTM + Legacy)
            config = r'--psm 6 --oem 3'

            # Extract text with Japanese and English language support
            logger.info("Running Tesseract OCR with jpn+eng languages")
            raw_text = pytesseract.image_to_string(
                image,
                lang='jpn+eng',  # Japanese + English
                config=config
            )

            logger.info(f"Tesseract extracted text length: {len(raw_text)}")
            logger.info(f"Tesseract text preview: {raw_text[:200]}")

            # Parse structured data based on document type
            parsed_data = self._parse_response(raw_text, document_type)

            return {
                "success": True,
                "raw_text": raw_text,
                "ocr_method": "tesseract",
                **parsed_data
            }

        except Exception as e:
            logger.error(f"Tesseract OCR error: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "ocr_method": "tesseract",
                "raw_text": ""
            }

    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image for better OCR results

        Args:
            image: PIL Image

        Returns:
            Preprocessed PIL Image
        """
        try:
            import cv2

            # Convert PIL to numpy array
            img_array = np.array(image)

            # Convert to grayscale
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

            # Apply thresholding to get binary image
            # OTSU's binarization automatically finds optimal threshold
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # Denoise
            denoised = cv2.fastNlMeansDenoising(binary, None, 10, 7, 21)

            # Convert back to PIL Image
            preprocessed = Image.fromarray(denoised)

            logger.info("Image preprocessed for Tesseract")
            return preprocessed

        except Exception as e:
            logger.warning(f"Image preprocessing failed, using original: {e}")
            return image

    def _parse_response(self, raw_text: str, document_type: str) -> Dict[str, Any]:
        """Parse Tesseract response into structured data"""
        data = {
            "document_type": document_type,
            "extracted_text": raw_text
        }

        # Parse based on document type
        if document_type == "zairyu_card":
            data.update(self._parse_zairyu_card(raw_text))
        elif document_type == "license":
            data.update(self._parse_license(raw_text))
        elif document_type == "rirekisho":
            data.update(self._parse_rirekisho(raw_text))

        return data

    def _parse_zairyu_card(self, text: str) -> Dict[str, Any]:
        """Parse Zairyu Card (Residence Card) data"""
        result = {}
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        # Extract name
        for i, line in enumerate(lines):
            if '氏名' in line or 'Name' in line:
                name_match = re.search(r'氏名[：:\s]*(.+)', line)
                if name_match:
                    result['name_kanji'] = name_match.group(1).strip()
                elif i + 1 < len(lines):
                    result['name_kanji'] = lines[i + 1].strip()

            # Extract birthday
            if '生年月日' in line or 'Date of birth' in line.lower():
                date_pattern = r'(\d{4})[年/\-.](\d{1,2})[月/\-.](\d{1,2})'
                match = re.search(date_pattern, line)
                if match:
                    year, month, day = match.groups()
                    result['birthday'] = f"{year}年{int(month):02d}月{int(day):02d}日"

            # Extract nationality
            if '国籍' in line or 'Nationality' in line.lower():
                nat_match = re.search(r'国籍[：:\s]*(.+)', line)
                if nat_match:
                    result['nationality'] = self._normalize_nationality(nat_match.group(1).strip())

            # Extract visa status
            if '在留資格' in line or 'Status of residence' in line.lower():
                status_match = re.search(r'在留資格[：:\s]*(.+)', line)
                if status_match:
                    result['visa_status'] = status_match.group(1).strip()

            # Extract card number
            if 'カード番号' in line or 'Card No' in line:
                pattern = r'([A-Z]{2}\s?\d{8}\s?[A-Z]{2})'
                match = re.search(pattern, line.replace(' ', ''))
                if match:
                    result['zairyu_card_number'] = match.group(1)

        return result

    def _parse_license(self, text: str) -> Dict[str, Any]:
        """Parse Driver's License data"""
        result = {}
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        for i, line in enumerate(lines):
            # Extract name
            if '氏名' in line:
                name_match = re.search(r'氏名[：:\s]*(.+)', line)
                if name_match:
                    result['name_kanji'] = name_match.group(1).strip()
                elif i + 1 < len(lines):
                    result['name_kanji'] = lines[i + 1].strip()

            # Extract birthday
            if '生年月日' in line:
                date_pattern = r'(\d{4})[年/\-.](\d{1,2})[月/\-.](\d{1,2})'
                match = re.search(date_pattern, line)
                if match:
                    year, month, day = match.groups()
                    result['birthday'] = f"{year}年{int(month):02d}月{int(day):02d}日"

            # Extract license number
            if '免許証番号' in line or line.startswith('第'):
                number_pattern = r'第?(\d{12,13})号?'
                match = re.search(number_pattern, line)
                if match:
                    result['license_number'] = match.group(1)

        return result

    def _parse_rirekisho(self, text: str) -> Dict[str, Any]:
        """Parse Rirekisho (Resume) data - Basic extraction"""
        result = {}
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        # Extract basic fields
        for i, line in enumerate(lines):
            # Name
            if '氏名' in line:
                name_match = re.search(r'氏名[：:\s]*(.+)', line)
                if name_match:
                    result['full_name_kanji'] = name_match.group(1).strip()

            # Birthday
            if '生年月日' in line:
                date_pattern = r'(\d{4})[年/\-.](\d{1,2})[月/\-.](\d{1,2})'
                match = re.search(date_pattern, line)
                if match:
                    year, month, day = match.groups()
                    result['date_of_birth'] = f"{year}年{int(month):02d}月{int(day):02d}日"

            # Gender
            if '性別' in line:
                if '男' in line:
                    result['gender'] = '男性'
                elif '女' in line:
                    result['gender'] = '女性'

            # Phone
            phone_pattern = r'(\d{3}[-\s]?\d{4}[-\s]?\d{4})'
            phone_match = re.search(phone_pattern, line)
            if phone_match and 'phone' not in result:
                result['phone'] = phone_match.group(1)

        return result

    def _normalize_nationality(self, nationality: str) -> str:
        """Normalize nationality to Japanese format"""
        nationality_mapping = {
            'VIETNAM': 'ベトナム',
            'VIET NAM': 'ベトナム',
            'Vietnam': 'ベトナム',
            'PHILIPPINES': 'フィリピン',
            'CHINA': '中国',
            'KOREA': '韓国',
            'BRAZIL': 'ブラジル',
            'PERU': 'ペルー',
            'INDONESIA': 'インドネシア',
            'THAILAND': 'タイ',
            'MYANMAR': 'ミャンマー',
        }

        normalized = nationality_mapping.get(nationality.upper())
        if normalized:
            return normalized

        # Try partial match
        for key, value in nationality_mapping.items():
            if key.lower() in nationality.lower():
                return value

        return nationality


# Singleton instance
tesseract_ocr_service = TesseractOCRService()

__all__ = ["TesseractOCRService", "tesseract_ocr_service"]
