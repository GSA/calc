from io import TextIO
from typing import List, Dict


class spawn:
    logfile = ...  # type: TextIO

    # TODO: These are not all the constructor args, just the ones we use.
    def __init__(self, command: str, args: List[str]=[], timeout: int=30,
                 env: Dict[str, str]=None) -> None:
        ...

    def readline(self, size: int=-1) -> str:
        ...

    def sendline(self, s: str='') -> int:
        ...

    def expect(self, pattern: str, timeout: int=-1, searchwindowsize: int=-1,
               async: bool=False) -> int:
        ...

    def close(self, force: bool=True) -> None:
        ...

spawnu = spawn
