from typing import Dict, Iterator, List, NamedTuple, Optional, Sequence, Tuple, Union

class ShellResult(NamedTuple):
    returncode: int
    stdout: str
    stderr: str

def decodes(text: Union[str, bytes]) -> str:
    pass

class ShellException(Exception):

    def __init__(self, msg: str, result: ShellResult) -> None:
        pass

def sh(cmd: str=':', shell: bool=True, check: bool=True, ok: Optional[bool]=None, default: str='') -> ShellResult:
    pass

def portprot(arg: str) -> Tuple[str, str]:
    pass

def need_to_remove_old_manifest() -> bool:
    pass

def need_to_clean_whitespaces() -> bool:
    pass

def need_to_chmod_file_stat() -> bool:
    pass

def clean_whitespaces(text: str) -> str:
    pass

def chmod_file_stat(filename: str) -> None:
    pass

class ImageName:
    registry: Optional[str]
    image: str
    version: Optional[str]

    def __init__(self, image: str) -> None:
        pass

    def parse(self, image: str) -> None:
        pass

    def __str__(self) -> str:
        pass

    def tag(self) -> str:
        pass

    def local(self) -> bool:
        pass

    def valid(self) -> bool:
        pass

    def problems(self) -> Iterator[str]:
        pass

def edit_image(inp: Optional[str], out: Optional[str], edits: Commands) -> int:
    pass

def edit_datadir(datadir: str, out: Optional[str], edits: Commands) -> int:
    pass

def parse_commands(args: Sequence[str]) -> Tuple[Optional[str], Optional[str], Commands]:
    pass

def docker_tag(inp: Optional[str], out: Optional[str]) -> None:
    pass

def run(*args: str) -> int:
    pass

def main() -> int:
    pass
