"""Fetch a small NASA Images API corpus and retain per-file attribution metadata."""
from __future__ import annotations
import csv, hashlib, json, urllib.request
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
IMAGE_DIR = ROOT / "data" / "images"
IMAGE_DIR.mkdir(parents=True, exist_ok=True)
NASA_IDS = ["PIA00123", "PIA00342", "PIA13081", "PIA25861", "PIA02860", "PIA08613"]
UA = "VishnuResearchImageBench/0.1 (academic benchmark; NASA Images API)"

def get_json(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=45) as response:
        return json.loads(response.read().decode("utf-8"))

records = []
for nasa_id in NASA_IDS:
    search = get_json(f"https://images-api.nasa.gov/search?q={nasa_id}&media_type=image&page_size=20")
    item = next((x for x in search["collection"]["items"]
                 if x.get("data", [{}])[0].get("nasa_id") == nasa_id), None)
    if item is None:
        raise RuntimeError(f"NASA API did not return metadata for {nasa_id}")
    data = item["data"][0]
    credit = data.get("secondary_creator", "") or data.get("photographer", "")
    rights_text = (credit + " " + data.get("description", "")).upper()
    if "CC BY-NC" in rights_text or "COPYRIGHT PROTECTED" in rights_text:
        raise RuntimeError(f"Restricted/third-party rights marker for {nasa_id}: {credit}")
    collection = get_json(f"https://images-assets.nasa.gov/image/{nasa_id}/collection.json")
    image_urls = [u for u in collection if u.lower().endswith((".jpg", ".jpeg", ".png"))]
    preferred = next((u for u in image_urls if "~orig." in u), None)
    if preferred is None:
        preferred = next((u for u in image_urls if "~large." in u), None)
    if preferred is None:
        raise RuntimeError(f"No original/large image file listed for {nasa_id}")
    suffix = Path(preferred.split("?")[0]).suffix.lower() or ".jpg"
    dest = IMAGE_DIR / f"{nasa_id}{suffix}"
    req = urllib.request.Request(preferred.replace("http://", "https://"), headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as response, dest.open("wb") as out:
        out.write(response.read())
    with Image.open(dest) as im:
        width, height = im.size
        mode = im.mode
    digest = hashlib.sha256(dest.read_bytes()).hexdigest()
    record = {
        "file": dest.name,
        "sha256": digest,
        "width": width,
        "height": height,
        "mode": mode,
        "nasa_id": nasa_id,
        "title": data.get("title", ""),
        "center": data.get("center", ""),
        "creator_credit": credit,
        "date_created": data.get("date_created", ""),
        "source_page": f"https://images.nasa.gov/details/{nasa_id}",
        "download_url": preferred.replace("http://", "https://"),
        "usage_note": "NASA media; check the item-specific credit and NASA Media Usage Guidelines before publication. Attribute NASA and credited contributors; exclude NASA logos/identifiers and do not imply endorsement.",
        "description": data.get("description", "").replace("\n", " "),
    }
    records.append(record)
    print(f"Downloaded {dest.name}: {record['title']} ({dest.stat().st_size} bytes)")

with (ROOT / "data" / "image_manifest.json").open("w", encoding="utf-8") as f:
    json.dump(records, f, ensure_ascii=False, indent=2)
with (ROOT / "data" / "image_manifest.csv").open("w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(records[0]))
    writer.writeheader()
    writer.writerows(records)




