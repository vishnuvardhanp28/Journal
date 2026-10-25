"""Create visible color-image AEAD examples and expanded attack diagnostics.

Important: every cryptographic experiment here evaluates AES-GCM or
ChaCha20-Poly1305 reference controls, not any of the six custom paper ciphers.
The ciphertext preview is the authenticated ciphertext body reshaped to RGB
for display; it is not the actual binary container and is clearly labeled.
"""
from __future__ import annotations
import csv
import hashlib
import json
import math
import secrets
import statistics
import struct
import time
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.stats import chisquare, ttest_ind

from image_aead_prototype import open_image_file
from secure_image_bench import CIPHERS, canonical_header, decrypt, encrypt, parse_envelope

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "benchmarks" / "usc_sipi" / "manifest.csv"
OUT = ROOT / "results" / "expanded_color_demo"
FIG = OUT / "figures"
IMAGE_IDS = ["4.1.07", "4.1.08"]  # USC-SIPI states these USC jelly-bean photographs are free to use.
ALGORITHMS = ["AES-256-GCM", "ChaCha20-Poly1305"]
SEED = 20261025
FILE_REPEATS = 30
DIFFERENTIAL_REPEATS = 30
CPA_TRIALS = 500
KPA_TRIALS = 100
WRONG_KEY_TRIALS = 100
TIMING_TRIALS_PER_CLASS = 1500
NONCE_BYTES = 12
TAG_BYTES = 16


def entropy_u8(data: np.ndarray) -> float:
    counts = np.bincount(np.asarray(data, dtype=np.uint8).ravel(), minlength=256)
    probs = counts[counts > 0] / counts.sum()
    return float(-(probs * np.log2(probs)).sum())


def npcr_uaci(a: np.ndarray, b: np.ndarray) -> tuple[float, float]:
    a = np.asarray(a, dtype=np.uint8).ravel().astype(np.int16)
    b = np.asarray(b, dtype=np.uint8).ravel().astype(np.int16)
    return float(np.mean(a != b) * 100), float(np.mean(np.abs(a - b)) / 255 * 100)


def corr_flat(x: np.ndarray, y: np.ndarray) -> float:
    x = np.asarray(x, dtype=np.float64).ravel()
    y = np.asarray(y, dtype=np.float64).ravel()
    if x.std() == 0 or y.std() == 0:
        return 0.0
    return float(np.corrcoef(x, y)[0, 1])


def rgb_correlation(image: np.ndarray) -> dict[str, float]:
    out: dict[str, float] = {}
    labels = ("R", "G", "B")
    for c, label in enumerate(labels):
        plane = image[:, :, c]
        out[f"{label}_horizontal"] = corr_flat(plane[:, :-1], plane[:, 1:])
        out[f"{label}_vertical"] = corr_flat(plane[:-1, :], plane[1:, :])
        out[f"{label}_diagonal"] = corr_flat(plane[:-1, :-1], plane[1:, 1:])
    return out


def wilson_interval(successes: int, trials: int, z: float = 1.959963984540054) -> tuple[float, float]:
    p = successes / trials
    den = 1 + z*z/trials
    center = (p + z*z/(2*trials)) / den
    half = z * math.sqrt((p*(1-p) + z*z/(4*trials))/trials) / den
    return center-half, center+half


def png_ciphertext_view(envelope: bytes, shape: tuple[int, int, int]) -> np.ndarray:
    _, _, body, _ = parse_envelope(envelope)
    cipher_bytes = body[:-TAG_BYTES]  # exclude the authentication tag from the raster preview
    expected = int(np.prod(shape))
    if len(cipher_bytes) != expected:
        raise ValueError(f"Ciphertext length {len(cipher_bytes)} != RGB raster bytes {expected}")
    return np.frombuffer(cipher_bytes, dtype=np.uint8).reshape(shape).copy()


def inject_noise(envelope: bytes, rng: np.random.Generator, density: float, kind: str) -> bytes:
    header, nonce, body, _ = parse_envelope(envelope)
    cipher = bytearray(body[:-TAG_BYTES])
    n = max(1, int(round(len(cipher) * density)))
    indexes = rng.choice(len(cipher), size=min(n, len(cipher)), replace=False)
    if kind == "salt_pepper":
        for i in indexes:
            cipher[int(i)] = 0 if rng.integers(0, 2) == 0 else 255
    elif kind == "gaussian":
        for i in indexes:
            cipher[int(i)] = int(np.clip(int(cipher[int(i)]) + int(rng.normal(0, 32)), 0, 255))
    else:
        raise ValueError(kind)
    return envelope[:len(envelope)-len(body)] + bytes(cipher) + body[-TAG_BYTES:]


