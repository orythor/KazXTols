"""
KazXTols - Social module (generik)
Dipakai untuk platform yang halaman profilnya expose Open Graph meta tag
secara publik: TikTok, Instagram, Facebook, Patreon, X/Twitter.

Pendekatan: fetch halaman profil publik -> parse og:title / og:description / og:image.
Tidak ada login, tidak ada API key, tidak ada akses ke data privat.
"""

import re
from modules.helper import safe_get, print_result, print_error, print_loading, ask_input


def _extract_og(html: str, prop: str):
    pattern = rf'<meta[^>]+property=["\']og:{prop}["\'][^>]+content=["\']([^"\']*)["\']'
    m = re.search(pattern, html, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    pattern2 = rf'<meta[^>]+content=["\']([^"\']*)["\'][^>]+property=["\']og:{prop}["\']'
    m2 = re.search(pattern2, html, re.IGNORECASE)
    return m2.group(1).strip() if m2 else None


def _extract_title_tag(html: str):
    m = re.search(r"<title>([^<]*)</title>", html, re.IGNORECASE)
    return m.group(1).strip() if m else None


def _clean_username(raw: str, domain_markers: list) -> str:
    val = raw.strip()
    for marker in domain_markers:
        if marker in val:
            val = val.split(marker)[-1]
    val = val.split("?")[0].strip("/")
    return val.lstrip("@")


PLATFORM_CONFIG = {
    "tiktok": {
        "label": "TikTok",
        "url_tmpl": "https://www.tiktok.com/@{u}",
        "markers": ["tiktok.com/@", "tiktok.com/"],
        "not_found_markers": ["couldn't find this account", "page not available"],
    },
    "instagram": {
        "label": "Instagram",
        "url_tmpl": "https://www.instagram.com/{u}/",
        "markers": ["instagram.com/"],
        "not_found_markers": ["page isn't available", "page not found", "sorry, this page"],
    },
    "facebook": {
        "label": "Facebook",
        "url_tmpl": "https://www.facebook.com/{u}",
        "markers": ["facebook.com/"],
        "not_found_markers": ["content isn't available", "page not found", "this content isn't available right now"],
    },
    "patreon": {
        "label": "Patreon",
        "url_tmpl": "https://www.patreon.com/{u}",
        "markers": ["patreon.com/"],
        "not_found_markers": ["page not found", "404"],
    },
    "x": {
        "label": "X (Twitter)",
        "url_tmpl": "https://x.com/{u}",
        "markers": ["x.com/", "twitter.com/"],
        "not_found_markers": ["page doesn't exist", "this account doesn't exist"],
    },
}


def _check_generic(platform_key: str):
    cfg = PLATFORM_CONFIG[platform_key]
    raw = ask_input(f"Masukkan Username {cfg['label']} (tanpa @):")
    if not raw:
        return

    username = _clean_username(raw, cfg["markers"])
    url = cfg["url_tmpl"].format(u=username)

    print_loading(f"Mengecek {cfg['label']}")
    resp, err = safe_get(url)
    if err:
        print_error(err)
        return

    html = resp.text
    title = _extract_og(html, "title") or _extract_title_tag(html)
    desc = _extract_og(html, "description")
    image = _extract_og(html, "image")

    lower_html_snippet = (title or "") + " " + (desc or "")
    is_not_found = resp.status_code == 404 or any(
        m in lower_html_snippet.lower() for m in cfg["not_found_markers"]
    )
    if title is None:
        is_not_found = True

    if is_not_found:
        print_result(cfg["label"], {"Username": username, "URL": url}, found=False)
        return

    print_result(cfg["label"], {
        "Username": username,
        "Nama/Judul": title,
        "Bio/Deskripsi": desc,
        "Foto Profil": image,
        "URL": url,
    }, found=True)


def check_tiktok():
    _check_generic("tiktok")


def check_instagram():
    _check_generic("instagram")


def check_facebook():
    _check_generic("facebook")


def check_patreon():
    _check_generic("patreon")


def check_x():
    _check_generic("x")


# ---------------------------------------------------------------------------
# STALKER (profile viewer publik) - data publik saja: nama, bio, follower (jika ada di og:description)
# ---------------------------------------------------------------------------

def _stalk_generic(platform_key: str):
    cfg = PLATFORM_CONFIG[platform_key]
    raw = ask_input(f"Masukkan Username {cfg['label']} yang mau dilihat (data publik):")
    if not raw:
        return

    username = _clean_username(raw, cfg["markers"])
    url = cfg["url_tmpl"].format(u=username)

    print_loading(f"Mengambil data publik {cfg['label']}")
    resp, err = safe_get(url)
    if err:
        print_error(err)
        return

    html = resp.text
    title = _extract_og(html, "title") or _extract_title_tag(html)
    desc = _extract_og(html, "description")
    image = _extract_og(html, "image")

    lower_html_snippet = (title or "") + " " + (desc or "")
    is_not_found = resp.status_code == 404 or any(
        m in lower_html_snippet.lower() for m in cfg["not_found_markers"]
    )
    if title is None:
        is_not_found = True

    if is_not_found:
        print_result(f"Stalker {cfg['label']}", {"Username": username, "URL": url}, found=False)
        return

    # og:description sering berisi ringkasan "X Followers, Y Following, Z Posts - bio..."
    print_result(f"Stalker {cfg['label']} (Data Publik)", {
        "Username": username,
        "Nama": title,
        "Info Publik (followers/bio jika tersedia)": desc,
        "Foto Profil": image,
        "URL": url,
        "Catatan": "Hanya data publik yang tampil di halaman profil, tanpa akses privat.",
    }, found=True)


def stalk_tiktok():
    _stalk_generic("tiktok")


def stalk_instagram():
    _stalk_generic("instagram")


def stalk_facebook():
    _stalk_generic("facebook")


def stalk_patreon():
    _stalk_generic("patreon")


def stalk_x():
    _stalk_generic("x")
