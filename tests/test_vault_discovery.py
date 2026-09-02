"""
test_vault_discovery.py

Verifies that ObsidianVaultDiscovery discovers a vault created after initial
startup once the cache TTL expires, simulating /api/vaults auto-refresh.
"""

from pathlib import Path
import pytest
from src.vault_discovery import ObsidianVaultDiscovery


@pytest.fixture()
def tmp_vault_root(tmp_path):
    return tmp_path


def _make_vault(parent, name, md_files=1):
    vault = parent / name
    vault.mkdir(parents=True, exist_ok=True)
    (vault / ".obsidian").mkdir()
    for i in range(md_files):
        (vault / f"note_{i}.md").write_text(f"# Note {i}\n\nContent.", encoding="utf-8")
    return vault


def test_new_vault_discovered_after_cache_expires(tmp_vault_root, tmp_path):
    """A vault created after initial discovery must appear once the cache TTL expires."""
    original_cache = ObsidianVaultDiscovery.CACHE_FILE
    original_ttl = ObsidianVaultDiscovery.CACHE_TTL_SECONDS
    ObsidianVaultDiscovery.CACHE_FILE = str(tmp_path / ".cache.json")
    ObsidianVaultDiscovery.CACHE_TTL_SECONDS = 0  # expire immediately
    try:
        idex = _make_vault(tmp_vault_root, "IDEX", md_files=3)
        discovery = ObsidianVaultDiscovery(extra_search_roots=[str(tmp_vault_root)])
        first_scan = discovery.discover(force_rescan=True)
        assert str(idex) in first_scan, "IDEX not found in first scan"
        fun = _make_vault(tmp_vault_root, "Fun", md_files=1)
        second_scan = discovery.discover(force_rescan=False)
        found_paths = list(second_scan.keys())
        assert str(fun) in second_scan, (
            f"Fun vault should be auto-discovered after cache expires. Found: {found_paths}"
        )
        assert str(idex) in second_scan, "IDEX should still be present in second scan"
    finally:
        ObsidianVaultDiscovery.CACHE_FILE = original_cache
        ObsidianVaultDiscovery.CACHE_TTL_SECONDS = original_ttl


def test_vault_with_obsidian_dir_and_md_file_is_valid(tmp_vault_root, tmp_path):
    """A dir with .obsidian/ and .md files must be classified as an Obsidian vault."""
    vault = _make_vault(tmp_vault_root, "ValidVault", md_files=2)
    original_cache = ObsidianVaultDiscovery.CACHE_FILE
    original_ttl = ObsidianVaultDiscovery.CACHE_TTL_SECONDS
    ObsidianVaultDiscovery.CACHE_FILE = str(tmp_path / ".cache2.json")
    ObsidianVaultDiscovery.CACHE_TTL_SECONDS = 0
    try:
        discovery = ObsidianVaultDiscovery(extra_search_roots=[str(tmp_vault_root)])
        found = discovery.discover(force_rescan=True)
        assert str(vault) in found
        assert found[str(vault)].has_obsidian_dir is True
        assert found[str(vault)].md_count >= 2
    finally:
        ObsidianVaultDiscovery.CACHE_FILE = original_cache
        ObsidianVaultDiscovery.CACHE_TTL_SECONDS = original_ttl


def test_dir_without_obsidian_not_a_vault(tmp_vault_root, tmp_path):
    """A dir with .md files but no .obsidian/ must NOT be classified as a vault."""
    plain_dir = tmp_vault_root / "NotAVault"
    plain_dir.mkdir()
    (plain_dir / "note.md").write_text("# Hello", encoding="utf-8")
    original_cache = ObsidianVaultDiscovery.CACHE_FILE
    original_ttl = ObsidianVaultDiscovery.CACHE_TTL_SECONDS
    ObsidianVaultDiscovery.CACHE_FILE = str(tmp_path / ".cache3.json")
    ObsidianVaultDiscovery.CACHE_TTL_SECONDS = 0
    try:
        discovery = ObsidianVaultDiscovery(extra_search_roots=[str(tmp_vault_root)])
        found = discovery.discover(force_rescan=True)
        assert str(plain_dir) not in found, "Dir without .obsidian/ must not be a vault"
    finally:
        ObsidianVaultDiscovery.CACHE_FILE = original_cache
        ObsidianVaultDiscovery.CACHE_TTL_SECONDS = original_ttl
