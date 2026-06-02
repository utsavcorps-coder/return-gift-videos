"""
Return Gift Product Video Generator
Uses Shotstack API to create promotional videos from product photos.
Runs automatically via GitHub Actions cron job (2x per day).
"""

import os
import json
import time
import random
import requests
from datetime import datetime

# ── Config ────────────────────────────────────────────────────────────────────
SHOTSTACK_API_KEY = os.environ.get("SHOTSTACK_API_KEY")
SHOTSTACK_BASE    = "https://api.shotstack.io/stage/render"   # sandbox (free)
GITHUB_REPO_RAW   = os.environ.get("GITHUB_REPO_RAW")        # base URL for raw photos

HEADERS = {
    "x-api-key": SHOTSTACK_API_KEY,
    "Content-Type": "application/json",
}

# ── Helpers ───────────────────────────────────────────────────────────────────
def load_products():
    """Load product list and pick one that hasn't been used recently."""
    with open("products.json") as f:
        data = json.load(f)

    products = data["products"]

    # Try to pick a product that's least recently used
    used_log = "used_products.json"
    used = []
    if os.path.exists(used_log):
        with open(used_log) as f:
            used = json.load(f).get("used", [])

    # Filter out recently used (last 2), fall back to all if needed
    available = [p for p in products if p["id"] not in used[-2:]]
    if not available:
        available = products

    chosen = random.choice(available)

    # Update used log
    used.append(chosen["id"])
    with open(used_log, "w") as f:
        json.dump({"used": used[-10:]}, f)  # keep last 10

    return chosen


def build_video_payload(product):
    """
    Build Shotstack JSON payload for a ~20-second product promo video.
    Layout:
      0–3s   : Product photo fades in (zoom effect)
      3–10s  : Product name text overlay
      10–17s : Tagline + CTA text
      17–20s : Logo / brand name outro
    """
    photo_url = f"{GITHUB_REPO_RAW}/photos/{product['photo']}"

    payload = {
        "timeline": {
            "background": "#1a1a2e",
            "tracks": [
                # ── Track 1: Product photo (full duration) ──────────────────
                {
                    "clips": [
                        {
                            "asset": {
                                "type": "image",
                                "src": photo_url,
                            },
                            "start": 0,
                            "length": 20,
                            "effect": "zoomIn",        # gentle zoom for energy
                            "transition": {
                                "in": "fade",
                                "out": "fade",
                            },
                            "fit": "cover",
                        }
                    ]
                },
                # ── Track 2: Product name (3–10s) ───────────────────────────
                {
                    "clips": [
                        {
                            "asset": {
                                "type": "title",
                                "text": product["name"],
                                "style": "future",
                                "color": "#ffffff",
                                "size": "large",
                                "background": "transparent",
                                "position": "center",
                            },
                            "start": 3,
                            "length": 7,
                            "transition": {"in": "slideUp", "out": "fade"},
                        }
                    ]
                },
                # ── Track 3: Tagline (10–17s) ────────────────────────────────
                {
                    "clips": [
                        {
                            "asset": {
                                "type": "html",
                                "html": f"""
                                    <p style="
                                        font-family: Arial, sans-serif;
                                        font-size: 48px;
                                        color: #FFD700;
                                        text-align: center;
                                        background: rgba(0,0,0,0.5);
                                        padding: 20px 40px;
                                        border-radius: 12px;
                                    ">{product['tagline']}</p>
                                """,
                                "width": 900,
                                "height": 200,
                            },
                            "start": 10,
                            "length": 7,
                            "position": "center",
                            "transition": {"in": "fade", "out": "fade"},
                        }
                    ]
                },
                # ── Track 4: CTA / contact (17–20s) ─────────────────────────
                {
                    "clips": [
                        {
                            "asset": {
                                "type": "html",
                                "html": f"""
                                    <p style="
                                        font-family: Arial, sans-serif;
                                        font-size: 40px;
                                        color: #ffffff;
                                        text-align: center;
                                        background: rgba(255,140,0,0.85);
                                        padding: 16px 36px;
                                        border-radius: 10px;
                                    ">📞 {product.get('contact', 'Contact us to order!')}</p>
                                """,
                                "width": 900,
                                "height": 150,
                            },
                            "start": 17,
                            "length": 3,
                            "position": "bottomCenter",
                            "offset": {"y": -0.05},
                            "transition": {"in": "slideUp", "out": "fade"},
                        }
                    ]
                },
            ],
            # ── Background music ─────────────────────────────────────────────
            "soundtrack": {
                "src": "https://shotstack-assets.s3-ap-southeast-2.amazonaws.com/music/freepd/effects.mp3",
                "effect": "fadeInFadeOut",
                "volume": 0.4,
            },
        },
        "output": {
            "format": "mp4",
            "resolution": "sd",       # 1024x576 — free tier friendly
            "fps": 25,
            "size": {
                "width": 1080,
                "height": 1080,       # square for social media
            },
        },
    }
    return payload


def submit_render(payload):
    """Submit video render job to Shotstack."""
    resp = requests.post(SHOTSTACK_BASE, headers=HEADERS, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    render_id = data["response"]["id"]
    print(f"✅ Render submitted. ID: {render_id}")
    return render_id


def poll_render(render_id, max_wait=300):
    """Poll until render is done or timeout."""
    url = f"{SHOTSTACK_BASE}/{render_id}"
    elapsed = 0
    while elapsed < max_wait:
        time.sleep(15)
        elapsed += 15
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        status_data = resp.json()["response"]
        status = status_data["status"]
        print(f"  ⏳ [{elapsed}s] Status: {status}")

        if status == "done":
            video_url = status_data["url"]
            print(f"\n🎬 Video ready: {video_url}")
            return video_url
        elif status == "failed":
            raise RuntimeError(f"Render failed: {status_data}")

    raise TimeoutError("Render timed out after 5 minutes.")


def save_result(product, video_url, run_number):
    """Append result to a simple log file."""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "run": run_number,
        "product": product["name"],
        "video_url": video_url,
    }

    log_file = "video_log.json"
    log = []
    if os.path.exists(log_file):
        with open(log_file) as f:
            log = json.load(f)
    log.append(log_entry)
    with open(log_file, "w") as f:
        json.dump(log, f, indent=2)

    print(f"\n📝 Logged to {log_file}")
    print(json.dumps(log_entry, indent=2))


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    if not SHOTSTACK_API_KEY:
        raise EnvironmentError("SHOTSTACK_API_KEY secret is not set!")
    if not GITHUB_REPO_RAW:
        raise EnvironmentError("GITHUB_REPO_RAW secret is not set!")

    # Determine which run this is (1 = morning, 2 = evening)
    hour = datetime.utcnow().hour
    run_number = 1 if hour < 12 else 2
    print(f"\n🚀 Starting video generation — Run #{run_number} ({datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')})")

    product = load_products()
    print(f"📦 Selected product: {product['name']}")

    payload  = build_video_payload(product)
    render_id = submit_render(payload)
    video_url = poll_render(render_id)
    save_result(product, video_url, run_number)

    print("\n✅ Done! Share your video from the URL above.")


if __name__ == "__main__":
    main()
