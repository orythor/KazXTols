"""
KazXTols - WhatsApp module
- Check ID Number: lewat halaman publik wa.me (Open Graph meta), tanpa login.
- Check ID Channel & Group: JID WhatsApp (xxx@newsletter / xxx@g.us) cuma bisa
  di-resolve lewat koneksi WhatsApp Web yang sudah login (protokol binary,
  bukan HTTP biasa). Makanya dua fitur ini manggil ke wa-helper (companion
  Node.js + Baileys yang jalan lokal di komputer/HP yang sama) lewat HTTP
  ke localhost. Lihat wa-helper/README.md buat cara setup & login sekali.
"""

import re
from modules.helper import safe_get, print_result, print_error, print_info, print_loading, ask_input

WA_HELPER_BASE = "http://127.0.0.1:8765"


def _wa_helper_get(path: str, params: dict):
    """
    Panggil endpoint wa-helper. Return (data_dict_or_None, error_message_or_None).
    error_message sudah dalam bahasa manusia, siap ditampilkan ke user.
    """
    resp, err = safe_get(f"{WA_HELPER_BASE}{path}", params=params, timeout=20)

    if err:
        return None, (
            "Tidak bisa konek ke wa-helper (localhost:8765).\n"
            "  Pastikan wa-helper sudah jalan: buka terminal baru, masuk folder wa-helper/, jalankan 'npm start'.\n"
            "  Kalau belum pernah login, jalankan dulu 'npm run login' di folder wa-helper/ dan scan QR-nya."
        )

    try:
        body = resp.json()
    except ValueError:
        return None, "wa-helper mengembalikan respons tidak valid. Coba restart wa-helper."

    if resp.status_code == 503:
        return None, (
            "wa-helper jalan tapi belum terhubung ke WhatsApp.\n"
            "  Cek terminal wa-helper, mungkin masih proses reconnect atau butuh login ulang."
        )

    if resp.status_code == 404:
        return {"__not_found__": True}, None

    if resp.status_code >= 400:
        return None, body.get("message", "Terjadi kesalahan di wa-helper.")

    return body.get("data"), None


def _parse_jid_or_code(raw: str, suffix: str):
    """
    Terima input dalam berbagai bentuk dan balikin (jid_or_none, invite_code_or_none).
    suffix: '@newsletter' atau '@g.us'
    """
    val = raw.strip()

    if suffix in val:
        return val, None

    if "whatsapp.com/channel/" in val:
        code = val.split("channel/")[-1].split("?")[0].strip("/")
        return None, code

    if "chat.whatsapp.com/" in val:
        code = val.split("chat.whatsapp.com/")[-1].split("?")[0].strip("/")
        return None, code

    # Angka polos tanpa @suffix -> asumsikan itu JID, tinggal tambahkan suffix
    if re.fullmatch(r"[\d\-]+", val):
        return f"{val}{suffix}", None

    # String lain (bukan angka, bukan link) -> anggap invite code
    return None, val


def check_channel():
    print_info("Masukkan JID (contoh: 120363423053078572@newsletter) atau link whatsapp.com/channel/xxx")
    raw = ask_input("ID/Link Channel WhatsApp:")
    if not raw:
        return

    jid, invite = _parse_jid_or_code(raw, "@newsletter")

    print_loading("Mengecek channel via wa-helper")
    params = {"jid": jid} if jid else {"invite": invite}
    data, err = _wa_helper_get("/newsletter", params)

    if err:
        print_error(err)
        return

    if not data or data.get("__not_found__"):
        print_result("WhatsApp Channel", {"Input": raw}, found=False)
        return

    print_result("WhatsApp Channel", {
        "JID": data.get("id"),
        "Nama": data.get("name"),
        "Deskripsi": data.get("description"),
        "Subscriber": data.get("subscribers"),
        "Verified": data.get("verified"),
        "Dibuat": data.get("createdAt"),
        "Invite Link": f"https://whatsapp.com/channel/{data.get('invite')}" if data.get("invite") else None,
    }, found=True)


def check_group():
    print_info("Masukkan JID (contoh: 120363012345678901@g.us) atau link chat.whatsapp.com/xxx")
    print_info("Catatan: Group hanya bisa dicek kalau akun WhatsApp yang login di wa-helper sudah join grup tsb.")
    raw = ask_input("ID/Link Group WhatsApp:")
    if not raw:
        return

    jid, invite = _parse_jid_or_code(raw, "@g.us")

    if not jid:
        print_error(
            "Group WhatsApp cuma bisa dicek pakai JID lengkap (xxx@g.us), bukan invite link/code.\n"
            "  Ini keterbatasan dari WhatsApp sendiri: metadata grup hanya ter-sync ke akun yang sudah join,\n"
            "  jadi resolve dari invite code tanpa join dulu tidak didukung."
        )
        return

    print_loading("Mengecek group via wa-helper")
    data, err = _wa_helper_get("/group", {"jid": jid})

    if err:
        print_error(err)
        return

    if not data or data.get("__not_found__"):
        print_result("WhatsApp Group", {
            "JID": jid,
        }, found=False)
        print_info("Kemungkinan: JID salah, atau akun yang login di wa-helper belum join grup ini.")
        return

    print_result("WhatsApp Group", {
        "JID": data.get("id"),
        "Nama Grup": data.get("subject"),
        "Deskripsi": data.get("description"),
        "Jumlah Member": data.get("size"),
        "Dibuat": data.get("creation"),
        "Hanya Admin Kirim Pesan": data.get("announce"),
    }, found=True)


def check_number():
    raw = ask_input("Masukkan Nomor WhatsApp (format internasional, contoh: 6281234567890):")
    if not raw:
        return

    number = re.sub(r"[^\d]", "", raw)
    if not number:
        print_error("Nomor tidak valid.")
        return

    url = f"https://wa.me/{number}"
    print_loading("Mengecek nomor")

    resp, err = safe_get(url)
    if err:
        print_error(err)
        return

    html = resp.text
    title = _extract_og(html, "title")
    desc = _extract_og(html, "description")
    image = _extract_og(html, "image")

    # wa.me untuk nomor personal biasanya cuma redirect ke halaman "Continue to Chat"
    # tanpa nama/foto. Business account publik akan punya og:title = nama bisnis.
    has_business_profile = bool(title) and title.strip().lower() not in ["whatsapp", ""]

    print_result("WhatsApp Number", {
        "Nomor": number,
        "Terdaftar (terindikasi)": "Ya" if resp.status_code == 200 else "Tidak diketahui",
        "Nama Bisnis (jika publik)": title if has_business_profile else "-",
        "Deskripsi": desc if has_business_profile else "-",
        "Foto Profil": image if has_business_profile else "-",
        "URL": url,
        "Catatan": "Akun personal dengan privasi terkunci tidak akan menampilkan info di sini, itu bukan berarti nomor tidak terdaftar.",
    }, found=True)


def _extract_og(html: str, prop: str):
    """Ambil isi meta og:xxx dari raw HTML. Dipakai oleh check_number()."""
    pattern = rf'<meta[^>]+property=["\']og:{prop}["\'][^>]+content=["\']([^"\']*)["\']'
    m = re.search(pattern, html, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    pattern2 = rf'<meta[^>]+content=["\']([^"\']*)["\'][^>]+property=["\']og:{prop}["\']'
    m2 = re.search(pattern2, html, re.IGNORECASE)
    return m2.group(1).strip() if m2 else None
