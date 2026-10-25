"""Exploratory image-encryption benchmark using standard AEAD reference ciphers.

This is a research harness, not a proposed cipher and not a reproduction of any
of the six supplied papers. The nonce-reuse experiment is explicitly unsafe and
exists only to demonstrate a metric/implementation pitfall in a controlled test.
"""
from __future__ import annotations

import csv
import hashlib
import json
import secrets
import statistics
import struct
import time
from pathlib import Path
from typing import Callable

import numpy as np
from PIL import Image
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305

ROOT = Path(__file__).resolve().parents[1]
IMAGE_DIR = ROOT / "data" / "images"
RESULT_DIR = ROOT / "results"
MAGIC = b"IMGBEN1\x00"
NONCE_SIZE = 12
TAG_SIZE = 16
CIPHERS: dict[str, Callable[[bytes], object]] = {
    "AES-256-GCM": AESGCM,
    "ChaCha20-Poly1305": ChaCha20Poly1305,
}


def canonical_header(algorithm: str, width: int, height: int, mode: str) -> bytes:
    return json.dumps(
        {"version": 1, "algorithm": algorithm, "width": width,
         "height": height, "mode": mode, "dtype": "uint8"},
        sort_keys=True, separators=(",", ":"),
    ).encode("utf-8")


def encrypt(raw: bytes, header: bytes, key: bytes, algorithm: str,
            nonce: bytes | None = None) -> bytes:
    """Encrypt bytes and authenticate the canonical image header as AAD."""
    if algorithm not in CIPHERS:
        raise ValueError(f"Unsupported cipher: {algorithm}")
    if len(key) != 32:
        raise ValueError("A 256-bit key is required")
    nonce = nonce if nonce is not None else secrets.token_bytes(NONCE_SIZE)
    if len(nonce) != NONCE_SIZE:
        raise ValueError("A 96-bit nonce is required")
    ciphertext_and_tag = CIPHERS[algorithm](key).encrypt(nonce, raw, header)
    return MAGIC + struct.pack(">H", len(header)) + header + nonce + ciphertext_and_tag


def parse_envelope(envelope: bytes) -> tuple[bytes, bytes, bytes, dict]:
    if not envelope.startswith(MAGIC) or len(envelope) < len(MAGIC) + 2:
        raise ValueError("Invalid envelope")
    pos = len(MAGIC)
    header_len = struct.unpack(">H", envelope[pos:pos + 2])[0]
    pos += 2
    header = envelope[pos:pos + header_len]
    pos += header_len
    nonce = envelope[pos:pos + NONCE_SIZE]
    pos += NONCE_SIZE
    if len(nonce) != NONCE_SIZE or len(envelope) - pos < TAG_SIZE:
        raise ValueError("Truncated envelope")
    metadata = json.loads(header.decode("utf-8"))
    return header, nonce, envelope[pos:], metadata


def decrypt(envelope: bytes, key: bytes) -> tuple[bytes, dict]:
    header, nonce, body, metadata = parse_envelope(envelope)
    algorithm = metadata["algorithm"]
    if algorithm not in CIPHERS:
        raise ValueError(f"Unsupported cipher: {algorithm}")
    plaintext = CIPHERS[algorithm](key).decrypt(nonce, body, header)
    return plaintext, metadata


def entropy_u8(data: np.ndarray) -> float:
    counts = np.bincount(np.asarray(data, dtype=np.uint8).ravel(), minlength=256)
    probs = counts[counts > 0] / counts.sum()
    return float(-(probs * np.log2(probs)).sum())


def corr_adjacent(data: np.ndarray) -> tuple[float, float]:
    a = np.asarray(data, dtype=np.float64)
    if a.ndim == 2:
        a = a[:, :, None]
    horiz_x, horiz_y = a[:, :-1, :].ravel(), a[:, 1:, :].ravel()
    vert_x, vert_y = a[:-1, :, :].ravel(), a[1:, :, :].ravel()
    def corr(x, y):
        if x.size < 2 or np.std(x) == 0 or np.std(y) == 0:
            return float("nan")
        return float(np.corrcoef(x, y)[0, 1])
    return corr(horiz_x, horiz_y), corr(vert_x, vert_y)


