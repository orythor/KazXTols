# KazXTols

Tools Checker ID & Public Info Lookup — dijalankan di Termux.

**Dev:** XioNiV ID
**Bahasa:** Python

---

## ⚠️ Catatan Penting

Semua fitur di tools ini **hanya mengambil data publik** yang memang bisa dilihat siapa saja (username availability, nama tampilan, bio, foto profil, follower/subscriber/member count publik, dll), lewat API resmi platform (Roblox, YouTube), halaman publik (Open Graph metadata), atau koneksi WhatsApp Web yang login sendiri (khusus Channel/Group WhatsApp — lihat bagian instalasi di bawah).

Tools ini **tidak**:
- Login ke akun siapapun selain milikmu sendiri (WhatsApp Web login khusus untuk fitur Channel/Group WhatsApp, pakai akunmu sendiri)
- Membaca chat pribadi atau mengirim pesan atas namamu
- Mengambil data privat, lokasi, atau riwayat aktivitas pengguna lain
- Melakukan bypass keamanan/privasi platform

Gunakan secara bertanggung jawab dan sesuai Terms of Service masing-masing platform.

---

## 📦 Instalasi (Termux)

```bash
pkg update && pkg upgrade -y
pkg install python git -y
git clone https://github.com/USERNAME_GITHUB_KAMU/KazXTols.git
cd KazXTols
pip install -r requirements.txt
python kazxtols.py
```

> Ganti `USERNAME_GITHUB_KAMU` dengan username GitHub tempat repo ini di-push.

### Instalasi Tambahan untuk Check ID Channel & Group WhatsApp

Dua fitur ini (nomor 1 & 2 di daftar bawah) butuh setup tambahan karena ID-nya berbentuk JID internal WhatsApp (`xxx@newsletter` / `xxx@g.us`), yang cuma bisa diambil lewat koneksi WhatsApp Web asli — bukan halaman publik biasa seperti fitur lain. Ini dijalankan lewat companion Node.js kecil bernama **wa-helper**.

```bash
pkg install nodejs -y
cd wa-helper
npm install
npm run login      # scan QR sekali pakai WhatsApp kamu
npm start          # biarkan tetap jalan di terminal ini
```

Lalu buka terminal Termux **kedua** (geser dari kiri layar > New Session) buat jalanin `python kazxtols.py` seperti biasa. Detail lengkap & troubleshooting ada di [`wa-helper/README.md`](wa-helper/README.md).

> Fitur lain (Number WhatsApp, Telegram, Roblox, TikTok, dst) **tidak butuh** wa-helper — langsung jalan begitu `pip install -r requirements.txt` selesai.

---

## ✨ Fitur

### Check ID
| # | Fitur | Butuh wa-helper? |
|---|-------|:---:|
| 1 | Check ID Channel WhatsApp | ✅ |
| 2 | Check ID Group WhatsApp | ✅ |
| 3 | Check ID Numbers WhatsApp | ❌ |
| 4 | Check ID Telegram | ❌ |
| 5 | Check ID Group Telegram | ❌ |
| 6 | Check ID Roblox | ❌ |
| 7 | Check ID TikTok | ❌ |
| 8 | Check ID Instagram | ❌ |
| 9 | Check ID Facebook | ❌ |
| 10 | Check ID Patreon | ❌ |
| 11 | Check ID X/Twitter | ❌ |
| 12 | Check ID YouTube | ❌ |

### Stalker (Data Publik)
| # | Fitur |
|---|-------|
| 13 | Stalker YouTube |
| 14 | Stalker X/Twitter |
| 15 | Stalker Patreon |
| 16 | Stalker Facebook |
| 17 | Stalker Instagram |
| 18 | Stalker Roblox |
| 19 | Stalker TikTok |
| 20 | Stalker Telegram |

> **Free Fire & Mobile Legends stalker tidak disertakan** — kedua game ini tidak punya API publik resmi dari Garena/Moonton untuk player lookup. API pihak ketiga yang beredar untuk ini bersifat tidak resmi dan berisiko melanggar ToS game.

---

## 🗂️ Struktur Project

```
KazXTols/
├── kazxtols.py          # Entry point / menu utama
├── requirements.txt
├── README.md
├── modules/
│   ├── helper.py         # Shared UI & HTTP helper
│   ├── whatsapp.py        # Channel & Group (via wa-helper), Number (publik)
│   ├── telegram.py        # User/Channel, Group
│   ├── roblox.py           # Check ID + Stalker (API resmi Roblox)
│   ├── social.py           # TikTok, Instagram, Facebook, Patreon, X (Check ID + Stalker)
│   └── youtube.py          # Check ID (oEmbed resmi) + Stalker
└── wa-helper/             # Companion Node.js (Baileys) - lihat wa-helper/README.md
    ├── server.js
    ├── login.js
    └── package.json
```

Struktur modular — tiap platform punya file sendiri di `modules/`, jadi gampang nambah fitur atau platform baru tanpa bongkar kode lain.

---

## 🔧 Menambah Platform Baru

1. Buat file baru di `modules/`, contoh `modules/threads.py`
2. Import helper: `from modules.helper import safe_get, print_result, ...`
3. Tambahkan entry baru di `kazxtols.py` pada `MENU_CHECK_ID` atau `MENU_STALKER`

---

## 📄 Lisensi

Bebas dipakai & dimodifikasi untuk kebutuhan pribadi. Mohon cantumkan credit ke **XioNiV ID** jika di-redistribute.
