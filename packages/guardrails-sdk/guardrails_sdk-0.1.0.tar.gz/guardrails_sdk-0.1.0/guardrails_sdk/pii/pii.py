
#!/usr/bhanuteja/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 07 21:19:15 2025

@author: viswateja.rayapaneni

Author: viswateja.rayapaneni
Description: 
    A script to detect and anonymize PII from text using Presidio.
    Custom recognizers added for SSN and street addresses.
"""

from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from .custom_entity import add_custom_recognizers

# Initialize Presidio Analyzer and Anonymizer engines
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()


# Define confidence score threshold for detected entities
# CONFIDENCE_THRESHOLD = 0.5


async def analyze_and_mask_text(text: str, entities: list, custom_entitie_list: list, CONFIDENCE_THRESHOLD: float) -> dict:
    """
    Analyze input text for specified PII entities and return masked output along with details.

    Args:
        text (str): The input text to process.
        entities (list): List of PII entity labels to look for.

    Returns:
        dict: Contains masked text, found entities, and metadata.
    """

    if len(custom_entitie_list) > 0:
        # User defined/Custom recognizer
        custom_entities = await add_custom_recognizers(analyzer, custom_entitie_list)

        # Get custom entities name
        custom_entitie_names = list(
            map(lambda rec: rec['entity_name'], custom_entitie_list))

        list_of_entities = custom_entitie_names+entities
    else:
        list_of_entities = entities
    # Analyze text for specified PII entities
    results = analyzer.analyze(
        text=text,
        entities=list_of_entities,
        language="en"
    )

    # Filter results based on confidence score
    filtered_results = [
        res for res in results if res.score >= CONFIDENCE_THRESHOLD]

    # Anonymize the text using the filtered results
    masked_result = anonymizer.anonymize(
        text=text, analyzer_results=filtered_results)

    return {
        "pii_found": True if filtered_results else False,

        "masked_text": masked_result.text
    }
