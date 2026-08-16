#!/usr/bin/env python3
"""Memory compact encoder.

encode: reads memory/*.md -> writes memory/*.bin (zlib-compressed bytes,
the same 0s-and-1s the machine stores, just much smaller).
decode: memory/*.bin -> original markdown text (roundtrip-safe).

Also optional 'bits' view: dumps the compressed bytes as a literal '0101..'
string for curiosity — note that string is ~8x BIGGER, not smaller.
"""
import subprocess, sys, zlib, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "memory" / "conversation-memory.md"
BIN = ROOT / "memory" / "conversation-memory.bin"
SYNC = ROOT / "scripts" / "monkeycode_sync.py"

def encode() -> None:
    data = SRC.read_bytes()
    comp = zlib.compress(data, level=9)
    BIN.write_bytes(comp)
    print(f"encode: {SRC.stat().st_size} B -> {len(comp)} B"
          f"  ({SRC.stat().st_size/max(len(comp),1):.1f}x smaller)")
    _sync_monkeycode()

def _sync_monkeycode() -> None:
    if not SYNC.exists():
        return
    try:
        subprocess.run([sys.executable, str(SYNC), "--quiet"], check=True,
                       capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"[sync] monkeycode_sync failed (non-fatal): {e.stderr.strip()}")

def decode() -> None:
    """Print the FULL decompressed memory to stdout so a session can load it."""
    comp = BIN.read_bytes()
    data = zlib.decompress(comp)
    sys.stdout.write(data.decode("utf-8", "replace"))
    sys.stdout.write("\n")
    if data == SRC.read_bytes():
        sys.stderr.write("[decoded] integrity MATCH\n")

def bits() -> None:
    comp = BIN.read_bytes()
    s = "".join(f"{b:08b}" for b in comp)
    print(f"compressed bits: {len(s)} chars ({len(comp)} bytes)")
    print("atom2:", s)

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "encode"
    {"encode": encode, "decode": decode, "bits": bits}[mode]()