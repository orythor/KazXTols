"""
KazXTols - YouTube module
Check ID Channel via YouTube oEmbed API resmi (tanpa API key).
Stalker: ambil data publik tambahan (subscriber count dll) dari halaman channel publik.
"""

import re
import json
from modules.helper import safe_get, print_result, print_error, print_loading, ask_input


def _clean_channel_input(raw: str) -> str:
    val = raw.strip()
    for marker in ["youtube.com/@", "youtube.com/channel/", "youtube.com/c/", "youtube.com/user/", "youtube.com/"]:
        if marker in val:
            val = val.split(marker)[-1]
    return val.split("?")[0].strip("/")


def check_id():
    raw = ask_input("Masukkan Username/Handle YouTube (contoh: @MrBeast atau nama channel):")
    if not raw:
        return

    handle = _clean_channel_input(raw)
    if not handle.startswith("@") and not handle.isdigit():
        handle_url = f"@{handle}"
    else:
        handle_url = handle

    channel_url = f"https://www.youtube.com/{handle_url}"
    oembed_url = "https://www.youtube.com/oembed"

    print_loading("Mengecek channel")
    resp, err = safe_get(oembed_url, params={"url": channel_url, "format": "json"})
    if err:
        print_error(err)
        return

    if resp.status_code != 200:
        print_result("YouTube Channel", {"Handle": handle, "URL": channel_url}, found=False)
        return

    try:
        data = resp.json()
    except ValueError:
        print_result("YouTube Channel", {"Handle": handle, "URL": channel_url}, found=False)
        return

    print_result("YouTube Channel", {
        "Handle": handle,
        "Nama Channel": data.get("author_name"),
        "URL Channel": data.get("author_url"),
        "Thumbnail": data.get("thumbnail_url"),
        "URL": channel_url,
    }, found=True)


def stalk():
    raw = ask_input("Masukkan Username/Handle YouTube yang mau dilihat datanya:")
    if not raw:
        return

    handle = _clean_channel_input(raw)
    handle_url = f"@{handle}" if not handle.startswith("@") else handle
    channel_url = f"https://www.youtube.com/{handle_url}/about"

    print_loading("Mengambil data publik channel")
    resp, err = safe_get(channel_url)
    if err:
        print_error(err)
        return

    if resp.status_code != 200:
        print_result("Stalker YouTube", {"Handle": handle, "URL": channel_url}, found=False)
        return

    html = resp.text

    # YouTube nyimpen data awal di window["ytInitialData"], kita coba tarik subscriber count & deskripsi
    subs_match = re.search(r'"subscriberCountText":\{"simpleText":"([^"]+)"', html)
    subs = subs_match.group(1) if subs_match else None
    if not subs:
        subs_match2 = re.search(r'"subscriberCountText":\{"accessibility".*?"simpleText":"([^"]+)"', html)
        subs = subs_match2.group(1) if subs_match2 else None

    desc_match = re.search(r'"description":\{"simpleText":"([^"]*)"', html)
    desc = desc_match.group(1) if desc_match else None

    og_title_match = re.search(r'<meta property="og:title" content="([^"]*)"', html)
    title = og_title_match.group(1) if og_title_match else handle

    og_image_match = re.search(r'<meta property="og:image" content="([^"]*)"', html)
    image = og_image_match.group(1) if og_image_match else None

    print_result("Stalker YouTube (Data Publik)", {
        "Handle": handle,
        "Nama Channel": title,
        "Subscriber (perkiraan publik)": subs or "Tersembunyi/Tidak tampil publik",
        "Deskripsi": desc,
        "Foto Channel": image,
        "URL": f"https://www.youtube.com/{handle_url}",
        "Catatan": "Data statistik detail mengikuti apa yang channel tampilkan secara publik.",
    }, found=True)
