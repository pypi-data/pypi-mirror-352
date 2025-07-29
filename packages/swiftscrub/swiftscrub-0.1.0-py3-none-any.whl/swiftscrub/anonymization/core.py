from typing import Optional

from swiftscrub.llm import LLM
from swiftscrub.anonymization.cvs import CVS, SegmenterParams
from swiftscrub.anonymization.anonymize import AnonymizeAgent, IdentifySensitiveInfoAgent


class Anonymizer:
    def __init__(self,
                 llm: LLM,
                 use_segmenter: bool = True,
                 model_name = "all-mpnet-base-v2"):
        self.use_segmenter = use_segmenter
        if self.use_segmenter:
            self.model_name = model_name
            self.cvs = CVS(model_name=model_name)
        
        self.llm = llm
        self.identifier = IdentifySensitiveInfoAgent(llm)
        self.anonymizer = AnonymizeAgent(llm)
    
    def predict(self, document: str,
                use_segmenter: Optional[bool] = None,
                segmenter_params: Optional[SegmenterParams] = None) -> str:
        if not document.strip():
            raise ValueError("Text input is required")
        
        if use_segmenter is None:
            use_segmenter = self.use_segmenter
        
        if use_segmenter:
            assert segmenter_params is not None, "Segmenter parameters must be provided when use_segmenter is True"
            
            sentences = self.cvs.get_sentences(document)
            segments = self.cvs.segment_text(
                sentences=sentences,
                method=segmenter_params.method,
                strategy=segmenter_params.strategy,
                num_segments=segmenter_params.num_segments
            )
            
            # Merge all segments into a single document
            document = "\n\n".join(segments)
        
        # Anonymize the merged document and return the complete result
        # Identify sensitive information
        identified_sensitive_info = self.identifier(document=document)
        
        # Second LLM call for anonymization
        anonymized_response = self.anonymizer(
            document=document,
            identified_sensitive_info=identified_sensitive_info
        )
        
        # Return the complete response with identified sensitive info
        full_response = identified_sensitive_info + "\n\n\n\n\n\n" + anonymized_response
        
        return full_response

