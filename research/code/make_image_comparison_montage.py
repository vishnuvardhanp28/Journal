"""Rebuild the all-20-image original/ciphertext-preview/decryption figure.

Ciphertext panels are display-only reshapes of authenticated ciphertext bytes.
The binary .imgenc containers and DEMO_ONLY keys are retained for this public
benchmark illustration, allowing the exact per-image outputs and attack probes
to be checked. These disclosed keys are insecure and must never be reused.
"""
from __future__ import annotations

import csv
import hashlib
from pathlib import Path
import secrets
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from secure_image_bench import canonical_header, decrypt, encrypt, parse_envelope, TAG_SIZE, entropy_u8, npcr_uaci

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "benchmarks" / "usc_sipi"
RESULTS = ROOT / "results" / "ten_by_ten_montage"
FIGURE = ROOT / "manuscript" / "figures" / "image_comparison_montage.png"
CSV_OUT = ROOT / "results" / "ten_by_ten_montage_verification.csv"
ALGORITHM = "AES-256-GCM"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def font(size: int, bold: bool = False):
    candidates = [
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
    ]
    for candidate in candidates:
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def render_case(entry: dict[str, str]) -> dict[str, object]:
    source = ROOT / entry["relative_path"]
    expected_mode = "L" if entry["subset"] == "grayscale" else "RGB"
    with Image.open(source) as input_image:
        image = input_image.copy()
    if image.mode != expected_mode:
        raise ValueError(f"{source}: expected {expected_mode}, got {image.mode}")
    raw = image.tobytes()
    aad = canonical_header(ALGORITHM, image.width, image.height, image.mode)
    key = secrets.token_bytes(32)
    envelope = encrypt(raw, aad, key, ALGORITHM)
    _, nonce, body_and_tag, metadata = parse_envelope(envelope)
    if metadata["mode"] != image.mode or len(body_and_tag) != len(raw) + TAG_SIZE:
        raise AssertionError(f"Unexpected encrypted envelope for {source.name}")
    recovered, opened_metadata = decrypt(envelope, key)
    exact = recovered == raw and opened_metadata == metadata
    if not exact:
        raise AssertionError(f"Pixel round-trip failed for {source.name}")

    body = body_and_tag[:-TAG_SIZE]
    cipher_preview = Image.frombytes(image.mode, image.size, body)
    paper_id = int(entry["paper_id"])
    out_name = f"image_{paper_id:02d}"
    original_path = RESULTS / f"{out_name}_original.png"
    cipher_path = RESULTS / f"{out_name}_cipher_preview.png"
    decrypted_path = RESULTS / f"{out_name}_decrypted.png"
    RESULTS.mkdir(parents=True, exist_ok=True)
    encrypted_dir = RESULTS / "encrypted"
    key_dir = RESULTS / "demo_keys"
    encrypted_dir.mkdir(parents=True, exist_ok=True)
    key_dir.mkdir(parents=True, exist_ok=True)
    container_path = encrypted_dir / f"{out_name}.imgenc"
    key_path = key_dir / f"{out_name}_DEMO_ONLY.key.txt"
    container_path.write_bytes(envelope)
    key_path.write_text(key.hex() + "\n", encoding="ascii")
    image.save(original_path, format="PNG")
    cipher_preview.save(cipher_path, format="PNG")
    Image.frombytes(image.mode, image.size, recovered).save(decrypted_path, format="PNG")

    return {
        "paper_image_no": paper_id, "mode": entry["subset"], "source_asset_id": entry["dataset_id"],
        "source_file": source.name, "width": image.width, "height": image.height,
        "algorithm": ALGORITHM, "nonce_bytes": len(nonce),
        "plaintext_entropy_bits_per_byte": entropy_u8(np.frombuffer(raw, dtype=np.uint8)),
        "ciphertext_body_entropy_bits_per_byte": entropy_u8(np.frombuffer(body, dtype=np.uint8)),
        "decrypted_entropy_bits_per_byte": entropy_u8(np.frombuffer(recovered, dtype=np.uint8)),
        "plaintext_vs_ciphertext_NPCR_bytes_pct": npcr_uaci(raw, body)[0],
        "plaintext_vs_ciphertext_UACI_bytes_pct": npcr_uaci(raw, body)[1],
        "exact_pixel_match": exact, "source_sha256": sha(source.read_bytes()),
        "plaintext_pixel_sha256": sha(raw), "container_sha256": sha(envelope),
        "container_file": container_path.relative_to(ROOT).as_posix(),
        "demo_only_key_file": key_path.relative_to(ROOT).as_posix(),
        "preview_file": cipher_path.relative_to(ROOT).as_posix(),
        "binary_container_saved": True, "key_saved_demo_only": True,
    }


