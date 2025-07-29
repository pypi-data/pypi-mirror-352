from typing import Dict
from presidio_anonymizer.operators import Operator, OperatorType


class InstanceCounterAnonymizer(Operator):
    """
    Anonymizer which replaces the entity value
    with an instance counter per entity.
    """

    REPLACING_FORMAT = "[{entity_type}_{index}]"

    def operate(self, text: str, params: Dict = {}) -> str:
        """Anonymize the input text."""

        entity_type: str = params["entity_type"]

        # Skip MISC entity types (no anonymization for MISC)
        if entity_type == "MISC":
            return text

        # entity_mapping is a dict of dicts containing mappings per entity type
        entity_mapping: Dict[str, Dict] = params["entity_mapping"]

        # Ensure mapping exists for the current entity type
        if entity_type not in entity_mapping:
            entity_mapping[entity_type] = {}

        entity_mapping_for_type = entity_mapping[entity_type]

        # If the entity has already been encountered, reuse its mapping
        if text in entity_mapping_for_type:
            return entity_mapping_for_type[text]

        # Get the next index for this entity type
        new_index = len(entity_mapping_for_type) + 1
        new_text = self.REPLACING_FORMAT.format(
            entity_type=entity_type, index=new_index
        )

        # Store the new entity in the mapping
        entity_mapping[entity_type][text] = new_text
        return new_text

    def validate(self, params: Dict = {}) -> None:
        """Validate operator parameters."""
        if "entity_mapping" not in params:
            raise ValueError("An input Dict called `entity_mapping` is required.")
        if "entity_type" not in params:
            raise ValueError("An entity_type param is required.")

    def operator_name(self) -> str:
        return "entity_counter"

    def operator_type(self) -> OperatorType:
        return OperatorType.Anonymize