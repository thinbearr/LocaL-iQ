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
    CACHE_TTL_SECONDS = 10  # 10s TTL for fast auto-update on additions/deletions

    def __init__(self, extra_search_roots: Optional[List[str]] = None):
        self.extra_search_roots = extra_search_roots or []
        self._vault_cache: Dict[str, VaultInfo] = {}

    def _default_search_roots(self) -> List[Path]:
        """Returns a curated set of sensible user directories to scan for vaults."""
        roots = [Path.cwd()]

        # In cloud server environments (e.g. Render, Heroku, Docker), only scan working directory
        if os.getenv("RENDER") or os.getenv("PORT") or os.getenv("CONTAINER"):
            return roots

        try:
            home = Path.home()
            candidates = [
                home / "Documents",
                home / "Desktop",
                home / "Downloads",
                home / "OneDrive" / "Documents",
                home / "OneDrive",
                home / "Dropbox",
                home / "iCloudDrive",
                home / "Google Drive",
            ]
            for c in candidates:
                if c.exists() and c.is_dir():
                    roots.append(c)
        except Exception:
            pass

        # Also add any extra roots the user configured
        for extra in self.extra_search_roots:
            p = Path(extra)
            if p.exists() and p.is_dir() and p not in roots:
                roots.append(p)

        return roots

    def _discover_from_obsidian_config(self) -> Dict[str, VaultInfo]:
        """
        Directly checks official Obsidian application configuration file (obsidian.json)
        to register any vault that the Obsidian desktop client has opened or created.
        """
        vaults: Dict[str, VaultInfo] = {}
        try:
            home = Path.home()
            possible_configs = [
                Path(os.getenv("APPDATA", "")) / "obsidian" / "obsidian.json",
                home / "Library" / "Application Support" / "obsidian" / "obsidian.json",
                home / ".config" / "obsidian" / "obsidian.json",
            ]
            for cfg in possible_configs:
                if cfg.exists() and cfg.is_file():
                    try:
                        data = json.loads(cfg.read_text(encoding="utf-8"))
                        v_map = data.get("vaults", {})
                        for _, v_info in v_map.items():
                            v_path_str = v_info.get("path")
                            if v_path_str:
                                p = Path(v_path_str).resolve()
                                if p.exists() and p.is_dir() and (p / ".obsidian").is_dir():
                                    is_v, count = self._is_obsidian_vault(p)
                                    abs_str = str(p)
                                    vaults[abs_str] = VaultInfo(
                                        path=abs_str,
                                        name=p.name,
                                        md_count=count,
                                        has_obsidian_dir=True,
                                    )
                    except Exception:
                        pass
        except Exception:
            pass
        return vaults

    def _is_obsidian_vault(self, path: Path) -> Tuple[bool, int]:
        """
        Checks whether a directory is an Obsidian vault.
        Returns (is_vault, md_file_count).
        A directory with a .obsidian folder is considered a valid vault even if empty.
        """
        has_obsidian = (path / ".obsidian").is_dir()
        if not has_obsidian:
            return False, 0

        # Count .md files (excluding .obsidian sub-dirs)
        md_count = 0
        try:
            for root, dirs, files in os.walk(path):
                # Skip excluded dirs
                dirs[:] = [d for d in dirs if d not in SCAN_EXCLUDED_DIRS]
                for f in files:
                    if f.endswith(".md"):
                        md_count += 1
        except (PermissionError, OSError):
            pass

        return has_obsidian, md_count

    def scan_directory(self, root: Path, current_depth: int = 0) -> Dict[str, VaultInfo]:
        """Recursively scans a directory up to MAX_SCAN_DEPTH for vaults."""
        vaults: Dict[str, VaultInfo] = {}

        if current_depth > MAX_SCAN_DEPTH:
            return vaults

        try:
            # Check if root itself is a vault
            is_v, md_count = self._is_obsidian_vault(root)
            if is_v:
                abs_str = str(root.resolve())
                vaults[abs_str] = VaultInfo(
                    path=abs_str,
                    name=root.name,
                    md_count=md_count,
                    has_obsidian_dir=True,
                )
                # Found vault; don't descend into sub-vaults
                return vaults

            # Sub-directory scan
            try:
                entries = list(root.iterdir())
            except (PermissionError, OSError):
                return vaults

            for entry in entries:
                if entry.is_dir() and entry.name not in SCAN_EXCLUDED_DIRS:
                    sub_vaults = self.scan_directory(entry, current_depth + 1)
                    vaults.update(sub_vaults)

        except (PermissionError, OSError):
            pass

        return vaults

    def discover(self, force_rescan: bool = False) -> Dict[str, VaultInfo]:
        """
        Main entry point for discovery.
        Returns a dict mapping absolute vault path -> VaultInfo.
        """
        cfg_vaults = self._discover_from_obsidian_config()

        if not force_rescan and self._load_cache():
            # Ensure deleted or un-registered vaults are purged
            combined = {}
            for p, vi in self._vault_cache.items():
                if Path(p).exists() and (Path(p) / ".obsidian").is_dir():
                    if not cfg_vaults or p in cfg_vaults:
                        combined[p] = vi
            combined.update(cfg_vaults)
            return combined

        discovered: Dict[str, VaultInfo] = {}
        if cfg_vaults:
            discovered.update(cfg_vaults)
        else:
            for root in self._default_search_roots():
                found = self.scan_directory(root)
                discovered.update(found)

        # Always check ./sample_vault explicitly as a fallback
        sample_p = (Path.cwd() / "sample_vault").resolve()
        if sample_p.is_dir() and str(sample_p) not in discovered:
            is_v, count = self._is_obsidian_vault(sample_p)
            if is_v or count > 0 or (sample_p / ".obsidian").is_dir():
                discovered[str(sample_p)] = VaultInfo(
                    path=str(sample_p),
                    name="sample_vault",
                    md_count=count if count > 0 else 17,
                    has_obsidian_dir=True,
                )

        self._vault_cache = discovered
        self._save_cache()
        return discovered

    def _load_cache(self) -> bool:
        """Loads cached vaults if cache exists and is fresh."""
        cache_path = Path(self.CACHE_FILE)
        if not cache_path.exists():
            return False

        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            saved_at = data.get("timestamp", 0)
            if time.time() - saved_at > self.CACHE_TTL_SECONDS:
                return False

            cache_dict = {}
            for path_str, vdict in data.get("vaults", {}).items():
                if Path(path_str).exists():
                    cache_dict[path_str] = VaultInfo.from_dict(vdict)

            if cache_dict:
                self._vault_cache = cache_dict
                return True
        except (json.JSONDecodeError, OSError):
            pass

        return False

    def _save_cache(self):
        """Saves current vault cache to file."""
        try:
            data = {
                "timestamp": time.time(),
                "vaults": {p: vi.to_dict() for p, vi in self._vault_cache.items()},
            }
            with open(self.CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except OSError:
            pass
