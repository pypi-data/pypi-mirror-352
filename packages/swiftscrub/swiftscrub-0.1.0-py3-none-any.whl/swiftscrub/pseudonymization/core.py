from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine, OperatorConfig, RecognizerResult

from swiftscrub.pseudonymization.bert_recognizer import BertNERRecognizer
from swiftscrub.pseudonymization.instance_counter import InstanceCounterAnonymizer


class Pseudonymizer:
    def __init__(self):
        self.analyzer = AnalyzerEngine()
        self.anonymizer_engine = AnonymizerEngine()

        # Add custom recognizer
        self.bert_ner_recognizer = BertNERRecognizer()
        self.analyzer.registry.add_recognizer(self.bert_ner_recognizer)

        # Add custom anonymizer
        self.anonymizer_engine.add_anonymizer(InstanceCounterAnonymizer)
    
    def predict(self, text: str) -> str:
        """
        Anonymize the input text by replacing identifiable entities with generic placeholders.
        :param text: The input text to be anonymized.
        :return: Anonymized text.
        """
        if not text.strip():
            raise ValueError("Text input is required")

        # Analyze the text
        results = self.analyzer.analyze(text=text, language="en")
        if not results:
            raise ValueError("No identifiable entities found in the text")
        
        # https://github.com/microsoft/presidio/issues/1396#issuecomment-2200118662
        # Thanks Presidio team for making this so much easier!
        results = [
            RecognizerResult(
                entity_type=result.entity_type,
                start=result.start,
                end=result.end,
                score=result.score,
            )
            for result in results
        ]

        # Create an entity mapping dictionary
        entity_mapping = dict()

        # Anonymize the text
        anonymized_result = self.anonymizer_engine.anonymize(
            text,
            results,
            {
                "DEFAULT": OperatorConfig("entity_counter", {"entity_mapping": entity_mapping})
            },
        )

        return anonymized_result.text
