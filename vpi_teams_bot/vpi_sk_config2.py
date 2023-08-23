from config import DefaultConfig

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import (AzureTextEmbedding,
                                                   OpenAITextCompletion, OpenAITextEmbedding)
from semantic_kernel.connectors.memory.azure_cognitive_search import AzureCognitiveSearchMemoryStore
from .vpi_sk_context import VpiSkContext
from qdrant_client import QdrantClient
from semantic_kernel.connectors.memory.qdrant import QdrantMemoryStore

class VpiSkKernel2(Kernel):

    def __init__(self):
        super().__init__()
        self._skill_foler = './vpi_bot_skills'
        CONFIG = DefaultConfig()
        self.add_text_embedding_generation_service('ada',OpenAITextEmbedding('text-embedding-ada-002', 
                                                                             api_key= CONFIG.OPENAI_API_KEY))

        self.add_text_completion_service("dv", OpenAITextCompletion("text-davinci-003",
                                                              CONFIG.OPENAI_API_KEY,  # type: ignore
                                                              CONFIG.OPENAI_ORG_ID))

        # self.register_memory_store(AzureCognitiveSearchMemoryStore(1536,
        #                                                     CONFIG.AZURE_SEARCH_ENDPOINT,
        #                                                     CONFIG.AZURE_SEARCH_API_KEY))

        qdrant_client = QdrantClient(
            url=CONFIG.QDRANT_ENDPOINT, 
            api_key=CONFIG.QDRANT_API_KEY,
            timeout=20,
        )
        
        qdrantMemory = QdrantMemoryStore(1536)
        qdrantMemory._qdrantclient = qdrant_client
        self.register_memory_store(qdrantMemory)
        

    def get_semantic_skill(self, skill_name: str):
        return self.import_semantic_skill_from_directory(self._skill_foler, skill_name)
    
    # def get_native_skill(self, skill_name: str):
    #     return self.import_native_skill_from_directory(self._skill_foler, skill_name)
    
    def get_context(self, context_type: str):
        return VpiSkContext(self, context_type = context_type)