#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from html import unescape
from pathlib import Path
from urllib.parse import unquote, urlsplit

IMAGE_EXTS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".bmp",
    ".svg",
    ".avif",
    ".tif",
    ".tiff",
    ".ico",
}

SKIP_DIRS = {".git", "node_modules", "vendor", ".idea", ".vscode"}

MD_IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
HTML_SRC_RE = re.compile(r"<(?:img|source)\b[^>]*?\bsrc\s*=\s*[\"']([^\"']+)[\"']", re.IGNORECASE)
CSS_URL_RE = re.compile(r"url\(([^)]+)\)", re.IGNORECASE)
RAW_IMAGE_PATH_RE = re.compile(r"[\"']([^\"'\s]+\.(?:png|jpe?g|gif|webp|bmp|svg|avif|tiff?|ico))(?:[?#][^\"']*)?[\"']", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Remove unreferenced local image files")
    parser.add_argument("--scan-directory", default=".", help="Directory to scan, relative to repository root")
    parser.add_argument("--ignore-paths", default="", help="Comma-separated paths to ignore, relative to repository root")
    return parser.parse_args()


def norm(path: Path) -> Path:
    return path.resolve()


def is_ignored(path: Path, ignored_roots: list[Path]) -> bool:
    rp = norm(path)
    for root in ignored_roots:
        try:
            rp.relative_to(root)
            return True
        except ValueError:
            continue
    return False


def iter_files(root: Path):
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        yield p


def sanitize_ref(raw: str) -> str:
    value = unescape(raw).strip().strip('"\'')
    if not value:
        return ""
    if " " in value:
        value = value.split(" ", 1)[0]
    lower = value.lower()
    if lower.startswith(("http://", "https://", "//", "data:", "mailto:", "tel:", "#")):
        return ""
    split = urlsplit(value)
    cleaned = unquote(split.path).strip()
    return cleaned


def to_absolute(ref_path: str, source_file: Path, repo_root: Path) -> Path:
    ref = Path(ref_path)
    if ref.is_absolute() or ref_path.startswith("/"):
        return norm(repo_root / ref_path.lstrip("/"))
    return norm(source_file.parent / ref)


def collect_references(file_path: Path, content: str, repo_root: Path) -> set[Path]:
    used: set[Path] = set()
    refs = []
    refs.extend(MD_IMAGE_RE.findall(content))
    refs.extend(HTML_SRC_RE.findall(content))
    refs.extend(CSS_URL_RE.findall(content))
    refs.extend(RAW_IMAGE_PATH_RE.findall(content))

    for raw in refs:
        cleaned = sanitize_ref(raw)
        if not cleaned:
            continue
        if Path(cleaned).suffix.lower() not in IMAGE_EXTS:
            continue
        used.add(to_absolute(cleaned, file_path, repo_root))

    return used


def main() -> int:
    args = parse_args()
    repo_root = Path.cwd()
    scan_root = norm(repo_root / args.scan_directory)

    if not scan_root.exists() or not scan_root.is_dir():
        print(f"scan directory does not exist: {scan_root}")
        return 1

    ignored_roots: list[Path] = []
    for p in [x.strip() for x in args.ignore_paths.split(",") if x.strip()]:
        ignored_roots.append(norm(repo_root / p))

    image_files: list[Path] = []
    used_images: set[Path] = set()

    for file_path in iter_files(scan_root):
        if is_ignored(file_path, ignored_roots):
            continue

        if file_path.suffix.lower() in IMAGE_EXTS:
            image_files.append(norm(file_path))
            continue

        try:
            content = file_path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue

        used_images.update(collect_references(file_path, content, repo_root))

    removed = []
    for image in image_files:
        if image in used_images:
            continue
        try:
            image.unlink()
            removed.append(image)
        except OSError as exc:
            print(f"failed to remove {image}: {exc}", file=sys.stderr)

    print(f"scanned images: {len(image_files)}")
    print(f"referenced images: {len(used_images)}")
    print(f"removed images: {len(removed)}")
    for path in removed:
        print(f"removed: {path.relative_to(repo_root)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
