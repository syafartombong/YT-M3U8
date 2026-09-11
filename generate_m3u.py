#!/usr/bin/env python3
"""
Generate an M3U8 playlist from a list of YouTube Live channels using yt-dlp.

Membaca daftar channel dari channels.txt (format: Nama|tvg-id|URL) dan
menulis playlist.m3u berisi URL HLS langsung untuk tiap channel yang
sedang live. Channel yang saat ini tidak live akan dilewati (bukan bikin
seluruh proses gagal).

Ditujukan untuk channel YouTube publik/gratis (mis. siaran berita FTA).
Jangan dipakai untuk stream berbayar/DRM-protected.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Optional

CHANNELS_FILE = Path("channels.txt")
OUTPUT_FILE = Path("playlist.m3u")
COOKIES_FILE = Path("cookies.txt")
YT_DLP_TIMEOUT_SECONDS = 30


def resolve_stream_url(youtube_url: str) -> Optional[str]:
    """Pakai yt-dlp untuk resolve URL YouTube Live ke URL HLS (.m3u8) langsung."""
    cmd = ["yt-dlp", "-g", "-f", "best"]
    if COOKIES_FILE.exists():
        cmd += ["--cookies", str(COOKIES_FILE)]
    cmd.append(youtube_url)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=YT_DLP_TIMEOUT_SECONDS,
            check=True,
        )
        lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        return lines[-1] if lines else None
    except subprocess.CalledProcessError as e:
        stderr = (e.stderr or "").strip() or "(tanpa detail)"
        print(f"  [!] Gagal resolve {youtube_url}:", file=sys.stderr)
        for line in stderr.splitlines():
            print(f"      {line}", file=sys.stderr)
        return None
    except subprocess.TimeoutExpired:
        print(f"  [!] Timeout resolve {youtube_url}", file=sys.stderr)
        return None


def load_channels() -> list[tuple[str, str, str]]:
    if not CHANNELS_FILE.exists():
        print(f"File {CHANNELS_FILE} tidak ditemukan.", file=sys.stderr)
        sys.exit(1)

    channels: list[tuple[str, str, str]] = []
    for lineno, raw_line in enumerate(
        CHANNELS_FILE.read_text(encoding="utf-8").splitlines(), start=1
    ):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) != 3:
            print(
                f"  [!] Baris {lineno} tidak valid (harus Nama|tvg-id|URL): {line}",
                file=sys.stderr,
            )
            continue
        name, tvg_id, url = parts
        channels.append((name, tvg_id, url))
    return channels


def build_m3u(entries: list[str]) -> str:
    body = "\n".join(entries)
    return f"#EXTM3U\n{body}\n" if entries else "#EXTM3U\n"


def main() -> None:
    channels = load_channels()
    entries: list[str] = []

    print(f"Memproses {len(channels)} channel...")
    for name, tvg_id, url in channels:
        print(f"- {name} ({url})")
        stream_url = resolve_stream_url(url)
        if stream_url:
            entries.append(
                f'#EXTINF:-1 tvg-id="{tvg_id}" group-title="Indonesia",{name}\n{stream_url}'
            )
            print("  [ok] berhasil")
        else:
            print("  [skip] tidak sedang live atau gagal di-resolve")

    OUTPUT_FILE.write_text(build_m3u(entries), encoding="utf-8")
    print(f"\nSelesai. {len(entries)}/{len(channels)} channel ditulis ke {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
