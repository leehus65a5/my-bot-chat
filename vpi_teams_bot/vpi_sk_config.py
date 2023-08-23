from config import DefaultConfig

import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import (AzureTextEmbedding,
                                                   OpenAITextCompletion)
from semantic_kernel.connectors.memory.azure_cognitive_search import AzureCognitiveSearchMemoryStore
from .vpi_sk_context import VpiSkContext

class VpiSkKernel:

    def __init__(self):
        self._skill_foler = './vpi_bot_skills'
        self._vpi_kernel = sk.Kernel()
        CONFIG = DefaultConfig()
        self._vpi_kernel.add_text_embedding_generation_service('ada', AzureTextEmbedding('ada-embedding', 
                                                                CONFIG.AZURE_OPENAI_ENDPOINT, 
                                                                CONFIG.AZURE_OPENAI_API_KEY))

        self._vpi_kernel.add_text_completion_service("dv", OpenAITextCompletion("text-davinci-003",
                                                              CONFIG.OPENAI_API_KEY,  # type: ignore
                                                              CONFIG.OPENAI_ORG_ID))

        self._vpi_kernel.register_memory_store(AzureCognitiveSearchMemoryStore(1536,
                                                            CONFIG.AZURE_SEARCH_ENDPOINT,
                                                            CONFIG.AZURE_SEARCH_API_KEY))
        
    def get_kernel(self):
        return self._vpi_kernel

    def get_semantic_skill(self, skill_name: str):
        return self._vpi_kernel.import_semantic_skill_from_directory(self._skill_foler, skill_name)
    
    def get_context(self, context_type: str):
        return VpiSkContext(self._vpi_kernel, context_type = context_type)
        
        
        
# CONFIG = DefaultConfig()
# kernel = sk.Kernel()
# kernel.add_text_embedding_generation_service('ada', 
#                                              AzureTextEmbedding('ada-embedding', 
#                                                                 CONFIG.AZURE_OPENAI_ENDPOINT, 
#                                                                 CONFIG.AZURE_OPENAI_API_KEY))

# kernel.add_text_completion_service("dv", OpenAITextCompletion("text-davinci-003",
#                                                               CONFIG.OPENAI_API_KEY, 
#                                                               CONFIG.OPENAI_ORG_ID))

# kernel.register_memory_store(AzureCognitiveSearchMemoryStore(1536,
#                                                             CONFIG.AZURE_SEARCH_ENDPOINT,
#                                                             CONFIG.AZURE_SEARCH_API_KEY))


# chatskill =  kernel.import_semantic_skill_from_directory("./vpi_bot_skills", 'chat_skills')
# sk_context = kernel.create_new_context()
# sk_context['history'] = ""
# sk_context = VpiSkHistory(kernel)
# sk_context.put_history("")

# def get_semantic_kernel():
#     return kernel
