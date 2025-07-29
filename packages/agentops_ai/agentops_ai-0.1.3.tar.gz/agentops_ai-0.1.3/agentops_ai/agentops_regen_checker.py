import hashlib
import json
import os
from typing import Optional
import argparse

METADATA_FILE = ".agentops/test_hashes.json"

def compute_hash(file_path: str) -> str:
    """Compute SHA-256 hash of a file."""
    with open(file_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def load_hashes() -> dict:
    """Load saved file hashes."""
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_hashes(data: dict):
    """Save current file hashes."""
    os.makedirs(os.path.dirname(METADATA_FILE), exist_ok=True)
    with open(METADATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def needs_regeneration(source_path: str, test_path: Optional[str] = None, force: bool = False) -> bool:
    """Decide whether test should be regenerated based on hash."""
    source_path = os.path.abspath(source_path)
    if force or not os.path.exists(test_path or ""):
        return True
    current_hash = compute_hash(source_path)
    all_hashes = load_hashes()
    saved_hash = all_hashes.get(source_path)
    return current_hash != saved_hash

def update_hash(source_path: str):
    """Update the stored hash after regeneration."""
    source_path = os.path.abspath(source_path)
    all_hashes = load_hashes()
    all_hashes[source_path] = compute_hash(source_path)
    save_hashes(all_hashes)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check if test regeneration is needed based on source file changes.")
    parser.add_argument("source", help="Path to the source file")
    parser.add_argument("--test", help="Path to the test file", default=None)
    parser.add_argument("--force-generate", action="store_true", help="Force regeneration regardless of hash")
    parser.add_argument("--update", action="store_true", help="Update hash after regeneration")
    args = parser.parse_args()

    if args.update:
        update_hash(args.source)
        print(f"Hash updated for {args.source}")
    else:
        regen = needs_regeneration(args.source, args.test, args.force_generate)
        print("REGENERATE" if regen else "UP-TO-DATE") 