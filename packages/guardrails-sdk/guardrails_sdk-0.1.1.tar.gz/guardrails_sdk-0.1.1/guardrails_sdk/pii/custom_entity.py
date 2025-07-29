
from presidio_analyzer import PatternRecognizer, Pattern
import re


async def add_custom_recognizers(analyzer, recognizer_definitions: list):
    """
    Adds multiple custom recognizers dynamically based on user input.

    Args:
        analyzer: The Presidio AnalyzerEngine instance.
        recognizer_definitions (list): A list of dictionaries where each contains:
            - entity_name (str): The supported entity (e.g., "CREDIT_CARD").
            - regex (str): The regex pattern.
            - score (float): (Optional) Confidence score (default is 0.85).
            - pattern_name (str): (Optional) Custom pattern name.

    Returns:
        list: List of successfully added entity names.
    """
    added_entities = []

    for rec in recognizer_definitions:
        entity_name = rec.get("entity_name")
        regex = rec.get("regex")
        score = rec.get("score", 0.85)
        pattern_name = rec.get("pattern_name", f"{entity_name} Pattern")

        if not entity_name or not regex:
            continue  # skip invalid entries

        pattern = Pattern(name=pattern_name, regex=regex, score=score)
        recognizer = PatternRecognizer(
            supported_entity=entity_name, patterns=[pattern])
        analyzer.registry.add_recognizer(recognizer)
        added_entities.append(entity_name)

    return added_entities
