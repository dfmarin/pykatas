from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import yaml

VALID_DIFFICULTIES = {"easy", "medium", "hard"}


@dataclass
class KataDefinition:
    id: str
    title: str
    difficulty: str
    tags: list[str]
    function_name: str
    timeout_seconds: int
    memory_limit_mb: int
    kata_dir: Path
    public_tests: bool = True
    lint_rules: list[str] = field(default_factory=list)

    @property
    def description(self) -> str:
        for line in self.readme.splitlines():
            line = line.strip().lstrip("#").strip()
            # first non-empty line of the README
            if line:
                return line
        return ""

    @property
    def public_test_source(self) -> str:
        path = self.kata_dir / "tests" / "test_public.py"
        if path.exists():
            return path.read_text()
        return "# No public tests available."

    @property
    def starter_code(self) -> str:
        return (self.kata_dir / "starter_code.py").read_text()

    @property
    def readme(self) -> str:
        return (self.kata_dir / "README.md").read_text()

    @property
    def has_hidden_tests(self) -> bool:
        return (self.kata_dir / "tests" / "test_hidden.py").exists()


class KataLoaderError(Exception):
    pass


class KataLoader:
    def __init__(self, kata_dir: str | Path) -> None:
        self._kata_dir = Path(kata_dir)
        self._cache: dict[str, KataDefinition] = {}

    def load_all(self) -> list[KataDefinition]:
        katas = []
        for path in sorted(self._kata_dir.iterdir()):
            if path.is_dir() and (path / "kata.yaml").exists():
                katas.append(self._load_one(path))
        return katas

    def get(self, kata_id: str) -> Optional[KataDefinition]:
        if kata_id not in self._cache:
            path = self._kata_dir / kata_id
            if not path.exists():
                return None
            self._cache[kata_id] = self._load_one(path)
        return self._cache[kata_id]

    def _load_one(self, path: Path) -> KataDefinition:
        raw = yaml.safe_load((path / "kata.yaml").read_text())
        self._validate(raw, path)
        return KataDefinition(kata_dir=path, **raw)

    def _validate(self, raw: dict, path: Path) -> None:
        required = {"id", "title", "difficulty", "function_name"}
        missing = required - raw.keys()
        if missing:
            raise KataLoaderError(f"{path}: missing fields {missing}")
        if raw["difficulty"] not in VALID_DIFFICULTIES:
            raise KataLoaderError(f"{path}: invalid difficulty '{raw['difficulty']}'")