def npcr_uaci(x: bytes, y: bytes) -> tuple[float, float]:
    if len(x) != len(y) or not x:
        raise ValueError("NPCR/UACI inputs must have equal, nonzero lengths")
    a = np.frombuffer(x, dtype=np.uint8).astype(np.int16)
    b = np.frombuffer(y, dtype=np.uint8).astype(np.int16)
    npcr = float(np.mean(a != b) * 100)
    uaci = float(np.mean(np.abs(a - b)) / 255 * 100)
    return npcr, uaci


def image_to_raw(path: Path) -> tuple[bytes, bytes, np.ndarray, Image.Image]:
    image = Image.open(path).convert("RGB")
    arr = np.asarray(image, dtype=np.uint8)
    header = canonical_header("", image.width, image.height, "RGB")
    return arr.tobytes(), header, arr, image


def body_bytes(envelope: bytes) -> bytes:
    _, _, body, _ = parse_envelope(envelope)
    return body[:-TAG_SIZE]


def tamper_rejected(envelope: bytes, key: bytes) -> bool:
    damaged = bytearray(envelope)
    damaged[-1] ^= 1
    try:
        decrypt(bytes(damaged), key)
    except InvalidTag:
        return True
    return False


def header_tamper_rejected(envelope: bytes, key: bytes) -> bool:
    header, nonce, body, _ = parse_envelope(envelope)
    altered = header.replace(b'"mode":"RGB"', b'"mode":"RBG"', 1)
    if altered == header:
        return False
    frame = MAGIC + struct.pack(">H", len(altered)) + altered + nonce + body
    try:
        decrypt(frame, key)
    except InvalidTag:
        return True
    return False


