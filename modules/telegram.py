"""
KazXTols - Telegram module
Check ID user/bot/channel dan grup Telegram lewat t.me public preview page.
"""

import re
from modules.helper import safe_get, print_result, print_error, print_loading, ask_input


def _extract_og(html: str, prop: str):
    pattern = rf'<meta[^>]+property=["\']og:{prop}["\'][^>]+content=["\']([^"\']*)["\']'
    m = re.search(pattern, html, re.IGNORECASE)
    return m.group(1).strip() if m else None


def _extract_member_count(html: str):
    # t.me preview biasanya nampilin "X members" atau "X subscribers" di <div class="tgme_page_extra">
    m = re.search(r'class="tgme_page_extra">([^<]+)<', html)
    return m.group(1).strip() if m else None


def check_user_or_channel():
    raw = ask_input("Masukkan Username Telegram (tanpa @, contoh: durov):")
    if not raw:
        return

    username = raw.strip().lstrip("@")
    if "t.me/" in username:
        username = username.split("t.me/")[-1].split("?")[0].strip("/")

    url = f"https://t.me/{username}"
    print_loading("Mengecek username")

    resp, err = safe_get(url)
    if err:
        print_error(err)
        return

    html = resp.text
    title = _extract_og(html, "title")
    desc = _extract_og(html, "description")
    image = _extract_og(html, "image")
    extra = _extract_member_count(html)

    # Kalau username tidak ada, t.me tetap return 200 tapi halaman kosong tanpa tgme_page_title
    has_page = 'tgme_page_title' in html or title is not None

    if not has_page:
        print_result("Telegram User/Channel", {"Username": username, "URL": url}, found=False)
        return

    kind = "Bot" if username.lower().endswith("bot") else "User/Channel/Group"

    print_result("Telegram User/Channel", {
        "Username": f"@{username}",
        "Tipe (terindikasi)": kind,
        "Nama": title,
        "Bio/Deskripsi": desc,
        "Info Tambahan": extra,
        "Foto": image,
        "URL": url,
    }, found=True)


def check_group():
    raw = ask_input("Masukkan Link/Kode Invite Grup Telegram (contoh: t.me/+xxxxx atau t.me/joinchat/xxxxx):")
    if not raw:
        return

    code = raw.strip()
    code = code.replace("https://t.me/", "").replace("t.me/", "")
    code = code.replace("joinchat/", "")

    if code.startswith("+"):
        url = f"https://t.me/+{code[1:]}"
    else:
        url = f"https://t.me/joinchat/{code}"

    print_loading("Mengecek grup")

    resp, err = safe_get(url)
    if err:
        print_error(err)
        return

    html = resp.text
    title = _extract_og(html, "title")
    desc = _extract_og(html, "description")
    image = _extract_og(html, "image")
    extra = _extract_member_count(html)

    has_page = 'tgme_page_title' in html or (title is not None and "telegram" not in title.lower())

    if not has_page:
        print_result("Telegram Group", {"Kode": code, "URL": url}, found=False)
        return

    print_result("Telegram Group", {
        "Kode Invite": code,
        "Nama Grup": title,
        "Deskripsi": desc,
        "Jumlah Member (jika tampil)": extra,
        "Foto": image,
        "URL": url,
    }, found=True)
