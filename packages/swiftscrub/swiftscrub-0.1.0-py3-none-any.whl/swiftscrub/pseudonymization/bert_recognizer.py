from presidio_analyzer import RecognizerResult, EntityRecognizer
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers.pipelines import pipeline


class BertNERRecognizer(EntityRecognizer):
    def __init__(self, model_name="dslim/bert-base-NER", supported_entities=None):
        super().__init__(supported_entities=supported_entities or ["ORG"])
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForTokenClassification.from_pretrained(self.model_name)
        self.nlp_pipeline = pipeline("ner", model=self.model, tokenizer=self.tokenizer)

    def load(self):
        pass  # Model loading done in init

    def analyze(self, text, entities, nlp_artifacts=None):
        results = []
        ner_results = self.nlp_pipeline(text)

        current_entity = ""
        entity_start = 0
        entity_end = 0
        entity_score = 0
        entity_type = ""

        assert ner_results is not None

        # Loop over NER results
        for entity in ner_results:
            if entity is None: continue
            assert isinstance(entity, dict), f"Expected dict, got {type(entity)}"
            if entity["entity"].startswith("B-"):  # Beginning of a new entity
                if current_entity:  # Store the previous entity
                    results.append(RecognizerResult(
                        entity_type=entity_type,
                        start=entity_start,
                        end=entity_end,
                        score=entity_score / (entity_end - entity_start)
                    ))

                # Start a new entity
                current_entity = entity["word"]
                entity_type = entity["entity"].split("-")[1]  # Get entity type (ORG, etc.)
                entity_start = entity["start"]
                entity_end = entity["end"]
                entity_score = entity["score"]

            elif entity["entity"].startswith("I-") and current_entity:
                # Continue the entity
                current_entity += entity["word"].replace("##", "")  # Handle wordpiece tokens
                entity_end = entity["end"]
                entity_score += entity["score"]  # Accumulate scores for tokens

        # Append the last entity (if any)
        if current_entity:
            results.append(RecognizerResult(
                entity_type=entity_type,
                start=entity_start,
                end=entity_end,
                score=entity_score / (entity_end - entity_start)
            ))

        return results