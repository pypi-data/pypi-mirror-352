from swiftscrub.llm import LLM
from swiftscrub.anonymization.prompts import (
    merge_system_prompt,
    identification_prompt,
    document_wrapper,
    anonymization_system_prompt,
    anonymization_user_prompt
)


class IdentifySensitiveInfoAgent:
    def __init__(self, llm: LLM):
        """
        Initialize the Anonymizer with an LLM instance.
        
        Args:
            llm: An instance of a language model (LLM) to use for anonymization.
        """
        self.llm = llm
    
    def identify(self, document: str) -> str:
        identified_sensitive_info = self.llm([
            {"role": "system", "content": merge_system_prompt},
            {"role": "user", "content": identification_prompt},
            {"role": "user", "content": document_wrapper.format(document=document)}
        ])
        # remnant of the ollama system
        # {"seed": 101, "temperature": 0.02, "num_ctx": CTX_WINDOW_SIZE}
        return identified_sensitive_info

    def __call__(self, document: str) -> str:
        """
        Call the agent to identify sensitive information in the document.
        
        Args:
            document: The text document to analyze for sensitive information.
        
        Returns:
            A string containing the identified sensitive information.
        """
        return self.identify(document=document)


class AnonymizeAgent:
    def __init__(self, llm: LLM):
        """
        Initialize the Anonymizer with an LLM instance.
        
        Args:
            llm: An instance of a language model (LLM) to use for anonymization.
        """
        self.llm = llm
    
    def anonymize(self, document: str, identified_sensitive_info: str) -> str:
        anonymized_response = self.llm([
            {"role": "system", "content": anonymization_system_prompt.format(
                identified_sensitive_info=identified_sensitive_info
            )},
            {"role": "user", "content": anonymization_user_prompt},
            {"role": "user", "content": document_wrapper.format(document=document)}
        ])
        # remnant of the ollama system
        # {"seed": 101, "temperature": 0.02, "num_ctx": CTX_WINDOW_SIZE}
        return anonymized_response
    
    def __call__(self, document: str, identified_sensitive_info: str) -> str:
        """
        Call the agent to anonymize the document based on identified sensitive information.
        
        Args:
            document: The text document to anonymize.
            identified_sensitive_info: The sensitive information identified in the document.
        
        Returns:
            A string containing the anonymized version of the document.
        """
        return self.anonymize(document=document, identified_sensitive_info=identified_sensitive_info)