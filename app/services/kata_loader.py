from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import html
import yaml

try:
    import markdown
except ImportError:
    markdown = None

VALID_DIFFICULTIES = {"easy", "medium", "hard"}


@dataclass
class KataDefinition:
    id: str
    title: str
    description: str
    difficulty: str
    tags: list[str]
    entry_name: str
    timeout_seconds: int
    memory_limit_mb: int
    kata_dir: Path
    public_tests: bool = True
    lint_rules: list[str] = field(default_factory=list)

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
    def readme_html(self) -> str:
        if markdown is not None:
            return markdown.markdown(
                self.readme,
                extensions=["fenced_code", "tables", "sane_lists"],
            )
        escaped = html.escape(self.readme)
        return f'<pre style="white-space: pre-wrap;">{escaped}</pre>'

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
            if path.is_dir():
                metadata_path = self._find_metadata_file(path)
                if metadata_path is not None:
                    katas.append(self._load_one(path, metadata_path))
        return katas

    def get(self, kata_id: str) -> Optional[KataDefinition]:
        if kata_id not in self._cache:
            path = self._kata_dir / kata_id
            if not path.exists() or not path.is_dir():
                return None
            metadata_path = self._find_metadata_file(path)
            if metadata_path is None:
                return None
            self._cache[kata_id] = self._load_one(path, metadata_path)
        return self._cache[kata_id]

    def _find_metadata_file(self, path: Path) -> Optional[Path]:
        for filename in ("kata.yaml", "kata.yml"):
            metadata_path = path / filename
            if metadata_path.exists():
                return metadata_path
        return None

    def _load_one(self, path: Path, metadata_path: Path) -> KataDefinition:
        raw = yaml.safe_load(metadata_path.read_text())
        self._validate(raw, path)
        raw["entry_name"] = raw.get("function_name") or raw.get("class_name")
        filtered = {k: v for k, v in raw.items() if k in KataDefinition.__annotations__}
        return KataDefinition(kata_dir=path, **filtered)

    def _validate(self, raw: dict, path: Path) -> None:
        required = {"id", "title", "difficulty"}
        missing = required - raw.keys()
        if missing:
            raise KataLoaderError(f"{path}: missing fields {missing}")
        if not (raw.get("function_name") or raw.get("class_name")):
            raise KataLoaderError(
                f"{path}: missing required entry point field, expected function_name or class_name"
            )
        if raw["difficulty"] not in VALID_DIFFICULTIES:
            raise KataLoaderError(f"{path}: invalid difficulty '{raw['difficulty']}'")
