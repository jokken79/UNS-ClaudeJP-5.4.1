"""
OCR Result Weighting System - Intelligent confidence-based merging

This module provides intelligent weighting algorithms for combining OCR results
from multiple providers based on their confidence scores.

Author: Claude Code
Created: 2025-11-12
Version: 1.0
"""

from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


# Provider-specific base confidence weights
# These weights represent the reliability of each OCR provider
PROVIDER_WEIGHTS = {
    'azure': 0.5,      # Azure Computer Vision is most reliable (50% base weight)
    'easyocr': 0.3,    # EasyOCR is good for Japanese text (30% base weight)
    'tesseract': 0.2,  # Tesseract is fallback option (20% base weight)
}


def calculate_weighted_confidence(
    provider_results: Dict[str, Dict[str, Any]]
) -> float:
    """
    Calculate weighted confidence score from multiple OCR provider results.

    Uses the formula:
    weighted_confidence = Σ(provider_weight * provider_confidence) / Σ(provider_weight)

    Example:
        If Azure returns 0.9 confidence and EasyOCR returns 0.8:
        weighted = (0.5 * 0.9 + 0.3 * 0.8) / (0.5 + 0.3) = 0.87

    Args:
        provider_results: Dictionary mapping provider name to result dict
            Format: {
                'azure': {'confidence': 0.9, 'success': True, ...},
                'easyocr': {'confidence': 0.8, 'success': True, ...}
            }

    Returns:
        float: Weighted confidence score (0.0-1.0)
    """
    total_weighted_confidence = 0.0
    total_weights = 0.0

    for provider, result in provider_results.items():
        if not result or not result.get('success'):
            continue

        provider_confidence = result.get('confidence', 0.0)
        provider_weight = PROVIDER_WEIGHTS.get(provider, 0.0)

        if provider_weight > 0:
            total_weighted_confidence += provider_weight * provider_confidence
            total_weights += provider_weight

    if total_weights == 0:
        return 0.0

    return total_weighted_confidence / total_weights


def combine_field_values_weighted(
    field_name: str,
    provider_values: Dict[str, tuple[str, float]]
) -> tuple[str, float]:
    """
    Combine field values from multiple providers using confidence-based weighting.

    Selects the value with the highest confidence score, with provider weight as tiebreaker.

    Args:
        field_name: Name of the field being combined
        provider_values: Dictionary mapping provider name to (value, confidence) tuple
            Format: {
                'azure': ('田中太郎', 0.95),
                'easyocr': ('田中 太郎', 0.85),
                'tesseract': ('田中', 0.60)
            }

    Returns:
        tuple[str, float]: (best_value, weighted_confidence)

    Example:
        >>> values = {
        ...     'azure': ('田中太郎', 0.95),
        ...     'easyocr': ('田中 太郎', 0.85)
        ... }
        >>> combine_field_values_weighted('name_kanji', values)
        ('田中太郎', 0.91)  # Azure value with weighted confidence
    """
    if not provider_values:
        return ('', 0.0)

    # Calculate weighted score for each provider's value
    scored_values = []
    for provider, (value, confidence) in provider_values.items():
        provider_weight = PROVIDER_WEIGHTS.get(provider, 0.0)

        # Weighted score = provider_weight * confidence
        # This gives higher priority to values from more reliable providers
        weighted_score = provider_weight * confidence

        scored_values.append({
            'provider': provider,
            'value': value,
            'confidence': confidence,
            'weight': provider_weight,
            'weighted_score': weighted_score
        })

    # Sort by weighted_score (descending)
    scored_values.sort(key=lambda x: x['weighted_score'], reverse=True)

    # Select the best value
    best = scored_values[0]

    # Calculate final weighted confidence considering all providers
    total_weighted_confidence = sum(
        PROVIDER_WEIGHTS.get(prov, 0.0) * conf
        for prov, (val, conf) in provider_values.items()
        if val == best['value']  # Only count providers that agree
    )
    total_weights = sum(
        PROVIDER_WEIGHTS.get(prov, 0.0)
        for prov in provider_values.keys()
    )

    final_confidence = total_weighted_confidence / total_weights if total_weights > 0 else best['confidence']

    logger.debug(
        f"Field '{field_name}': Selected '{best['value']}' from {best['provider']} "
        f"(confidence: {best['confidence']:.2f}, weighted: {final_confidence:.2f})"
    )

    return (best['value'], final_confidence)