def alter_metadata(envelope: bytes) -> bytes:
    # Change one authenticated byte in the JSON header without changing its length.
    header, _, _, _ = parse_envelope(envelope)
    pos = envelope.index(header)
    damaged = bytearray(envelope)
    damaged[pos] ^= 1
    return bytes(damaged)


def quick_reject(envelope: bytes, key: bytes) -> bool:
    try:
        decrypt(envelope, key)
    except Exception:
        return True
    return False


def calculate_histograms(axes, image: np.ndarray) -> None:
    colors = ("red", "green", "blue")
    x = np.arange(256)
    for channel, (color, name) in enumerate(zip(colors, ("R", "G", "B"))):
        counts = np.bincount(image[:, :, channel].ravel(), minlength=256)
        axes.plot(x, counts, color=color, linewidth=0.8, label=name)
    axes.set_xlim(0, 255)
    axes.set_xlabel("Pixel value")
    axes.set_ylabel("Count")
    axes.grid(alpha=0.18)
    axes.legend(fontsize=6, ncol=3, loc="upper right", frameon=False)


def build_composite(cases: list[dict]) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(4, 3, figsize=(12, 14))
    col_titles = ("Original image", "Ciphertext-byte visualization", "Decrypted image")
    for col, title in enumerate(col_titles):
        axes[0, col].set_title(title, fontsize=12, weight="bold")
    for idx, case in enumerate(cases):
        image_row = idx * 2
        hist_row = image_row + 1
        imgs = [case["original"], case["cipher_view"], case["decrypted"]]
        captions = [
            f"{case['image_id']} — original",
            f"{case['algorithm']} ciphertext bytes\nreshaped as RGB (display only)",
            f"{case['image_id']} — exact decryption",
        ]
        for col, (ax, img, caption) in enumerate(zip(axes[image_row], imgs, captions)):
            ax.imshow(img)
            ax.set_title(caption, fontsize=9)
            ax.set_axis_off()
            calculate_histograms(axes[hist_row, col], img)
            axes[hist_row, col].set_title(f"Histogram: {caption.splitlines()[0]}", fontsize=8)
    fig.suptitle("Authenticated image encryption: two color examples and channel histograms", fontsize=15, weight="bold")
    fig.text(0.5, 0.018,
             "Ciphertext preview = encrypted pixel-body bytes reshaped as RGB for display; the .imgenc file is binary. Decrypted pixels match exactly.",
             ha="center", fontsize=8)
    fig.subplots_adjust(left=0.08, right=0.98, top=0.94, bottom=0.055, hspace=0.52, wspace=0.22)
    fig.savefig(FIG / "color_original_ciphertext_decrypted_histograms.png", dpi=240, bbox_inches="tight")
    plt.close(fig)