def draw_panel(draw: ImageDraw.ImageDraw, panel_x: int, panel_y: int,
               panel_w: int, row_h: int, heading: str,
               entries: list[dict[str, object]], figure: Image.Image) -> None:
    label_w = 138
    gap = 12
    col_w = (panel_w - label_w - 2 * gap) // 3
    heading_font = font(31, True)
    col_font = font(23, True)
    id_font = font(21, True)
    draw.text((panel_x + label_w, panel_y), heading, fill="#183b5b", font=heading_font)
    column_top = panel_y + 48
    for i, title in enumerate(("Original", "Ciphertext-byte preview", "Decrypted")):
        x = panel_x + label_w + i * (col_w + gap)
        draw.text((x + 6, column_top), title, fill="#263746", font=col_font)
    top = column_top + 34
    for index, entry in enumerate(entries):
        y = top + index * row_h
        ident = str(int(entry["paper_id"]))
        file_ident = f"{int(entry['paper_id']):02d}"
        draw.text((panel_x, y + 8), ident, fill="#253746", font=id_font)
        paths = [
            RESULTS / f"image_{file_ident}_original.png",
            RESULTS / f"image_{file_ident}_cipher_preview.png",
            RESULTS / f"image_{file_ident}_decrypted.png",
        ]
        for col, image_path in enumerate(paths):
            x = panel_x + label_w + col * (col_w + gap)
            frame = (x, y, x + col_w - 4, y + row_h - 8)
            draw.rectangle(frame, outline="#aebbc6", width=2)
            with Image.open(image_path) as im:
                tile = im.copy()
            tile.thumbnail((col_w - 20, row_h - 26), Image.Resampling.LANCZOS)
            px = x + (col_w - tile.width) // 2
            py = y + (row_h - tile.height - 8) // 2
            if tile.mode == "L":
                tile = tile.convert("RGB")
            canvas = Image.new("RGB", tile.size, "white")
            canvas.paste(tile)
            im_canvas = canvas
            figure.paste(im_canvas, (px, py))


def main() -> None:
    with (DATA / "manifest.csv").open(newline="", encoding="utf-8") as stream:
        manifest = list(csv.DictReader(stream))
    grayscale = [r for r in manifest if r["subset"] == "grayscale" and not r["derived_from"]]
    color = [r for r in manifest if r["subset"] == "color" and not r["derived_from"]]
    if len(grayscale) != 10 or len(color) != 10:
        raise ValueError(f"Expected 10 native grayscale and 10 native RGB inputs; got {len(grayscale)} and {len(color)}")
    indexed = []
    for serial, entry in enumerate(grayscale + color, start=1):
        indexed.append({**entry, "paper_id": str(serial)})
    grayscale = indexed[:10]
    color = indexed[10:]
    records = [render_case(entry) for entry in indexed]
    fieldnames = list(records[0])
    with CSV_OUT.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    width, row_h = 3200, 190
    header_h, bottom_h, margin, gutter = 112, 32, 30, 34
    panel_w = (width - 2 * margin - gutter) // 2
    height = header_h + 10 * row_h + bottom_h
    figure = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(figure)
    draw_panel(draw, margin, 12, panel_w, row_h, "Grayscale images 1 to 10", grayscale, figure)
    draw_panel(draw, margin + panel_w + gutter, 12, panel_w, row_h, "Color images 11 to 20", color, figure)
    foot = font(20)
    draw.text((margin, height - bottom_h + 3),
              "NPCR/UACI compare each plaintext byte array with its encrypted body reshaped to image mode; these are descriptive cross-array differences, not differential-plaintext security tests. Keys are DEMO ONLY.",
              fill="#4a5965", font=foot)
    FIGURE.parent.mkdir(parents=True, exist_ok=True)
    figure.save(FIGURE, format="PNG", optimize=True)
    print(f"verified {len(records)} image cases; exact pixel matches={sum(bool(x['exact_pixel_match']) for x in records)}")
    print(f"image numbering 1--10 grayscale; 11--20 color; container files and demo-only keys saved")
    print(f"figure={FIGURE.resolve()}")
    print(f"verification={CSV_OUT.resolve()}")


if __name__ == "__main__":
    main()
