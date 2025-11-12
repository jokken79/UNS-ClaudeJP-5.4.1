"""
Azure Computer Vision OCR Service - UNS-ClaudeJP 2.0
Service for processing documents using Azure Computer Vision API
"""
import os
import base64
import logging
from typing import Dict, Any, Optional
from pathlib import Path

import numpy as np

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

from app.core.config_azure import (
    AZURE_API_VERSION,
    azure_credentials_available,
    get_azure_credentials,
)

logger = logging.getLogger(__name__)

class AzureOCRService:
    """Azure Computer Vision OCR service"""

    def __init__(self):
        self.api_version = AZURE_API_VERSION
        self._client: Optional[ComputerVisionClient] = None
        if not azure_credentials_available():
            logger.warning("Azure Computer Vision credentials are not configured. OCR requests will fail until they are set.")
        logger.info("AzureOCRService initialized")

    def _get_client(self) -> ComputerVisionClient:
        """Lazily initialize the Azure Computer Vision client."""

        if self._client is None:
            endpoint, key = get_azure_credentials()
            if not endpoint or not key:
                raise RuntimeError("Azure Computer Vision credentials are not configured")
            credentials = CognitiveServicesCredentials(key)
            self._client = ComputerVisionClient(endpoint, credentials)
        return self._client

    def process_document(self, file_path: str, document_type: str = "zairyu_card") -> Dict[str, Any]:
        """
        Process document image with Azure Computer Vision OCR

        Args:
            file_path: Path to image file
            document_type: Type of document (zairyu_card, rirekisho, license, etc.)

        Returns:
            Dictionary with extracted data
        """
        try:
            logger.info(f"Processing document: {file_path}, type: {document_type}")

            # Read image file
            with open(file_path, 'rb') as image:
                image_data = image.read()

            # Process with Azure Computer Vision
            result = self._process_with_azure(image_data, document_type)

            logger.info(f"Document processed successfully: {document_type}")
            return result

        except RuntimeError as err:
            logger.error("Azure OCR service is not configured: %s", err)
            return {
                "success": False,
                "error": str(err),
                "raw_text": "",
            }
        except Exception as e:
            logger.error(f"Error processing document: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "raw_text": f"Error: {str(e)}"
            }

    def process_timer_card(self, file_path: str) -> Dict[str, Any]:
        """
        Process timer card PDF/image with Azure Computer Vision OCR

        Args:
            file_path: Path to PDF or image file

        Returns:
            Dictionary with success status and list of timer card records
        """
        try:
            logger.info(f"Processing timer card: {file_path}")

            # Read file
            with open(file_path, 'rb') as f:
                file_data = f.read()

            # Process with Azure Computer Vision Read API (supports both images and PDFs)
            raw_text = self._extract_text_from_file(file_data)

            logger.info(f"Timer card - Extracted text length: {len(raw_text)}")
            logger.info(f"Timer card - Text preview: {raw_text[:500]}")

            # Parse timer card data
            records = self._parse_timer_card(raw_text)

            logger.info(f"Timer card - Parsed {len(records)} records")

            return {
                "success": True,
                "raw_text": raw_text,
                "records": records,
                "total_records": len(records)
            }

        except RuntimeError as err:
            logger.error(f"Azure OCR service is not configured: {err}")
            return {
                "success": False,
                "error": str(err),
                "raw_text": "",
                "records": []
            }
        except Exception as e:
            logger.error(f"Error processing timer card: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "raw_text": "",
                "records": []
            }

    def _extract_text_from_file(self, file_data: bytes) -> str:
        """Extract text from image or PDF using Azure Read API"""
        try:
            from io import BytesIO

            # Convert bytes to file-like object
            file_stream = BytesIO(file_data)

            # Send file for OCR processing (works for both images and PDFs)
            client = self._get_client()
            read_response = client.read_in_stream(file_stream, raw=True)
            operation_location = read_response.headers["Operation-Location"]
            operation_id = operation_location.split("/")[-1]

            # Poll for result
            import time
            while True:
                read_result = client.get_read_result(operation_id)
                if read_result.status.lower() == 'succeeded':
                    break
                elif read_result.status.lower() == 'failed':
                    raise Exception(f"OCR processing failed: {read_result.status}")
                time.sleep(1)

            # Extract text from results
            raw_text = ""
            if read_result.analyze_result.read_results:
                for text_result in read_result.analyze_result.read_results:
                    for line in text_result.lines:
                        raw_text += line.text + "\n"

            return raw_text

        except Exception as e:
            logger.error(f"Error extracting text from file: {e}", exc_info=True)
            raise

    def _parse_timer_card(self, text: str) -> list:
        """
        Parse timer card text and extract employee records

        Typical timer card format contains:
        - 氏名 (Name) or Employee Name
        - 日付 (Date) or Date
        - 出勤時間 (Clock In) or Clock In
        - 退勤時間 (Clock Out) or Clock Out
        - 休憩 (Break) or Break
        - 備考 (Notes) or Notes

        Returns list of records with employee data
        """
        import re
        from datetime import datetime

        records = []
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        logger.info(f"Timer card parsing - Total lines: {len(lines)}")

        # Pattern to detect dates (YYYY/MM/DD, YYYY-MM-DD, MM/DD, etc.)
        date_patterns = [
            r'(\d{4})[年/\-](\d{1,2})[月/\-](\d{1,2})日?',  # 2025年01月15日 or 2025/01/15
            r'(\d{1,2})[月/\-](\d{1,2})日?',  # 01/15 or 1月15日
        ]

        # Pattern to detect time (HH:MM, HH時MM分)
        time_patterns = [
            r'(\d{1,2}):(\d{2})',  # 08:30
            r'(\d{1,2})時(\d{2})分?',  # 8時30分
        ]

        # Try to find table-like structure
        current_record = {}
        employee_name = None

        for i, line in enumerate(lines):
            line_upper = line.upper()

            # Detect employee name header
            if any(keyword in line for keyword in ['氏名', 'NAME', '名前', '社員名']):
                # Name might be on same line or next line
                name_match = re.search(r'(?:氏名|NAME|名前|社員名)[：:\s]+(.+)', line, re.IGNORECASE)
                if name_match:
                    employee_name = name_match.group(1).strip()
                    logger.info(f"Found employee name: {employee_name}")
                elif i + 1 < len(lines):
                    # Check next line for name
                    next_line = lines[i + 1].strip()
                    if next_line and not any(k in next_line for k in ['日付', 'DATE', '出勤', '退勤']):
                        employee_name = next_line
                        logger.info(f"Found employee name (next line): {employee_name}")

            # Try to find date in line
            work_date = None
            for pattern in date_patterns:
                date_match = re.search(pattern, line)
                if date_match:
                    groups = date_match.groups()
                    if len(groups) == 3:  # Full date with year
                        year, month, day = groups
                        work_date = f"{year}-{int(month):02d}-{int(day):02d}"
                    elif len(groups) == 2:  # Month and day only (assume current year)
                        month, day = groups
                        current_year = datetime.now().year
                        work_date = f"{current_year}-{int(month):02d}-{int(day):02d}"
                    break

            # Try to find times in line
            times_found = []
            for pattern in time_patterns:
                for match in re.finditer(pattern, line):
                    hour, minute = match.groups()
                    times_found.append(f"{int(hour):02d}:{int(minute):02d}")

            # Try to find break minutes
            break_minutes = 0
            break_match = re.search(r'休憩[：:\s]*(\d+)', line)
            if not break_match:
                break_match = re.search(r'BREAK[：:\s]*(\d+)', line, re.IGNORECASE)
            if break_match:
                break_minutes = int(break_match.group(1))

            # If we have a date and at least one time, this might be a record line
            if work_date and len(times_found) >= 1:
                clock_in = times_found[0] if len(times_found) > 0 else None
                clock_out = times_found[1] if len(times_found) > 1 else None

                # Extract notes if present
                notes = ""
                notes_match = re.search(r'(?:備考|NOTES|メモ)[：:\s]+(.+)', line, re.IGNORECASE)
                if notes_match:
                    notes = notes_match.group(1).strip()

                record = {
                    "employee_name": employee_name or "不明",
                    "work_date": work_date,
                    "clock_in": clock_in,
                    "clock_out": clock_out,
                    "break_minutes": break_minutes,
                    "notes": notes
                }

                logger.info(f"Timer card record found: {record}")
                records.append(record)

        # If no structured records found, try alternative parsing
        if not records:
            logger.warning("No structured timer card records found. Trying alternative parsing...")
            # Could implement fallback parsing here if needed

        return records

    def _process_with_azure(self, image_data: bytes, document_type: str) -> Dict[str, Any]:
        """Process image with Azure Computer Vision API"""
        try:
            # Use Read API for OCR
            logger.info("Calling Azure Computer Vision Read API")

            # Convert bytes to file-like object
            from io import BytesIO
            image_stream = BytesIO(image_data)

            # Send image for OCR processing
            client = self._get_client()
            read_response = client.read_in_stream(image_stream, raw=True)
            operation_location = read_response.headers["Operation-Location"]
            operation_id = operation_location.split("/")[-1]
            
            # Poll for result
            while True:
                read_result = client.get_read_result(operation_id)
                if read_result.status.lower() == 'succeeded':
                    break
                elif read_result.status.lower() == 'failed':
                    raise Exception(f"OCR processing failed: {read_result.status}")
                
                # Wait before polling again
                import time
                time.sleep(1)
            
            # Extract text from results
            raw_text = ""
            if read_result.analyze_result.read_results:
                for text_result in read_result.analyze_result.read_results:
                    for line in text_result.lines:
                        raw_text += line.text + "\n"

            logger.info(f"Azure Computer Vision API response received")
            logger.info(f"Raw text length: {len(raw_text)}")
            logger.info(f"Raw text preview: {raw_text[:200] if raw_text else 'EMPTY'}")

            # Parse structured data based on document type
            parsed_data = self._parse_response(raw_text, document_type)

            # Extract photo from document
            photo_data = self._extract_photo_from_document(image_data, document_type)
            if photo_data:
                parsed_data['photo'] = photo_data

            parsed_data = self._apply_common_aliases(parsed_data)

            return {
                "success": True,
                "raw_text": raw_text,
                **parsed_data
            }

        except Exception as e:
            logger.error(f"Azure Computer Vision API error: {e}", exc_info=True)
            raise

    def _parse_response(self, raw_text: str, document_type: str) -> Dict[str, Any]:
        """Parse Azure response into structured data"""
        import re

        data = {
            "document_type": document_type,
            "extracted_text": raw_text
        }

        # Parse based on document type
        if document_type == "zairyu_card":
            data.update(self._parse_zairyu_card(raw_text))
        elif document_type == "license":
            data.update(self._parse_license(raw_text))

        return data

    def _apply_common_aliases(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add form-friendly aliases for extracted OCR data."""
        if not isinstance(data, dict):
            return data

        # Names
        if data.get('name_kanji') and not data.get('full_name_kanji'):
            data['full_name_kanji'] = data['name_kanji']
        if data.get('name_kana') and not data.get('full_name_kana'):
            data['full_name_kana'] = data['name_kana']
        if data.get('name_roman') and not data.get('full_name_roman'):
            data['full_name_roman'] = data['name_roman']

        # Dates
        if data.get('birthday') and not data.get('date_of_birth'):
            data['date_of_birth'] = data['birthday']
        if data.get('zairyu_expire_date') and not data.get('residence_expiry'):
            data['residence_expiry'] = data['zairyu_expire_date']
        if data.get('license_expire_date') and not data.get('license_expiry'):
            data['license_expiry'] = data['license_expire_date']

        # Identification numbers
        if data.get('zairyu_card_number') and not data.get('residence_card_number'):
            data['residence_card_number'] = data['zairyu_card_number']

        # Status fields
        if data.get('visa_status') and not data.get('residence_status'):
            data['residence_status'] = data['visa_status']

        # Address aliases
        if data.get('address'):
            data.setdefault('current_address', data['address'])
        if data.get('banchi') and not data.get('address_banchi'):
            data['address_banchi'] = data['banchi']
        if data.get('building') and not data.get('address_building'):
            data['address_building'] = data['building']

        # Photo
        if data.get('photo') and not data.get('photo_url'):
            data['photo_url'] = data['photo']

        return data

    def _parse_zairyu_card(self, text: str) -> Dict[str, Any]:
        """Parse Zairyu Card (Residence Card) data"""
        import re
        result = {}
        raw_lines = [line.replace('\u3000', ' ') for line in text.split('\n')]
        lines = [line.strip() for line in raw_lines if line.strip()]
        normalized_lines = [re.sub(r'\s+', '', line) for line in lines]
        
        # --- DATE PARSING - JAPANESE FORMAT YYYY年MM月DD日 ---
        date_patterns = [
            r'(\d{4})[年/\-\.](\d{1,2})[月/\-\.](\d{1,2})日?',
            r'(\d{4})[/\-\.](\d{1,2})[/\-\.](\d{1,2})'
        ]
        all_dates = []
        for line in lines:
            for pattern in date_patterns:
                for match in re.finditer(pattern, line):
                    try:
                        year, month, day = [int(g) for g in match.groups()]
                        if 1 <= month <= 12 and 1 <= day <= 31:
                            # JAPANESE FORMAT: YYYY年MM月DD日
                            formatted_date = f"{year}年{month:02d}月{day:02d}日"
                            all_dates.append(formatted_date)
                            logger.info(f"OCR - Found date: {formatted_date}")
                    except (ValueError, IndexError):
                        continue

        if all_dates:
            result['birthday'] = all_dates[0]
            logger.info(f"OCR - Set birthday: {result['birthday']}")
            if len(all_dates) > 1:
                result['zairyu_expire_date'] = all_dates[-1]
                logger.info(f"OCR - Set zairyu expiry: {result['zairyu_expire_date']}")

        # --- MAIN PARSING LOOP ---
        for i, line in enumerate(lines):
            normalized_line = normalized_lines[i]
            normalized_upper = normalized_line.upper()
            # Name (detect both Kanji and Roman)
            if 'name_kanji' not in result and any(keyword in line for keyword in ['氏名', 'Name']):
                name_match = re.search(r'氏名[：:\s]*(.+)', line)
                if name_match and len(name_match.group(1).strip()) > 1:
                    name_text = name_match.group(1).strip()
                    # Check if it's Roman letters (all uppercase or mixed case English)
                    if re.match(r'^[A-Z][A-Z\s]+$', name_text):
                        result['name_roman'] = name_text
                        # AUTO-CONVERT to Katakana
                        result['name_kana'] = self._convert_to_katakana(name_text)
                        # ALSO set name_kanji so frontend displays the name
                        result['name_kanji'] = name_text
                        logger.info(f"OCR - Detected Roman name: {name_text}, converted to: {result['name_kana']}")
                    else:
                        result['name_kanji'] = name_text
                elif i + 1 < len(lines) and not any(k in lines[i+1] for k in ['生年月日', '国籍', '性別']):
                    name_text = lines[i+1].strip()
                    # Check if it's Roman letters
                    if re.match(r'^[A-Z][A-Z\s]+$', name_text):
                        result['name_roman'] = name_text
                        result['name_kana'] = self._convert_to_katakana(name_text)
                        # ALSO set name_kanji so frontend displays the name
                        result['name_kanji'] = name_text
                        logger.info(f"OCR - Detected Roman name: {name_text}, converted to: {result['name_kana']}")
                    else:
                        result['name_kanji'] = name_text

            # Gender
            if 'gender' not in result and any(keyword in line for keyword in ['性別', 'Gender']):
                if '男' in line or 'Male' in line: result['gender'] = '男性'
                elif '女' in line or 'Female' in line: result['gender'] = '女性'

            # Nationality
            if 'nationality' not in result and (
                '国籍' in normalized_line or 'NATIONALITY' in normalized_upper or '地域' in normalized_line
            ):
                nat_match = re.search(r'国籍[・：:\s]*(.+)', line)
                if nat_match and nat_match.group(1).strip():
                    result['nationality'] = self._normalize_nationality(nat_match.group(1).strip())

            # Address
            if 'address' not in result and any(keyword in line for keyword in ['住居地', 'Address']):
                addr_match = re.search(r'住居地[：:\s]*(.+)', line)
                if addr_match and addr_match.group(1).strip():
                    result['address'] = addr_match.group(1).strip()
                elif i + 1 < len(lines):
                    result['address'] = lines[i+1].strip()

            # Visa Status - IMPROVED DETECTION WITH KANJI EXTRACTION
            if 'visa_status' not in result and (
                '在留資格' in normalized_line or 'STATUSOFRESIDENCE' in normalized_upper or 'STATUS' in normalized_upper or '資格' in normalized_line
            ):
                # First, try to extract status from same line
                status_match = re.search(r'在留資格[：:\s]*(.+)', line)
                if status_match and status_match.group(1).strip():
                    visa_text = status_match.group(1).strip()
                    # Remove English translation if present (e.g., "技能実習 Technical Intern Training")
                    visa_text = re.sub(r'\s+[A-Za-z]+.*$', '', visa_text).strip()
                    # Clean up visa status (remove dates, numbers at end)
                    visa_text = re.sub(r'\d{4}[年/\-].*$', '', visa_text).strip()
                    if visa_text and len(visa_text) > 2:
                        result['visa_status'] = visa_text
                        logger.info(f"OCR - Detected visa status (same line): {visa_text}")
                # If not found, check next lines (within 3 lines)
                elif i + 1 < len(lines):
                    for offset in range(1, 4):
                        if i + offset >= len(lines):
                            break
                        candidate_line = lines[i + offset].strip()
                        if not candidate_line:
                            continue
                        # Skip if it's just the English header
                        if 'STATUS' in candidate_line.upper() and not any(jp in candidate_line for jp in ['在留', '資格']):
                            continue
                        # Remove English text (keep only Japanese Kanji)
                        visa_text = re.sub(r'\s+[A-Za-z]+.*$', '', candidate_line).strip()
                        # Clean up and validate
                        visa_text = re.sub(r'\d{4}[年/\-].*$', '', visa_text).strip()
                        if visa_text and len(visa_text) > 2 and not any(skip in visa_text for skip in ['Address', '住所', '番号', '在留期間', 'Period', 'PERIOD']):
                            result['visa_status'] = visa_text
                            logger.info(f"OCR - Detected visa status (next line +{offset}): {visa_text}")
                            break

            # Residence Period (在留期間) - IMPROVED DETECTION
            if 'visa_period' not in result and any(keyword in normalized_line for keyword in ['在留期間', 'PERIODOFSTAY', 'PERIOD']):
                # First, try to extract period from same line
                # Patterns: "在留期間 3年" or "在留期間(満了日) 2028年05月19日" or "在留期間: 5年"
                period_match = re.search(r'在留期間[：:\s(（満了日）]*(.+)', line)
                if period_match and period_match.group(1).strip():
                    period_text = period_match.group(1).strip()
                    # Remove English text
                    period_text = re.sub(r'[A-Za-z\s]+', '', period_text)
                    # Common periods: 3年, 5年, 1年, 6ヶ月, etc.
                    if re.search(r'\d+[年ヶか月]', period_text):
                        # Extract just the period part (e.g., "3年" from "3年(2028年05月19日)")
                        clean_period = re.search(r'(\d+[年ヶか月]+)', period_text)
                        if clean_period:
                            result['visa_period'] = clean_period.group(1)
                            logger.info(f"OCR - Detected residence period (same line): {result['visa_period']}")
                # If not found, check next lines (within 3 lines)
                elif i + 1 < len(lines):
                    for offset in range(1, 4):
                        if i + offset >= len(lines):
                            break
                        candidate_line = lines[i + offset].strip()
                        if not candidate_line:
                            continue
                        # Skip if it's just English header
                        if re.match(r'^[A-Za-z\s]+$', candidate_line):
                            continue
                        # Remove English text
                        period_text = re.sub(r'[A-Za-z\s]+', '', candidate_line)
                        # Validate it looks like a period (e.g., "3年" or "5ヶ月")
                        if re.search(r'\d+[年ヶか月]', period_text):
                            # Extract just the period part
                            clean_period = re.search(r'(\d+[年ヶか月]+)', period_text)
                            if clean_period:
                                result['visa_period'] = clean_period.group(1)
                                logger.info(f"OCR - Detected residence period (next line +{offset}): {result['visa_period']}")
                                break

            # Card Number
            if 'zairyu_card_number' not in result and any(keyword in line for keyword in ['カード番号', '番号', 'Card No']):
                pattern = r'([A-Z]{2}\s?\d{8}\s?[A-Z]{2})'
                match = re.search(pattern, line.replace(' ', ''))
                if match:
                    result['zairyu_card_number'] = match.group(1)

        # --- FALLBACKS & POST-PROCESSING ---

        # Additional Visa Status fallback scanning entire text
        if 'visa_status' not in result:
            combined_text = '\n'.join(lines)
            combined_text_clean = combined_text.replace('\u3000', ' ')
            status_pattern = re.compile(r'(?:在留資格|Status of residence|STATUS OF RESIDENCE)[：:\s]*([^\n]+)', re.IGNORECASE)
            status_match = status_pattern.search(combined_text_clean)
            if status_match:
                candidate_status = re.sub(r'\d{4}[年/\-].*$', '', status_match.group(1)).strip()
                if candidate_status:
                    result['visa_status'] = candidate_status
                    logger.info(f"OCR - Visa status fallback extraction: {candidate_status}")
            else:
                for idx, line in enumerate(lines):
                    if any(keyword in line for keyword in ['在留資格', 'Status of residence', 'STATUS OF RESIDENCE']):
                        for offset in range(1, 4):
                            if idx + offset >= len(lines):
                                break
                            candidate_line = lines[idx + offset].strip()
                            if not candidate_line:
                                continue
                            if re.search(r'(在留期間|PERIOD OF STAY)', candidate_line, re.IGNORECASE):
                                continue
                            clean_candidate = re.sub(r'\d{4}[年/\-].*$', '', candidate_line).strip()
                            if clean_candidate:
                                result['visa_status'] = clean_candidate
                                logger.info(f"OCR - Visa status fallback (next lines): {clean_candidate}")
                                break
                        if 'visa_status' in result:
                            break

        # Nationality Fallback
        if 'nationality' not in result:
            normalized_nat = self._normalize_nationality(text)
            if normalized_nat != text: result['nationality'] = normalized_nat
        
        # Address Component Parsing
        if 'address' in result:
            address_components = self._parse_japanese_address(result['address'])
            result.update(address_components)
            main_address_parts = [
                address_components.get('prefecture', ''),
                address_components.get('city', ''),
                address_components.get('ward', ''),
                address_components.get('district', '')
            ]
            # Overwrite full address with just the main parts, before banchi
            if any(main_address_parts):
                result['address'] = ''.join(main_address_parts).strip()

        if result.get('visa_status') and 'residence_status' not in result:
            result['residence_status'] = result['visa_status']
        if result.get('birthday') and 'date_of_birth' not in result:
            result['date_of_birth'] = result['birthday']
        if result.get('zairyu_expire_date') and 'residence_expiry' not in result:
            result['residence_expiry'] = result['zairyu_expire_date']
        if result.get('zairyu_card_number') and 'residence_card_number' not in result:
            result['residence_card_number'] = result['zairyu_card_number']

        if result.get('name_kanji') and 'full_name_kanji' not in result:
            result['full_name_kanji'] = result['name_kanji']
        if result.get('name_kana') and 'full_name_kana' not in result:
            result['full_name_kana'] = result['name_kana']
        if result.get('name_roman') and 'full_name_roman' not in result:
            result['full_name_roman'] = result['name_roman']

        if result.get('address'):
            result.setdefault('current_address', result['address'])

        return result

    def _parse_license(self, text: str) -> Dict[str, Any]:
        """Parse Driver's License (Menkyosho) data"""
        import re

        result = {}
        raw_lines = [line.replace('\u3000', ' ') for line in text.split('\n')]
        lines = [line.strip() for line in raw_lines if line.strip()]

        for i, line in enumerate(lines):
            line_clean = line.strip()
            line_normalized = re.sub(r'\s+', '', line_clean)
            line_upper = line_clean.upper()

            # Extract name (氏名)
            if '氏名' in line or 'Name' in line:
                name_match = re.search(r'氏名[：:\s]*(.+)', line)
                if name_match:
                    result['name_kanji'] = name_match.group(1).strip()
                elif i + 1 < len(lines):
                    result['name_kanji'] = lines[i + 1].strip()

            # Extract name kana (フリガナ)
            if 'フリガナ' in line or '振り仮名' in line_normalized or 'FURIGANA' in line_upper:
                kana_match = re.search(r'(?:フリガナ|ふりがな|FURIGANA)[：:\s]*(.+)', line)
                if kana_match:
                    result['name_kana'] = kana_match.group(1).strip()
                elif i + 1 < len(lines):
                    result['name_kana'] = lines[i + 1].strip()

            # Extract date of birth (生年月日) - JAPANESE FORMAT
            if '生年月日' in line or 'BIRTH' in line_upper:
                date_pattern = r'(\d{4})[年/\-.](\d{1,2})[月/\-.](\d{1,2})'
                match = re.search(date_pattern, line)
                if match:
                    year, month, day = match.groups()
                    # JAPANESE FORMAT: YYYY年MM月DD日
                    result['birthday'] = f"{year}年{int(month):02d}月{int(day):02d}日"
                    logger.info(f"OCR - Detected birthday (license): {result['birthday']}")

            # Extract license number (免許証番号)
            if '免許証番号' in line or line_normalized.startswith('第'):
                # License numbers: 第1234567890123号
                number_pattern = r'第?(\d{12,13})号?'
                match = re.search(number_pattern, line)
                if match:
                    result['license_number'] = match.group(1)

            # Extract license type (免許の種類)
            if '免許の種類' in line or '種類' in line:
                # Common types: 普通, 大型, 中型, 準中型, 大特, 大自二, 普自二, 小特, 原付
                types = []
                for license_type in ['大型', '中型', '準中型', '普通', '大特', '大自二', '普自二', '小特', '原付']:
                    if license_type in line or (i + 1 < len(lines) and license_type in lines[i + 1]):
                        types.append(license_type)
                if types:
                    result['license_type'] = ', '.join(types)

            # Extract expiry date (有効期限) - JAPANESE FORMAT
            if '有効期限' in line or 'EXPIRY' in line_upper or '期限' in line:
                date_pattern = r'(\d{4})[年/\-.](\d{1,2})[月/\-.](\d{1,2})'
                match = re.search(date_pattern, line)
                if match:
                    year, month, day = match.groups()
                    # JAPANESE FORMAT: YYYY年MM月DD日
                    result['license_expire_date'] = f"{year}年{int(month):02d}月{int(day):02d}日"
                    logger.info(f"OCR - Detected license expiry: {result['license_expire_date']}")

            # Extract address (住所)
            if '住所' in line or 'ADDRESS' in line_upper:
                addr_match = re.search(r'住所[：:\s]*(.+)', line)
                if addr_match:
                    result['address'] = addr_match.group(1).strip()
                elif i + 1 < len(lines):
                    # Address might be on next lines
                    address_parts = []
                    for j in range(i + 1, min(i + 4, len(lines))):
                        if lines[j].strip() and not any(key in lines[j] for key in ['氏名', '生年月日', '交付']):
                            address_parts.append(lines[j].strip())
                        else:
                            break
                    if address_parts:
                        result['address'] = ' '.join(address_parts)

            # Extract issuing date (交付年月日) - JAPANESE FORMAT
            if '交付' in line or 'ISSUED' in line_upper:
                date_pattern = r'(\d{4})[年/\-.](\d{1,2})[月/\-.](\d{1,2})'
                match = re.search(date_pattern, line)
                if match:
                    year, month, day = match.groups()
                    # JAPANESE FORMAT: YYYY年MM月DD日
                    result['license_issue_date'] = f"{year}年{int(month):02d}月{int(day):02d}日"
                    logger.info(f"OCR - Detected license issue date: {result['license_issue_date']}")

        # Fallbacks using entire text
        if 'license_number' not in result:
            number_pattern = re.compile(r'第\s?(\d{12,13})号?')
            number_match = number_pattern.search(''.join(lines))
            if number_match:
                result['license_number'] = number_match.group(1)

        if 'license_expire_date' not in result:
            date_pattern = re.compile(r'有効期限[：:\s]*(\d{4})[年/\-.](\d{1,2})[月/\-.](\d{1,2})')
            date_match = date_pattern.search(' '.join(lines))
            if date_match:
                year, month, day = date_match.groups()
                result['license_expire_date'] = f"{year}-{int(month):02d}-{int(day):02d}"

        if 'address' in result:
            address_components = self._parse_japanese_address(result['address'])
            result.update(address_components)
            result.setdefault('current_address', result['address'])

        if result.get('birthday') and 'date_of_birth' not in result:
            result['date_of_birth'] = result['birthday']
        if result.get('name_kanji') and 'full_name_kanji' not in result:
            result['full_name_kanji'] = result['name_kanji']
        if result.get('name_kana') and 'full_name_kana' not in result:
            result['full_name_kana'] = result['name_kana']
        if result.get('license_expire_date') and 'license_expiry' not in result:
            result['license_expiry'] = result['license_expire_date']

        return result

    def _convert_to_katakana(self, text: str) -> str:
        """Convert romaji text to Katakana using pykakasi library"""
        try:
            import pykakasi

            # Initialize pykakasi converter
            kks = pykakasi.kakasi()

            # Convert romaji to katakana
            # pykakasi works best with proper capitalization
            result = kks.convert(text)

            # Extract katakana from result
            katakana_parts = []
            for item in result:
                # pykakasi returns dict with 'kana' key containing katakana
                if 'kana' in item:
                    katakana_parts.append(item['kana'])
                elif 'orig' in item:
                    # Fallback to original if conversion failed
                    katakana_parts.append(item['orig'])

            katakana_result = ''.join(katakana_parts)

            logger.info(f"OCR - Converted '{text}' to katakana: '{katakana_result}'")
            return katakana_result

        except ImportError:
            logger.warning("OCR - pykakasi not available, using fallback conversion")
            # Fallback to manual conversion if pykakasi not installed
            return self._convert_to_katakana_fallback(text)
        except Exception as e:
            logger.error(f"OCR - Error converting to katakana: {e}")
            return self._convert_to_katakana_fallback(text)

    def _convert_to_katakana_fallback(self, text: str) -> str:
        """Fallback conversion using manual mapping"""
        import re

        # Manual conversion map for common names when pykakasi fails
        conversion_map = {
            # Portuguese/Brazilian names (common)
            'DIEGO': 'ディエゴ',
            'BOLZAN': 'ボルザン',
            'PASSOS': 'パソス',
            'DOS': 'ドス',
            'DA': 'ダ',
            'DE': 'デ',
            'SILVA': 'シルバ',
            'SANTOS': 'サントス',
            'OLIVEIRA': 'オリベイラ',
            'SOUZA': 'ソウザ',
            'LIMA': 'リマ',
            'COSTA': 'コスタ',
            'PEREIRA': 'ペレイラ',
            'RODRIGUES': 'ロドリゲス',
            'FERNANDES': 'フェルナンデス',
            'GOMES': 'ゴメス',
            'MARTINS': 'マルティンス',
            'ALVES': 'アルベス',
            'RIBEIRO': 'リベイロ',
            'CARVALHO': 'カルバーリョ',
            'CARLOS': 'カルロス',
            'JOSE': 'ホセ',
            'MARIA': 'マリア',
            'JOAO': 'ジョアン',
            'PEDRO': 'ペドロ',
            'PAULO': 'パウロ',
            'LUCAS': 'ルカス',
            'RAFAEL': 'ラファエル',
            'GABRIEL': 'ガブリエル',
            'FERNANDO': 'フェルナンド',
            'RICARDO': 'リカルド',
            'ANDERSON': 'アンデルソン',
            'ROBERTO': 'ロベルト',

            # Vietnamese names (from your examples)
            'MAI': 'マイ',
            'TU': 'トゥ',
            'ANH': 'アン',
            'NGUYEN': 'グエン',
            'VAN': 'ヴァン',
            'QUY': 'クイ',
            'VU': 'ヴゥ',
            'THI': 'ティ',
            'SAU': 'サウ',
            'TUAN': 'トゥアン',
            'VIET': 'ヴィエット',
            'CUONG': 'クオン',
            'LUU': 'ルウ',
            'PHUONG': 'フォン',
            'HOAI': 'ホアイ',
            
            # Common Vietnamese name components
            'MINH': 'ミン',
            'THANH': 'タン',
            'HUY': 'フイ',
            'DUC': 'ドゥック',
            'HOANG': 'ホアン',
            'TRUNG': 'チュン',
            'AN': 'アン',
            'BINH': 'ビン',
            'NAM': 'ナム',
            'NU': 'ヌ',
            'HA': 'ハ',
            'LINH': 'リン',
            'GIANG': 'ジャン',
            'QUYNH': 'クイン',
            'TRANG': 'チャン',
            'PHUC': 'フック',
            'SON': 'ソン',
            'LAM': 'ラム',
            'TAM': 'タム',
            'NGOC': 'ゴック',
            'THAO': 'タオ',
            'THUY': 'トゥイ',
            'MY': 'ミー',
            'LY': 'リー',
            
            # Common Japanese names
            'YAMADA': 'ヤマダ',
            'TARO': 'タロウ',
            'HANAKO': 'ハナコ',
            'SUZUKI': 'スズキ',
            'SATOU': 'サトウ',
            'TANAKA': 'タナカ',
            'WATANABE': 'ワタナベ',
            'ITO': 'イトウ',
            'YAMAMOTO': 'ヤマモト',
            'NAKAMURA': 'ナカムラ',
            'KOBAYASHI': 'コバヤシ',
            'SAITOU': 'サイトウ',
            'KATO': 'カトウ',
            'YOSHIDA': 'ヨシダ',
            'YAMASHITA': 'ヤマシタ',
            'HASHIMOTO': 'ハシモト',
            'FUJITA': 'フジタ',
            'OGAWA': 'オガワ',
            'MORI': 'モリ',
            'ISHIDA': 'イシダ',
            'MATSUMOTO': 'マツモト',
            'HAYASHI': 'ハヤシ',
            'KIMURA': 'キムラ',
            
            # Special character combinations
            'PH': 'フ',
            'TH': 'ト',
            'QU': 'ク',
            'NG': 'ング',
            'NH': 'ニ',
            'CH': 'チ'
        }
        
        # Try to convert known patterns
        result = text.upper()  # Convert to uppercase for matching
        
        # Handle special Vietnamese combinations first
        for romaji, katakana in conversion_map.items():
            result = result.replace(romaji, katakana)
        
        # Handle individual character conversions for remaining text
        char_map = {
            'A': 'ア', 'B': 'ビ', 'C': 'シ', 'D': 'ド', 'E': 'エ',
            'F': 'フ', 'G': 'グ', 'H': 'ハ', 'I': 'イ', 'J': 'ジ',
            'K': 'ク', 'L': 'ル', 'M': 'ム', 'N': 'ン', 'O': 'オ',
            'P': 'プ', 'Q': 'ク', 'R': 'ル', 'S': 'ス', 'T': 'ト',
            'U': 'ウ', 'V': 'ヴ', 'W': 'ワ', 'X': 'クス', 'Y': 'ヤ',
            'Z': 'ズ'
        }
        
        # Convert any remaining characters
        final_result = ''
        for char in result:
            if char in char_map:
                final_result += char_map[char]
            else:
                final_result += char
        
        return final_result

    def _normalize_nationality(self, nationality: str) -> str:
        """Normalize nationality to Japanese format"""
        nationality_mapping = {
            'VIETNAM': 'ベトナム',
            'VIET NAM': 'ベトナム',
            'Vietnam': 'ベトナム',
            'Viet Nam': 'ベトナム',
            'vietnan': 'ベトナム',  # Common OCR error
            'VIETNAN': 'ベトナム',
            'PHILIPPINES': 'フィリピン',
            'Philippines': 'フィリピン',
            'CHINA': '中国',
            'China': '中国',
            'KOREA': '韓国',
            'Korea': '韓国',
            'BRAZIL': 'ブラジル',
            'Brazil': 'ブラジル',
            'PERU': 'ペルー',
            'Peru': 'ペルー',
            'INDONESIA': 'インドネシア',
            'Indonesia': 'インドネシア',
            'THAILAND': 'タイ',
            'Thailand': 'タイ',
            'MYANMAR': 'ミャンマー',
            'Myanmar': 'ミャンマー',
            'CAMBODIA': 'カンボジア',
            'Cambodia': 'カンボジア',
            'NEPAL': 'ネパール',
            'Nepal': 'ネパール',
            'MONGOLIA': 'モンゴル',
            'Mongolia': 'モンゴル',
            'BANGLADESH': 'バングラデシュ',
            'Bangladesh': 'バングラデシュ',
            'SRI LANKA': 'スリランカ',
            'Sri Lanka': 'スリランカ'
        }
        
        # Try exact match first
        normalized = nationality_mapping.get(nationality.upper())
        if normalized:
            return normalized
        
        # Try partial match
        for key, value in nationality_mapping.items():
            if key.lower() in nationality.lower() or nationality.lower() in key.lower():
                return value
        
        # Return original if no mapping found
        return nationality

    def _parse_japanese_address(self, address: str) -> Dict[str, str]:
        """Parse Japanese address into components"""
        import re
        
        result = {
            'postal_code': '',
            'prefecture': '',
            'city': '',
            'ward': '',
            'district': '',
            'banchi': '',
            'building': ''
        }
        
        # Extract postal code if present
        postal_match = re.search(r'(\d{3}-\d{4})', address)
        if postal_match:
            result['postal_code'] = postal_match.group(1)
        
        # Extract prefecture
        prefectures = ['北海道', '青森県', '岩手県', '宮城県', '秋田県', '山形県', '福島県',
                      '茨城県', '栃木県', '群馬県', '埼玉県', '千葉県', '東京都', '神奈川県',
                      '新潟県', '富山県', '石川県', '福井県', '山梨県', '長野県', '岐阜県',
                      '静岡県', '愛知県', '三重県', '滋賀県', '京都府', '大阪府', '兵庫県',
                      '奈良県', '和歌山県', '鳥取県', '島根県', '岡山県', '広島県', '山口県',
                      '徳島県', '香川県', '愛媛県', '高知県', '福岡県', '佐賀県', '長崎県',
                      '熊本県', '大分県', '宮崎県', '鹿児島県', '沖縄県']
        
        for prefecture in prefectures:
            if prefecture in address:
                result['prefecture'] = prefecture
                # Remove prefecture from address for further processing
                address = address.replace(prefecture, '', 1)
                break
        
        # Split remaining address by common delimiters
        # Pattern: 市区町村 + 番地 + 建物名
        # Example: 名古屋市東区徳川2-18-18
        #          city  ward district banchi
        
        # Match patterns like "名古屋市東区徳川"
        city_ward_pattern = r'([^0-9]+[市区町村])([^0-9]+[区郡]?[^0-9]*)([^0-9]+)?'
        match = re.search(city_ward_pattern, address)
        if match:
            result['city'] = match.group(1)
            result['ward'] = match.group(2) if match.group(2) else ''
            result['district'] = match.group(3) if match.group(3) else ''
        
        # Extract banchi (番地) - numbers after district
        # Handle patterns like "908番地1の2" or "908-1-2"
        banchi_patterns = [
            r'(\d+)番地(\d+)の(\d+)',  # 908番地1の2
            r'(\d+)[−\-\s](\d+)[−\-\s](\d+)',  # 908-1-2
            r'(\d+)[−\-\s]*(\d+)[−\-\s]*(\d*)',  # More flexible
        ]
        
        for pattern in banchi_patterns:
            banchi_match = re.search(pattern, address)
            if banchi_match:
                groups = banchi_match.groups()
                # Format as XXX番地XのX
                if groups[2]:  # Third group exists
                    result['banchi'] = f"{groups[0]}番地{groups[1]}の{groups[2]}"
                else:
                    result['banchi'] = f"{groups[0]}番地{groups[1]}"
                logger.info(f"OCR - Parsed banchi: {result['banchi']}")
                break
        
        # Extract building name (if any) - usually after numbers
        # Look for patterns like "メゾン徳川101号室"
        building_patterns = [
            r'(\d+[−\-\s]*\d+[−\-\s]*\d*\s*)([^0-9]+号室[^0-9]*)',  # Building with room number
            r'(\d+[−\-\s]*\d+[−\-\s]*\d*\s*)([^0-9]+)',  # Building name after numbers
        ]
        
        for pattern in building_patterns:
            building_match = re.search(pattern, address)
            if building_match:
                building_parts = building_match.groups()
                if len(building_parts) > 1:
                    building_name = building_parts[1].strip()
                    if building_name != "番地":
                        result['building'] = building_name
                        logger.info(f"OCR - Parsed building: {result['building']}")
                        break
        
        return result

    def _extract_photo_from_document(self, image_data: bytes, document_type: str) -> Optional[str]:
        """Extract photo from document image using enhanced face detection."""
        try:
            # Intentar usar el nuevo servicio mejorado de detección facial
            try:
                from app.services.face_detection_service import face_detection_service
                logger.info("OCR - Usando servicio mejorado de detección facial")
                
                result = face_detection_service.extract_face_from_document(image_data, document_type)
                if result:
                    logger.info("OCR - ✅ Rostro extraído exitosamente con nuevo servicio")
                    return result
                else:
                    logger.warning("OCR - Nuevo servicio no detectó rostro, usando método original")
                    
            except ImportError:
                logger.warning("OCR - Servicio de detección facial no disponible, usando método original")
            except Exception as e:
                logger.warning(f"OCR - Error con nuevo servicio: {e}, usando método original")
            
            # Método original como fallback (sin cambios para mantener compatibilidad)
            return self._extract_photo_original_method(image_data, document_type)
            
        except Exception as e:
            logger.error(f"Error extracting photo with face detection: {e}", exc_info=True)
            # Fallback to returning the full image in case of any error
            import base64
            base64_image = base64.b64encode(image_data).decode('utf-8')
            return f"data:image/jpeg;base64,{base64_image}"
    
    def _extract_photo_original_method(self, image_data: bytes, document_type: str) -> Optional[str]:
        """Método original de extracción de foto mantenido como fallback"""
        try:
            import base64
            from io import BytesIO
            from PIL import Image
            import numpy as np
            import cv2

            image = Image.open(BytesIO(image_data)).convert("RGB")
            img_array = np.array(image)
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            # Correct path to the Haar Cascade file
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            if not os.path.exists(cascade_path):
                logger.error(f"Haar Cascade file not found at: {cascade_path}")
                # Fallback to fixed coordinates if cascade is missing
                return self._extract_photo_with_fixed_coordinates(img_array, document_type, image_data)

            face_cascade = cv2.CascadeClassifier(cascade_path)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))

            if len(faces) > 0:
                # Assume the largest detected face is the correct one
                (x, y, w, h) = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)[0]
                
                # Add padding to capture the whole head
                padding_y = int(h * 0.3)
                padding_x = int(w * 0.2)
                
                y1 = max(0, y - padding_y)
                y2 = min(img_array.shape[0], y + h + padding_y)
                x1 = max(0, x - padding_x)
                x2 = min(img_array.shape[1], x + w + padding_x)
                
                face_region = img_array[y1:y2, x1:x2]
                logger.info(f"OCR - ✅ Face detected at (x={x}, y={y}, w={w}, h={h}). Cropped region: y={y1}-{y2}, x={x1}-{x2}")
                
                # Resize to a standard size
                photo_image = Image.fromarray(face_region)
                photo_image = photo_image.resize((300, 400), Image.Resampling.LANCZOS)

            else:
                logger.warning(f"OCR - No face detected in {document_type}. Falling back to fixed coordinates.")
                return self._extract_photo_with_fixed_coordinates(img_array, document_type, image_data)

            buffered = BytesIO()
            photo_image.save(buffered, format="JPEG", quality=95)
            base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
            return f"data:image/jpeg;base64,{base64_image}"

        except Exception as e:
            logger.error(f"Error extracting photo with original method: {e}", exc_info=True)
            # Fallback to fixed coordinates
            try:
                import base64
                from io import BytesIO
                from PIL import Image
                import numpy as np

                image = Image.open(BytesIO(image_data)).convert("RGB")
                img_array = np.array(image)
                return self._extract_photo_with_fixed_coordinates(img_array, document_type, image_data)
            except Exception as e:
                # Last fallback - return full image as base64 if coordinate extraction fails
                logger.warning(f"Photo extraction with fixed coordinates failed: {e}, using full image")
                import base64
                base64_image = base64.b64encode(image_data).decode('utf-8')
                return f"data:image/jpeg;base64,{base64_image}"

    def _extract_photo_with_fixed_coordinates(self, img_array: np.ndarray, document_type: str, image_data: bytes) -> str:
        """Fallback method to extract photo using fixed coordinates."""
        try:
            import base64
            from io import BytesIO
            from PIL import Image

            height, width = img_array.shape[:2]
            face_region = None

            if document_type == "zairyu_card":
                y1 = int(height * 0.15)
                y2 = int(height * 0.60)
                x1 = int(width * 0.70)
                x2 = int(width * 0.95)
                face_region = img_array[max(0, y1):min(height, y2), max(0, x1):min(width, x2)]
                logger.info(f"OCR - Fallback to FIXED Zairyu coordinates: y={y1}-{y2}, x={x1}-{x2}")
            
            elif document_type == "license":
                y1 = int(height * 0.20)
                y2 = int(height * 0.78)
                x1 = int(width * 0.05)
                x2 = int(width * 0.35)
                face_region = img_array[max(0, y1):min(height, y2), max(0, x1):min(width, x2)]
                logger.info("OCR - Fallback to FIXED license coordinates.")

            if face_region is None or face_region.size == 0:
                logger.warning("OCR - Fixed coordinate cropping resulted in an empty image. Returning full image.")
                face_region = img_array

            photo_image = Image.fromarray(face_region)
            buffered = BytesIO()
            photo_image.save(buffered, format="JPEG", quality=90)
            base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
            return f"data:image/jpeg;base64,{base64_image}"

        except Exception as e:
            logger.error(f"Error in fallback photo extraction: {e}", exc_info=True)
            import base64
            base64_image = base64.b64encode(image_data).decode('utf-8')
            return f"data:image/jpeg;base64,{base64_image}"



# Create singleton instance
azure_ocr_service = AzureOCRService()

__all__ = ["AzureOCRService", "azure_ocr_service"]