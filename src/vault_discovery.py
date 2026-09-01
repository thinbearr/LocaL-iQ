"""
Obsidian Vault Discovery Module

Scans sensible user-accessible directories for Obsidian vaults (identified by .obsidian/ dir + .md files).
Does NOT scan entire drives. Uses a curated, configurable set of search roots.
Caches discovered vault paths between invocations.
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict


# Directories that should never be entered during discovery scans
SCAN_EXCLUDED_DIRS = {
    ".git", ".obsidian", "__pycache__", "node_modules", "venv", ".venv",
    "site-packages", "AppData", "ProgramData", "Windows", "System32",
    "$Recycle.Bin", "Program Files", "Program Files (x86)"
}

# Maximum depth to descend when searching for vaults
MAX_SCAN_DEPTH = 5


@dataclass
class VaultInfo:
    """Metadata about a discovered Obsidian vault."""
    path: str               # Absolute path to vault root
    name: str               # Display name (folder name)
    md_count: int           # Number of .md files found
    has_obsidian_dir: bool  # Whether .obsidian/ is present
    last_discovered: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "VaultInfo":
        return VaultInfo(**d)


class ObsidianVaultDiscovery:
    """
    Discovers Obsidian vaults by scanning user-accessible directories.
    Uses sensible defaults; allows configuring additional search roots.
    Caches results to avoid expensive re-scans on every startup.
    """

    CACHE_FILE = ".vault_discovery_cache.json"
    CACHE_TTL_SECONDS = 300  # Re-use cache for 5 minutes between restarts

    def __init__(self, extra_search_roots: Optional[List[str]] = None):
        self.extra_search_roots = extra_search_roots or []
        self._vault_cache: Dict[str, VaultInfo] = {}

    def _default_search_roots(self) -> List[Path]:
        """Returns a curated set of sensible user directories to scan for vaults."""
        roots = []
        home = Path.home()

        candidates = [
            home / "Documents",
            home / "Desktop",
            home / "OneDrive" / "Documents",
            home / "OneDrive",
            home / "Dropbox",
            home / "iCloudDrive",
            home / "Google Drive",
            Path("C:/Users") / os.getlogin() / "Documents",
        ]

        # Also add any extra roots the user configured
        for extra in self.extra_search_roots:
            candidates.append(Path(extra))

        # Also always include the cwd (project directory) for sample_vault etc.
        candidates.append(Path.cwd())

        for c in candidates:
            try:
                if c.exists() and c.is_dir():
                    roots.append(c)
            except (PermissionError, OSError):
                continue

        return roots

    def _is_obsidian_vault(self, path: Path) -> Tuple[bool, int]:
        """
        Checks whether a directory is an Obsidian vault.
        Returns (is_vault, md_file_count).
        """
        has_obsidian = (path / ".obsidian").is_dir()
        if not has_obsidian:
            return False, 0

        # Count .md files (excluding .obsidian sub-dirs)
        md_count = 0
        try:
            for root, dirs, files in os.walk(path):
                dirs[:] = [d for d in dirs if d not in SCAN_EXCLUDED_DIRS and not d.startswith(".")]
                for f in files:
                    if f.endswith(".md"):
                        md_count += 1
        except (PermissionError, OSError):
            pass

        return md_count > 0, md_count

    def _scan_for_vaults(self, root: Path, depth: int = 0) -> List[VaultInfo]:
        """
        Recursively scans for vaults up to MAX_SCAN_DEPTH.
        Stops descending into a directory once a vault is found there.
        """
        found = []
        if depth > MAX_SCAN_DEPTH:
            return found

        try:
            is_vault, md_count = self._is_obsidian_vault(root)
            if is_vault:
                found.append(VaultInfo(
                    path=str(root),
                    name=root.name,
                    md_count=md_count,
                    has_obsidian_dir=True,
                    last_discovered=time.time()
                ))
                return found  # Don't recurse further into a vault

            # Recurse into subdirectories
            for child in sorted(root.iterdir()):
                if (
                    child.is_dir()
                    and child.name not in SCAN_EXCLUDED_DIRS
                    and not child.name.startswith(".")
                ):
                    try:
                        found.extend(self._scan_for_vaults(child, depth + 1))
                    except (PermissionError, OSError):
                        continue

        except (PermissionError, OSError):
            pass

        return found

    def _load_cache(self) -> Dict[str, VaultInfo]:
        """Loads previously discovered vaults from disk cache if still fresh."""
        cache_path = Path(self.CACHE_FILE)
        if not cache_path.exists():
            return {}
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Check TTL
            if time.time() - data.get("timestamp", 0) > self.CACHE_TTL_SECONDS:
                return {}
            vaults = {}
            for v in data.get("vaults", []):
                vi = VaultInfo.from_dict(v)
                vaults[vi.path] = vi
            return vaults
        except Exception:
            return {}

    def _save_cache(self, vaults: Dict[str, VaultInfo]):
        """Saves discovered vaults to disk cache."""
        try:
            cache_path = Path(self.CACHE_FILE)
            data = {
                "timestamp": time.time(),
                "vaults": [v.to_dict() for v in vaults.values()]
            }
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def discover(self, force_rescan: bool = False) -> Dict[str, VaultInfo]:
        """
        Returns all discovered Obsidian vaults.
        Uses cache unless force_rescan=True.
        """
        if not force_rescan:
            cached = self._load_cache()
            if cached:
                # Validate cached paths still exist
                valid = {p: v for p, v in cached.items() if Path(p).exists()}
                if valid:
                    self._vault_cache = valid
                    return valid

        all_vaults: Dict[str, VaultInfo] = {}
        for root in self._default_search_roots():
            for vi in self._scan_for_vaults(root):
                if vi.path not in all_vaults:
                    all_vaults[vi.path] = vi

        self._vault_cache = all_vaults
        self._save_cache(all_vaults)
        return all_vaults

    def add_search_root(self, path: str) -> Dict[str, VaultInfo]:
        """Adds a new search root and re-scans from it."""
        root = Path(path)
        if not root.exists():
            return self._vault_cache
        new_vaults = self._scan_for_vaults(root)
        for vi in new_vaults:
            self._vault_cache[vi.path] = vi
        self._save_cache(self._vault_cache)
        return self._vault_cache
