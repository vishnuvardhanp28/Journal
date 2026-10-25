"""Authenticated image-file wrapper for reproducible research experiments.

Uses standard AES-256-GCM or ChaCha20-Poly1305. The wrapper is a prototype,
not a novel cipher. It authenticates image shape/mode metadata and pixel bytes.
Key provisioning and exchange are deliberately external to this module.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from PIL import Image
from secure_image_bench import (
    CIPHERS,
    canonical_header,
    decrypt,
    encrypt,
)


SUPPORTED_MODES = {"L": 1, "RGB": 3}


def seal_pixels(
    plaintext: bytes,
    width: int,
    height: int,
    mode: str,
    key: bytes,
    algorithm: str = "AES-256-GCM",
) -> bytes:
    """Encrypt pixels and authenticate dimensions, mode, algorithm, and dtype."""
    if mode not in SUPPORTED_MODES:
        raise ValueError(f"Unsupported image mode {mode!r}; use L or RGB")
    if width <= 0 or height <= 0:
        raise ValueError("Image dimensions must be positive")
    expected = width * height * SUPPORTED_MODES[mode]
    if len(plaintext) != expected:
        raise ValueError(f"Pixel payload length {len(plaintext)} != expected {expected}")
    if algorithm not in CIPHERS:
        raise ValueError(f"Unsupported algorithm {algorithm!r}")
    header = canonical_header(algorithm, width, height, mode)
    return encrypt(plaintext, header, key, algorithm)


def open_pixels(envelope: bytes, key: bytes) -> tuple[bytes, dict[str, Any]]:
    """Authenticate and recover pixels, rejecting inconsistent metadata."""
    plaintext, metadata = decrypt(envelope, key)
    mode = metadata.get("mode")
    width = metadata.get("width")
    height = metadata.get("height")
    if mode not in SUPPORTED_MODES or not isinstance(width, int) or not isinstance(height, int):
        raise ValueError("Authenticated image metadata is invalid or unsupported")
    if width <= 0 or height <= 0:
        raise ValueError("Authenticated dimensions must be positive")
    expected = width * height * SUPPORTED_MODES[mode]
    if len(plaintext) != expected:
        raise ValueError(f"Authenticated payload length {len(plaintext)} != expected {expected}")
    return plaintext, metadata


def seal_image_file(
    input_path: str | Path,
    output_path: str | Path,
    key: bytes,
    algorithm: str = "AES-256-GCM",
) -> dict[str, Any]:
    """Seal a grayscale or RGB image into a binary authenticated container."""
    with Image.open(input_path) as source:
        if source.mode not in SUPPORTED_MODES:
            raise ValueError(f"Unsupported input image mode {source.mode!r}; use L or RGB")
        image = source.copy()
    envelope = seal_pixels(image.tobytes(), image.width, image.height, image.mode, key, algorithm)
    Path(output_path).write_bytes(envelope)
    return {
        "width": image.width,
        "height": image.height,
        "mode": image.mode,
        "algorithm": algorithm,
        "plaintext_bytes": len(image.tobytes()),
        "container_bytes": len(envelope),
    }


def open_image_file(
    input_path: str | Path,
    output_path: str | Path,
    key: bytes,
    png_compress_level: int = 1,
) -> dict[str, Any]:
    """Open an authenticated container and write recovered pixels as lossless PNG."""
    envelope = Path(input_path).read_bytes()
    plaintext, metadata = open_pixels(envelope, key)
    image = Image.frombytes(metadata["mode"], (metadata["width"], metadata["height"]), plaintext)
    if not 0 <= png_compress_level <= 9:
        raise ValueError("PNG compression level must be between 0 and 9")
    image.save(output_path, format="PNG", compress_level=png_compress_level)
    return metadata