def run_metrics_and_tamper(raw: bytes, width: int, height: int,
                           algorithm: str) -> dict:
    header = canonical_header(algorithm, width, height, "RGB")
    key = secrets.token_bytes(32)
    e1 = encrypt(raw, header, key, algorithm)
    recovered, metadata = decrypt(e1, key)
    assert recovered == raw, "round-trip mismatch"
    assert metadata["width"] == width and metadata["height"] == height
    assert tamper_rejected(e1, key), "tampered ciphertext was accepted"
    assert header_tamper_rejected(e1, key), "tampered authenticated metadata was accepted"
    try:
        decrypt(e1, secrets.token_bytes(32))
    except InvalidTag:
        wrong_key_rejected = True
    else:
        wrong_key_rejected = False
    assert wrong_key_rejected, "ciphertext was accepted under the wrong key"

    # Controls: changing only the nonce already randomizes the body. Compare
    # that with a one-byte plaintext change under another fresh nonce.
    e2 = encrypt(raw, header, key, algorithm)
    repeated_plain_npcr, repeated_plain_uaci = npcr_uaci(body_bytes(e1), body_bytes(e2))
    changed = bytearray(raw)
    changed[len(changed) // 2] ^= 1
    e_changed_fresh = encrypt(bytes(changed), header, key, algorithm)
    changed_fresh_npcr, changed_fresh_uaci = npcr_uaci(
        body_bytes(e1), body_bytes(e_changed_fresh)
    )

    # UNSAFE controlled experiment: nonce reuse is forbidden for actual use.
    # The goal is to show that byte-level NPCR/UACI are not a security proof.
    fixed_nonce = b"\x00" * NONCE_SIZE
    e_fixed = encrypt(raw, header, key, algorithm, nonce=fixed_nonce)
    e_fixed_changed = encrypt(bytes(changed), header, key, algorithm, nonce=fixed_nonce)
    reused_nonce_npcr, reused_nonce_uaci = npcr_uaci(
        body_bytes(e_fixed), body_bytes(e_fixed_changed)
    )
    xor_leak = bytes(a ^ b for a, b in zip(body_bytes(e_fixed), body_bytes(e_fixed_changed)))
    plaintext_xor = bytes(a ^ b for a, b in zip(raw, changed))
    assert xor_leak == plaintext_xor, "expected stream-cipher nonce-reuse relation did not hold"

    cipher_arr = np.frombuffer(body_bytes(e1), dtype=np.uint8).reshape(height, width, 3)
    hc, vc = corr_adjacent(cipher_arr)
    return {
        "roundtrip_ok": True,
        "tamper_rejected": True,
        "header_tamper_rejected": True,
        "wrong_key_rejected": True,
        "ciphertext_entropy_bits_per_byte": entropy_u8(cipher_arr),
        "ciphertext_adjacent_corr_h": hc,
        "ciphertext_adjacent_corr_v": vc,
        "same_plain_fresh_nonce_npcr_pct": repeated_plain_npcr,
        "same_plain_fresh_nonce_uaci_pct": repeated_plain_uaci,
        "one_byte_change_fresh_nonce_npcr_pct": changed_fresh_npcr,
        "one_byte_change_fresh_nonce_uaci_pct": changed_fresh_uaci,
        "nonce_reuse_one_byte_change_npcr_pct_UNSAFE": reused_nonce_npcr,
        "nonce_reuse_one_byte_change_uaci_pct_UNSAFE": reused_nonce_uaci,
        "nonce_reuse_xor_leak_reproduced_UNSAFE": True,
    }


def benchmark_one(raw: bytes, width: int, height: int, algorithm: str,
                  repeats: int = 9) -> dict:
    header = canonical_header(algorithm, width, height, "RGB")
    key = secrets.token_bytes(32)
    # Warm-up is excluded from timing.
    warm = encrypt(raw, header, key, algorithm)
    decrypt(warm, key)
    enc, dec = [], []
    for _ in range(repeats):
        t0 = time.perf_counter_ns()
        envelope = encrypt(raw, header, key, algorithm)
        t1 = time.perf_counter_ns()
        opened, _ = decrypt(envelope, key)
        t2 = time.perf_counter_ns()
        assert opened == raw
        enc.append((t1 - t0) / 1e6)
        dec.append((t2 - t1) / 1e6)
    median_enc = statistics.median(enc)
    median_dec = statistics.median(dec)
    mib = len(raw) / (1024 * 1024)
    return {
        "algorithm": algorithm,
        "width": width,
        "height": height,
        "raw_bytes": len(raw),
        "encrypt_median_ms": median_enc,
        "decrypt_median_ms": median_dec,
        "encrypt_mib_s": mib / (median_enc / 1000),
        "decrypt_mib_s": mib / (median_dec / 1000),
    }


def main() -> None:
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(p for p in IMAGE_DIR.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"})
    if not files:
        raise SystemExit(f"No downloaded images found in {IMAGE_DIR}")
    rows = []
    diagnostic_rows = []
    for path in files:
        raw, _, arr, image = image_to_raw(path)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        for algorithm in CIPHERS:
            result = benchmark_one(raw, image.width, image.height, algorithm)
            result.update({"image": path.name, "sha256": digest})
            rows.append(result)
            diagnostic = run_metrics_and_tamper(raw, image.width, image.height, algorithm)
            diagnostic.update({"image": path.name, "sha256": digest, "algorithm": algorithm})
            diagnostic_rows.append(diagnostic)
            print(f"{path.name} | {algorithm}: round-trip/tamper OK; "
                  f"encrypt {result['encrypt_mib_s']:.2f} MiB/s; "
                  f"entropy {diagnostic['ciphertext_entropy_bits_per_byte']:.4f} bits/byte")
    for filename, output_rows in [
        ("aead_timing.csv", rows),
        ("metric_nonce_diagnostics.csv", diagnostic_rows),
    ]:
        keys = list(output_rows[0])
        with (RESULT_DIR / filename).open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(output_rows)
    print(f"Saved {len(rows)} timing rows and {len(diagnostic_rows)} diagnostic rows to {RESULT_DIR}")


if __name__ == "__main__":
    main()