def merge_ocr_results_intelligent(
    azure_result: Optional[Dict[str, Any]] = None,
    easyocr_result: Optional[Dict[str, Any]] = None,
    tesseract_result: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Intelligently merge OCR results from multiple providers using confidence weighting.

    This function implements the improved OCR merging logic requested in [A8]:
    - Uses real confidence scores from each provider
    - Applies intelligent weighting: azure (50%) > easyocr (30%) > tesseract (20%)
    - Selects best value per field based on weighted confidence

    Args:
        azure_result: Result dictionary from Azure Computer Vision OCR
        easyocr_result: Result dictionary from EasyOCR
        tesseract_result: Result dictionary from Tesseract OCR

    Returns:
        Dict[str, Any]: Merged result with best values from all providers
            {
                'success': bool,
                'method_used': 'intelligent_hybrid',
                'confidence_score': float,  # Overall weighted confidence
                'fields': {
                    'field_name': {
                        'value': str,
                        'confidence': float,
                        'source': str  # Provider that contributed this value
                    },
                    ...
                },
                'provider_results': {
                    'azure': {...},
                    'easyocr': {...},
                    'tesseract': {...}
                }
            }

    Example:
        >>> azure = {'success': True, 'name_kanji': '田中太郎', 'confidence': 0.95}
        >>> easyocr = {'success': True, 'name_kanji': '田中 太郎', 'confidence': 0.85}
        >>> result = merge_ocr_results_intelligent(azure, easyocr)
        >>> result['fields']['name_kanji']['value']
        '田中太郎'  # Azure's value selected due to higher weighted score
    """
    provider_results = {}

    if azure_result and azure_result.get('success'):
        provider_results['azure'] = azure_result
    if easyocr_result and easyocr_result.get('success'):
        provider_results['easyocr'] = easyocr_result
    if tesseract_result and tesseract_result.get('success'):
        provider_results['tesseract'] = tesseract_result

    if not provider_results:
        return {
            'success': False,
            'method_used': 'none',
            'confidence_score': 0.0,
            'error': 'No successful OCR results to merge'
        }

    # Calculate overall weighted confidence
    overall_confidence = calculate_weighted_confidence(provider_results)

    # Collect all unique field names from all providers
    all_fields = set()
    for result in provider_results.values():
        all_fields.update(result.keys())

    # Remove metadata fields
    metadata_fields = {'success', 'confidence', 'method_used', 'error', 'document_type'}
    all_fields -= metadata_fields

    # Merge field values using intelligent weighting
    merged_fields = {}

    for field_name in all_fields:
        # Collect values from each provider with their confidences
        provider_values = {}

        for provider, result in provider_results.items():
            value = result.get(field_name)
            if value and str(value).strip():  # Only include non-empty values
                # Use field-specific confidence if available, otherwise use overall provider confidence
                field_confidence = result.get(f'{field_name}_confidence', result.get('confidence', 0.0))
                provider_values[provider] = (str(value), field_confidence)

        if provider_values:
            best_value, field_confidence = combine_field_values_weighted(field_name, provider_values)

            # Determine which provider(s) contributed this value
            sources = [
                provider for provider, (value, _) in provider_values.items()
                if value == best_value
            ]

            merged_fields[field_name] = {
                'value': best_value,
                'confidence': field_confidence,
                'source': sources[0] if len(sources) == 1 else f"consensus({','.join(sources)})"
            }

    result = {
        'success': True,
        'method_used': 'intelligent_hybrid',
        'confidence_score': overall_confidence,
        'fields': merged_fields,
        'provider_results': provider_results,
        'providers_used': list(provider_results.keys())
    }

    logger.info(
        f"Intelligent OCR merge completed: {len(merged_fields)} fields, "
        f"confidence: {overall_confidence:.2f}, "
        f"providers: {','.join(provider_results.keys())}"
    )

    return result


# Usage example for integration into hybrid_ocr_service.py:
"""
# In hybrid_ocr_service.py, replace the _combine_results method with:

from app.services.ocr_weighting import merge_ocr_results_intelligent

def _combine_results_intelligent(self, azure_result, easyocr_result, tesseract_result=None):
    '''
    Intelligently combine OCR results using confidence-based weighting.

    This replaces the old _combine_results method with the improved algorithm.
    '''
    merged = merge_ocr_results_intelligent(
        azure_result=azure_result,
        easyocr_result=easyocr_result,
        tesseract_result=tesseract_result
    )

    # Convert back to flat format for backward compatibility
    if merged['success']:
        result = {
            'success': True,
            'method_used': 'intelligent_hybrid',
            'confidence_score': merged['confidence_score']
        }

        # Extract field values from nested structure
        for field_name, field_data in merged['fields'].items():
            result[field_name] = field_data['value']
            result[f'{field_name}_confidence'] = field_data['confidence']
            result[f'{field_name}_source'] = field_data['source']

        return result

    return merged
"""
