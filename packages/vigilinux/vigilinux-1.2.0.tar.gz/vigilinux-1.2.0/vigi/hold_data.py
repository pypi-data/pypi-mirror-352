#hold_data.py
import json
from hashlib import md5
from pathlib import Path
from typing import Any, Callable, Generator, no_type_check


class Cache:
    """
    Cache decorator with proper parameter handling for caching flag
    """

    def __init__(self, length: int, cache_path: Path) -> None:
        self.length = length
        self.cache_path = cache_path
        self.cache_path.mkdir(parents=True, exist_ok=True)

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args: Any, **kwargs: Any) -> Generator[str, None, None]:
            # Extract caching flag while keeping it in kwargs for the wrapped function
            should_cache = kwargs.get("caching", False)
            
            # Create key from args and kwargs (excluding caching for stability)
            key_data = {
                "args": args,
                "kwargs": {k: v for k, v in kwargs.items() if k != "caching"}
            }
            key = md5(json.dumps(key_data, sort_keys=True).encode("utf-8")).hexdigest()
            file = self.cache_path / key

            if should_cache and file.exists():
                yield file.read_text()
                return

            result = ""
            # Pass through original kwargs including caching
            for chunk in func(*args, **kwargs):
                result += chunk
                yield chunk

            if should_cache and "@FunctionCall" not in result:
                file.write_text(result)
                self._cleanup_cache()

        return wrapper

    @no_type_check
    def _cleanup_cache(self) -> None:
        """Maintain cache size limit"""
        files = sorted(self.cache_path.glob("*"), key=lambda f: f.stat().st_mtime)
        if len(files) > self.length:
            for f in files[:len(files) - self.length]:
                f.unlink()