def make_cases(entries: dict[str, dict]) -> tuple[list[dict], list[dict], list[dict]]:
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    (OUT / "encrypted").mkdir(exist_ok=True)
    (OUT / "decrypted").mkdir(exist_ok=True)
    (OUT / "ciphertext_views").mkdir(exist_ok=True)
    (OUT / "demo_keys").mkdir(exist_ok=True)
    rng = np.random.default_rng(SEED)
    file_rows: list[dict] = []
    per_case: list[dict] = []
    visuals: list[dict] = []
    for image_id in IMAGE_IDS:
        source = ROOT / entries[image_id]["relative_path"]
        with Image.open(source) as im:
            if im.mode != "RGB":
                raise ValueError(f"Expected RGB: {source} mode={im.mode}")
            original = np.asarray(im).copy()
        h, w, channels = original.shape
        raw = original.tobytes()
        header = canonical_header("AES-256-GCM", w, h, "RGB")
        # The same sealed bytes are reused for the visual comparison; every call uses fresh nonce.
        sample_key = secrets.token_bytes(32)
        key_path = OUT / "demo_keys" / f"{image_id}_AES-256-GCM_DEMO_ONLY.key.txt"
        key_path.write_text(sample_key.hex() + "\n", encoding="ascii")
        envelope = encrypt(raw, header, sample_key, "AES-256-GCM")
        cipher_view = png_ciphertext_view(envelope, original.shape)
        cipher_path = OUT / "ciphertext_views" / f"{image_id}_aes_gcm_ciphertext_bytes.png"
        Image.fromarray(cipher_view, "RGB").save(cipher_path)
        encrypted_path = OUT / "encrypted" / f"{image_id}_AES-256-GCM.imgenc"
        encrypted_path.write_bytes(envelope)
        # One exact open writes a user-viewable lossless PNG; only the 4.1.07/08 source images are used.
        decrypted_path = OUT / "decrypted" / f"{image_id}_AES-256-GCM_decrypted.png"
        decrypted, _ = decrypt(envelope, sample_key)
        if decrypted != raw:
            raise AssertionError(f"Pixel mismatch for {image_id}")
        Image.frombytes("RGB", (w, h), decrypted).save(decrypted_path, format="PNG", compress_level=1)
        with Image.open(decrypted_path) as dec_im:
            dec_array = np.asarray(dec_im).copy()
        if not np.array_equal(original, dec_array):
            raise AssertionError(f"Saved PNG differs from source pixels: {image_id}")
        visuals.append({
            "image_id": image_id,
            "source_file": source.name,
            "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "source_mode": "RGB",
            "width": w,
            "height": h,
            "algorithm": "AES-256-GCM",
            "encrypted_binary": str(encrypted_path.relative_to(OUT)),
            "demo_key_sidecar": str(key_path.relative_to(OUT)),
            "encrypted_binary_sha256": hashlib.sha256(envelope).hexdigest(),
            "ciphertext_display_png": str(cipher_path.relative_to(OUT)),
            "decrypted_png": str(decrypted_path.relative_to(OUT)),
            "decryption_exact_pixel_match": True,
            "key_fingerprint_sha256_prefix": hashlib.sha256(sample_key).hexdigest()[:16],
            "key_included_in_demo_key_sidecar": True,
            "warning": "demo key is intentionally included for reproducibility; do not reuse or treat this sample as secure key management",
        })

        # Fresh per-run secret key for matched full-file timing and attack diagnostics.
        for algorithm in ALGORITHMS:
            key = secrets.token_bytes(32)
            key_id = hashlib.sha256(key).hexdigest()[:16]
            sealed_path = OUT / "encrypted" / f"{image_id}_{algorithm}.imgenc"
            recovered_path = OUT / "decrypted" / f"{image_id}_{algorithm}_decrypted.png"
            # File-level timing: image load -> AEAD -> authenticated container, and back -> PNG output.
            seal_image = __import__("image_aead_prototype").seal_image_file
            seal_image(source, sealed_path, key, algorithm)
            open_image_file(sealed_path, recovered_path, key, png_compress_level=1)
            enc_ms: list[float] = []
            dec_ms: list[float] = []
            for _ in range(FILE_REPEATS):
                t0 = time.perf_counter_ns()
                seal_image(source, sealed_path, key, algorithm)
                t1 = time.perf_counter_ns()
                open_image_file(sealed_path, recovered_path, key, png_compress_level=1)
                t2 = time.perf_counter_ns()
                enc_ms.append((t1-t0)/1e6)
                dec_ms.append((t2-t1)/1e6)
                with Image.open(recovered_path) as test_image:
                    if test_image.mode != "RGB" or test_image.size != (w, h) or test_image.tobytes() != raw:
                        raise AssertionError(f"File API round trip failed: {image_id}/{algorithm}")
            enc_median = statistics.median(enc_ms)
            dec_median = statistics.median(dec_ms)
            per_mib = len(raw)/(1024*1024)
            file_rows.append({
                "image_id": image_id,
                "algorithm": algorithm,
                "width": w,
                "height": h,
                "raw_bytes": len(raw),
                "file_repetitions": FILE_REPEATS,
                "png_compress_level": 1,
                "seal_median_ms": enc_median,
                "open_plus_png_median_ms": dec_median,
                "seal_MiB_s": per_mib/(enc_median/1000),
                "open_plus_png_MiB_s": per_mib/(dec_median/1000),
                "key_fingerprint_prefix": key_id,
                "exact_round_trip": True,
            })

            # In-memory AEAD timing isolates the cipher+header from image codecs and file I/O.
            aad = canonical_header(algorithm, w, h, "RGB")
            inmem_enc: list[float] = []
            inmem_dec: list[float] = []
            last_envelope = b""
            for _ in range(100):
                t0 = time.perf_counter_ns()
                last_envelope = encrypt(raw, aad, key, algorithm)
                t1 = time.perf_counter_ns()
                recovered, _ = decrypt(last_envelope, key)
                t2 = time.perf_counter_ns()
                if recovered != raw:
                    raise AssertionError("In-memory exact round trip failed")
                inmem_enc.append((t1-t0)/1e6)
                inmem_dec.append((t2-t1)/1e6)
            inmem_enc_median = statistics.median(inmem_enc)
            inmem_dec_median = statistics.median(inmem_dec)

            # Image metrics: cipher body is shown as a raster only for diagnostics.
            cipher_array = png_ciphertext_view(last_envelope, original.shape)
            channel_entropy = {name: entropy_u8(cipher_array[:,:,i]) for i,name in enumerate(("R","G","B"))}
            channel_hist_chi2 = {}
            for i, name in enumerate(("R","G","B")):
                counts = np.bincount(cipher_array[:,:,i].ravel(), minlength=256)
                channel_hist_chi2[name] = {
                    "chi_square": float(chisquare(counts).statistic),
                    "p_value": float(chisquare(counts).pvalue),
                }
            correlations = rgb_correlation(cipher_array)
            corr_abs_mean = statistics.mean(abs(v) for v in correlations.values())

            # Fresh-nonce NPCR/UACI on same and one-byte-changed chosen inputs.
            npcr_same: list[float] = []
            uaci_same: list[float] = []
            npcr_changed: list[float] = []
            uaci_changed: list[float] = []
            for _ in range(DIFFERENTIAL_REPEATS):
                e1 = encrypt(raw, aad, key, algorithm)
                e2 = encrypt(raw, aad, key, algorithm)
                c1 = png_ciphertext_view(e1, original.shape)
                c2 = png_ciphertext_view(e2, original.shape)
                n, u = npcr_uaci(c1, c2)
                npcr_same.append(n); uaci_same.append(u)
                changed = bytearray(raw)
                idx = int(rng.integers(0, len(changed)))
                changed[idx] ^= 1
                e3 = encrypt(bytes(changed), aad, key, algorithm)
                c3 = png_ciphertext_view(e3, original.shape)
                n, u = npcr_uaci(c1, c3)
                npcr_changed.append(n); uaci_changed.append(u)

            # Basic ciphertext-only byte metrics and length/metadata disclosure.
            # CPA challenge: fixed equal-length chosen messages, random hidden bit, fresh nonce,
            # simple classifier uses only ciphertext-body mean byte.
            zero_msg = bytes(len(raw))
            full_msg = bytes([255]) * len(raw)
            challenge_rng = np.random.default_rng(SEED + (0 if algorithm == ALGORITHMS[0] else 1))
            right = 0
            class_mean = {"0": [], "1": []}
            for _ in range(CPA_TRIALS):
                bit = int(challenge_rng.integers(0, 2))
                msg = full_msg if bit else zero_msg
                env = encrypt(msg, aad, key, algorithm)
                body = parse_envelope(env)[2][:-TAG_BYTES]
                mean_byte = float(np.frombuffer(body, dtype=np.uint8).mean())
                class_mean[str(bit)].append(mean_byte)
                guess = int(mean_byte > 127.5)
                right += (guess == bit)
            cpa_lo, cpa_hi = wilson_interval(right, CPA_TRIALS)

            # Known-plaintext keystream-transfer probe across distinct nonces.
            known_env = encrypt(raw, aad, key, algorithm)
            known_ct = parse_envelope(known_env)[2][:-TAG_BYTES]
            known_stream = bytes(a ^ b for a,b in zip(raw[:32], known_ct[:32]))
            kpa_recovered = 0
            reused_prefix = 0
            for _ in range(KPA_TRIALS):
                target = rng.integers(0, 256, size=len(raw), dtype=np.uint8).tobytes()
                target_env = encrypt(target, aad, key, algorithm)
                _, target_nonce, target_body, _ = parse_envelope(target_env)
                target_ct = target_body[:-TAG_BYTES]
                target_stream = bytes(a ^ b for a,b in zip(target[:32], target_ct[:32]))
                reused_prefix += (target_stream == known_stream)
                candidate = bytes(a ^ b for a,b in zip(target_ct[:32], known_stream))
                kpa_recovered += (candidate == target[:32])

            # Noise, bit-flip, truncation, authenticated metadata, and byte-order probes.
            attack_env = encrypt(raw, aad, key, algorithm)
            probe_rows: list[dict] = []
            for kind in ("salt_pepper", "gaussian"):
                for density in (0.001, 0.01, 0.05, 0.1):
                    damaged = inject_noise(attack_env, rng, density, kind)
                    rejected = quick_reject(damaged, key)
                    probe_rows.append({"attack":f"{kind}_noise","level":density,"rejected":rejected})
            damaged = bytearray(attack_env)
            damaged[-(TAG_BYTES+1)] ^= 1
            probe_rows.append({"attack":"single_bit_ciphertext_tamper","level":"1 bit","rejected":quick_reject(bytes(damaged),key)})
            probe_rows.append({"attack":"tag_tamper","level":"1 bit","rejected":quick_reject(attack_env[:-1]+bytes([attack_env[-1]^1]),key)})
            probe_rows.append({"attack":"authenticated_metadata_tamper","level":"1 bit","rejected":quick_reject(alter_metadata(attack_env),key)})
            probe_rows.append({"attack":"truncation","level":"1 byte","rejected":quick_reject(attack_env[:-1],key)})
            # Swap two 16-byte ciphertext blocks while leaving the tag unchanged.
            header_bytes, nonce_bytes, body_bytes, _ = parse_envelope(attack_env)
            cipher_part = bytearray(body_bytes[:-TAG_BYTES])
            cipher_part[:16], cipher_part[16:32] = cipher_part[16:32], cipher_part[:16]
            body_offset = len(attack_env)-len(body_bytes)
            swapped = attack_env[:body_offset]+bytes(cipher_part)+body_bytes[-TAG_BYTES:]
            probe_rows.append({"attack":"ciphertext_block_reordering_proxy","level":"swap 16-byte blocks","rejected":quick_reject(swapped,key)})
            # Random wrong-key guesses; no key material is written to disk.
            wrong_key_rejections = 0
            for _ in range(WRONG_KEY_TRIALS):
                wrong = secrets.token_bytes(32)
                if quick_reject(attack_env, wrong):
                    wrong_key_rejections += 1
            one_bit_key = bytearray(key); one_bit_key[0] ^= 1
            one_bit_key_rejected = quick_reject(attack_env, bytes(one_bit_key))

            per_case.append({
                "image_id": image_id,
                "algorithm": algorithm,
                "key_fingerprint_prefix": key_id,
                "pixels": {"width":w,"height":h,"channels":channels,"raw_bytes":len(raw)},
                "ciphertext_metrics": {
                    "byte_entropy_bits": entropy_u8(cipher_array),
                    "channel_entropy_bits": channel_entropy,
                    "channel_histogram_chi_square": channel_hist_chi2,
                    "spatial_correlation": correlations,
                    "mean_absolute_spatial_correlation": corr_abs_mean,
                },
                "differential_diagnostics": {
                    "fresh_nonce_trials": DIFFERENTIAL_REPEATS,
                    "same_plain_npcr_mean_pct": statistics.mean(npcr_same),
                    "same_plain_uaci_mean_pct": statistics.mean(uaci_same),
                    "one_byte_changed_npcr_mean_pct": statistics.mean(npcr_changed),
                    "one_byte_changed_uaci_mean_pct": statistics.mean(uaci_changed),
                },
                "chosen_plaintext_distinguisher": {
                    "trials": CPA_TRIALS,
                    "chosen_messages": "all-zero RGB image vs all-255 RGB image, same length and metadata",
                    "classifier": "ciphertext body mean byte > 127.5 predicts all-255 message",
                    "correct": right,
                    "accuracy": right/CPA_TRIALS,
                    "wilson_95_ci": [cpa_lo,cpa_hi],
                    "class_mean_ciphertext_byte": {k:statistics.mean(v) for k,v in class_mean.items()},
                    "interpretation": "one simple distinguisher test only; this is not a complete IND-CPA proof",
                },
                "known_plaintext_keystream_transfer_probe": {
                    "known_pairs":1,
                    "target_pairs":KPA_TRIALS,
                    "nonce_policy":"fresh random 96-bit nonce per encryption",
                    "target_first_32_bytes_recovered":kpa_recovered,
                    "reused_32_byte_keystream_prefixes":reused_prefix,
                    "interpretation":"simple cross-nonce XOR/keystream-transfer attempt; not general key recovery",
                },
                "integrity_probes": {
                    "all_probes_rejected": all(r["rejected"] for r in probe_rows),
                    "rejected":sum(r["rejected"] for r in probe_rows),
                    "total":len(probe_rows),
                    "rows":probe_rows,
                    "random_wrong_key_rejections":wrong_key_rejections,
                    "random_wrong_key_trials":WRONG_KEY_TRIALS,
                    "one_bit_key_change_rejected":one_bit_key_rejected,
                },
                "ciphertext_only_scope": "Histogram, entropy, correlation, and visual ciphertext-byte inspection are diagnostics; no plaintext recovery is claimed.",
                "scrambling_only_scope": "Not applicable: this AEAD construction has no separate permutation/scrambling layer. Ciphertext block-reordering is tested as an integrity probe only.",
                "timing_probe": None,
                "time_complexity": "O(n) time and O(n) memory in this whole-image Python wrapper; standard AEAD primitive is linear in message length.",
            })

        # Restore the separately identified display example after timed runs,
        # which reuse the same filenames with independent ephemeral keys.
        encrypted_path.write_bytes(envelope)
        key_path.write_text(sample_key.hex() + "\n", encoding="ascii")

    # Timing-dependence check for data classes on fixed-length inputs; diagnostic only.
    timing_rows = []
    timing_rng = np.random.default_rng(SEED + 20)
    sample_image = per_case[0]["pixels"]
    timing_source = ROOT / entries[IMAGE_IDS[0]]["relative_path"]
    with Image.open(timing_source) as im:
        timing_raw = im.tobytes()
        tw, th = im.size
    timing_aad = canonical_header(ALGORITHMS[0], tw, th, "RGB")
    for algorithm in ALGORITHMS:
        key = secrets.token_bytes(32)
        aad = canonical_header(algorithm, tw, th, "RGB")
        zero = bytes(len(timing_raw))
        random_data = timing_rng.integers(0,256,size=len(timing_raw),dtype=np.uint8).tobytes()
        labels = np.array([0]*TIMING_TRIALS_PER_CLASS+[1]*TIMING_TRIALS_PER_CLASS)
        timing_rng.shuffle(labels)
        samples = {0:[],1:[]}
        for label in labels:
            payload = zero if label == 0 else random_data
            t0=time.perf_counter_ns(); encrypt(payload,aad,key,algorithm); t1=time.perf_counter_ns()
            samples[int(label)].append((t1-t0)/1e3)
        test=ttest_ind(samples[0],samples[1],equal_var=False)
        timing_rows.append({
            "algorithm":algorithm,
            "samples_per_class":TIMING_TRIALS_PER_CLASS,
            "class_0":"all-zero image bytes",
            "class_1":"fixed pseudorandom image bytes",
            "mean_us_class_0":statistics.mean(samples[0]),
            "mean_us_class_1":statistics.mean(samples[1]),
            "median_us_class_0":statistics.median(samples[0]),
            "median_us_class_1":statistics.median(samples[1]),
            "welch_t_statistic":float(test.statistic),
            "welch_p_value":float(test.pvalue),
            "interpretation":"timing-leakage screening only; a nonsignificant result is not proof of constant-time behavior",
        })
    for item in per_case:
        item["timing_probe"] = next(x for x in timing_rows if x["algorithm"]==item["algorithm"])

    # Rebuild the requested 2-image panel with the AES-GCM visual examples only.
    aes_cases=[]
    for image_id in IMAGE_IDS:
        source=ROOT/entries[image_id]["relative_path"]
        with Image.open(source) as im: original=np.asarray(im).copy()
        key=secrets.token_bytes(32)
        aad=canonical_header("AES-256-GCM",original.shape[1],original.shape[0],"RGB")
        env=encrypt(original.tobytes(),aad,key,"AES-256-GCM")
        cipher=png_ciphertext_view(env,original.shape)
        decrypted,_=decrypt(env,key)
        decarr=np.frombuffer(decrypted,dtype=np.uint8).reshape(original.shape).copy()
        aes_cases.append({"image_id":image_id,"algorithm":"AES-256-GCM","original":original,"cipher_view":cipher,"decrypted":decarr})
    build_composite(aes_cases)

    # Save CSVs and JSON with enough detail to reproduce tables and figures.
    with (OUT/"file_timing.csv").open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=list(file_rows[0])); writer.writeheader(); writer.writerows(file_rows)
    with (OUT/"timing_attack_probe.csv").open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=list(timing_rows[0])); writer.writeheader(); writer.writerows(timing_rows)
    attack_rows=[]
    for item in per_case:
        attack_rows.append({
            "image_id":item["image_id"],"algorithm":item["algorithm"],
            "byte_entropy_bits":item["ciphertext_metrics"]["byte_entropy_bits"],
            "mean_channel_entropy_bits":statistics.mean(item["ciphertext_metrics"]["channel_entropy_bits"].values()),
            "mean_abs_spatial_correlation":item["ciphertext_metrics"]["mean_absolute_spatial_correlation"],
            "same_plain_npcr_pct":item["differential_diagnostics"]["same_plain_npcr_mean_pct"],
            "same_plain_uaci_pct":item["differential_diagnostics"]["same_plain_uaci_mean_pct"],
            "one_byte_changed_npcr_pct":item["differential_diagnostics"]["one_byte_changed_npcr_mean_pct"],
            "one_byte_changed_uaci_pct":item["differential_diagnostics"]["one_byte_changed_uaci_mean_pct"],
            "CPA_accuracy":item["chosen_plaintext_distinguisher"]["accuracy"],
            "CPA_trials":CPA_TRIALS,
            "KPA_recovered_targets":item["known_plaintext_keystream_transfer_probe"]["target_first_32_bytes_recovered"],
            "KPA_targets":KPA_TRIALS,
            "integrity_rejected":item["integrity_probes"]["rejected"],
            "integrity_total":item["integrity_probes"]["total"],
            "wrong_keys_rejected":item["integrity_probes"]["random_wrong_key_rejections"],
            "wrong_key_trials":WRONG_KEY_TRIALS,
            "one_bit_key_change_rejected":item["integrity_probes"]["one_bit_key_change_rejected"],
        })
    with (OUT/"attack_diagnostics.csv").open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=list(attack_rows[0])); writer.writeheader(); writer.writerows(attack_rows)

    summary={
        "scope":"Two color-image demos and diagnostic attack probes on standard AEAD controls only; none of the six custom ciphers is tested here.",
        "image_ids":IMAGE_IDS,
        "rights_note":"USC-SIPI states 4.1.07 and 4.1.08 were photographs taken at USC and are free to use.",
        "algorithms":ALGORITHMS,
        "file_api_round_trips":len(file_rows),
        "file_repetitions_per_case":FILE_REPEATS,
        "mean_file_seal_median_ms":statistics.mean(r["seal_median_ms"] for r in file_rows),
        "mean_file_open_plus_png_median_ms":statistics.mean(r["open_plus_png_median_ms"] for r in file_rows),
        "pixel_and_saved_png_match":"exact for all examples and timed repetitions",
        "test_counts":{"CPA_trials_per_algorithm":CPA_TRIALS,"KPA_transfer_targets_per_case":KPA_TRIALS,"random_wrong_key_trials_per_case":WRONG_KEY_TRIALS,"timing_samples_per_class_per_algorithm":TIMING_TRIALS_PER_CLASS,"fresh_nonce_differential_trials_per_case":DIFFERENTIAL_REPEATS},
        "attack_interpretation":"CPA/KPA/COA/timing results are limited diagnostic attacks against the reference AEAD implementation. They do not establish resistance of the six paper ciphers or constitute a formal proof.",
        "time_complexity":"O(n) AEAD time; O(n) memory in the whole-image API because complete raster/container buffers are held in memory.",
        "space_complexity":"O(n) peak working memory in the current wrapper; no streaming/chunked implementation is evaluated.",
        "cases":per_case,
        "visual_manifest":visuals,
        "timing_attack_probe":timing_rows,
    }
    (OUT/"expanded_security_demo.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    (OUT/"visual_manifest.json").write_text(json.dumps(visuals,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in summary.items() if k not in ("cases","visual_manifest","timing_attack_probe")},indent=2))


def main() -> None:
    with MANIFEST.open(newline="",encoding="utf-8") as f:
        entries={r["dataset_id"]:r for r in csv.DictReader(f)}
    make_cases(entries)

if __name__ == "__main__":
    main()
