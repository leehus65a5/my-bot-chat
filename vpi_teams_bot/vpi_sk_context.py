from semantic_kernel import Kernel, SKContext
from semantic_kernel.orchestration.context_variables import ContextVariables

class VpiSkContext(SKContext):
    
    def __init__(self, kernel: Kernel, context_type : str):
        super().__init__(
            ContextVariables(),
            kernel._memory,
            kernel.skills,
            kernel._log
        )
        self._type = context_type 
        self._lhistory = []
        self._isfull = False 
        self.__setitem__(context_type, "")
    
    def _isFull(self) -> bool:
        self._isfull = True if len(self._lhistory) >= 10 else False
        return self._isfull
	
    def get(self) -> str:
        return " ".join(self._lhistory)
    
    def put(self, content: str) -> None:
        self._lhistory.append(content)
        if self._isFull():
            self._lhistory.pop(0)

        self.__setitem__(self._type, self.get())
