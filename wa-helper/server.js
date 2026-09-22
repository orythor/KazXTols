/**
 * KazXTols - wa-helper
 * Dev: XioNiV ID
 *
 * Companion Node.js buat KazXTols (Python). Login sekali via QR, session
 * tersimpan di ./auth_info, lalu expose local HTTP server supaya Python
 * bisa resolve metadata Channel (@newsletter) & Group (@g.us) WhatsApp -
 * dua hal yang cuma bisa diambil lewat koneksi WhatsApp Web yang sudah
 * login, bukan lewat halaman publik biasa.
 *
 * Endpoint:
 *   GET /status                        -> {connected: bool}
 *   GET /newsletter?jid=xxx@newsletter  -> metadata channel
 *   GET /newsletter?invite=xxxxx        -> metadata channel via invite code
 *   GET /group?jid=xxx@g.us             -> metadata group (harus sudah join)
 *
 * Semua endpoint hanya MEMBACA metadata publik (nama, deskripsi, jumlah
 * member/follower, foto). Tidak mengirim pesan, tidak membaca chat pribadi.
 */

const http = require("http");
const { URL } = require("url");
const path = require("path");
const fs = require("fs");
const qrcodeTerminal = require("qrcode-terminal");
const pino = require("pino");

const {
  default: makeWASocket,
  useMultiFileAuthState,
  DisconnectReason,
  fetchLatestBaileysVersion,
} = require("baileys");

const PORT = process.env.WA_HELPER_PORT || 8765;
const AUTH_DIR = path.join(__dirname, "auth_info");

let sock = null;
let isConnected = false;
let isStarting = false;

const logger = pino({ level: "silent" });

// ---------------------------------------------------------------------------
// Koneksi Baileys
// ---------------------------------------------------------------------------

async function startSock() {
  if (isStarting) return;
  isStarting = true;

  if (!fs.existsSync(AUTH_DIR)) {
    fs.mkdirSync(AUTH_DIR, { recursive: true });
  }

  const { state, saveCreds } = await useMultiFileAuthState(AUTH_DIR);
  const { version } = await fetchLatestBaileysVersion();

  sock = makeWASocket({
    version,
    auth: state,
    logger,
    browser: ["KazXTols", "Chrome", "1.0.0"],
    syncFullHistory: false,
    markOnlineOnConnect: false,
  });

  sock.ev.on("creds.update", saveCreds);

  sock.ev.on("connection.update", (update) => {
    const { connection, lastDisconnect, qr } = update;

    if (qr) {
      console.log("\n=== Scan QR ini pakai WhatsApp kamu (Perangkat Tertaut) ===\n");
      qrcodeTerminal.generate(qr, { small: true });
      console.log("\nQR berlaku sebentar, kalau expired tunggu QR baru muncul otomatis.\n");
    }

    if (connection === "open") {
      isConnected = true;
      isStarting = false;
      console.log("[wa-helper] Terhubung ke WhatsApp. Server siap dipakai KazXTols.");
    }

    if (connection === "close") {
      isConnected = false;
      isStarting = false;
      const statusCode = lastDisconnect?.error?.output?.statusCode;
      const shouldReconnect = statusCode !== DisconnectReason.loggedOut;

      console.log(`[wa-helper] Koneksi tertutup (code: ${statusCode}).`);

      if (shouldReconnect) {
        console.log("[wa-helper] Mencoba reconnect...");
        setTimeout(startSock, 3000);
      } else {
        console.log("[wa-helper] Logged out. Hapus folder auth_info lalu jalankan ulang untuk login baru.");
      }
    }
  });
}

// ---------------------------------------------------------------------------
// HTTP server - dipanggil oleh Python
// ---------------------------------------------------------------------------

function sendJSON(res, statusCode, payload) {
  res.writeHead(statusCode, { "Content-Type": "application/json" });
  res.end(JSON.stringify(payload));
}

function normalizeNewsletterMetadata(meta) {
  if (!meta) return null;
  // sock.newsletterMetadata() balikin objek yang SUDAH di-flatten oleh Baileys
  // (lihat interface NewsletterMetadata): meta.name, meta.description, dst
  // langsung string, bukan nested di thread_metadata. picture sendiri
  // berbentuk object { directPath, id, ... } kalau ada.
  return {
    id: meta.id || null,
    name: meta.name || null,
    description: meta.description || null,
    subscribers: meta.subscribers ?? null,
    verified: meta.thread_metadata?.verification || null,
    picture: meta.picture?.directPath || null,
    invite: meta.invite || null,
    createdAt: meta.creation_time ?? null,
  };
}

function normalizeGroupMetadata(meta) {
  if (!meta) return null;
  return {
    id: meta.id,
    subject: meta.subject || null,
    description: meta.desc || null,
    owner: meta.owner || null,
    size: meta.size ?? (meta.participants ? meta.participants.length : null),
    creation: meta.creation ?? null,
    announce: meta.announce ?? null,
    restrict: meta.restrict ?? null,
  };
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://localhost:${PORT}`);

  if (url.pathname === "/status") {
    return sendJSON(res, 200, { connected: isConnected });
  }

  if (!isConnected) {
    return sendJSON(res, 503, {
      error: "not_connected",
      message: "Belum terhubung ke WhatsApp. Cek terminal wa-helper, mungkin perlu scan QR atau masih reconnect.",
    });
  }

  try {
    if (url.pathname === "/newsletter") {
      const jid = url.searchParams.get("jid");
      const invite = url.searchParams.get("invite");

      if (!jid && !invite) {
        return sendJSON(res, 400, { error: "missing_param", message: "Butuh parameter 'jid' atau 'invite'." });
      }

      let meta;
      if (jid) {
        meta = await sock.newsletterMetadata("jid", jid);
      } else {
        meta = await sock.newsletterMetadata("invite", invite);
      }

      const normalized = normalizeNewsletterMetadata(meta);
      if (!normalized || !normalized.id) {
        return sendJSON(res, 404, { error: "not_found", message: "Channel tidak ditemukan." });
      }
      return sendJSON(res, 200, { found: true, data: normalized });
    }

    if (url.pathname === "/group") {
      const jid = url.searchParams.get("jid");
      if (!jid) {
        return sendJSON(res, 400, { error: "missing_param", message: "Butuh parameter 'jid'." });
      }

      const meta = await sock.groupMetadata(jid);
      const normalized = normalizeGroupMetadata(meta);
      if (!normalized || !normalized.id) {
        return sendJSON(res, 404, { error: "not_found", message: "Group tidak ditemukan." });
      }
      return sendJSON(res, 200, { found: true, data: normalized });
    }

    return sendJSON(res, 404, { error: "unknown_endpoint" });
  } catch (err) {
    const message = err?.message || String(err);

    // Baileys biasanya nge-throw kalau JID invalid / channel-nya sudah tidak ada / group belum di-join.
    const notFoundHints = ["item-not-found", "not-authorized", "404", "not found"];
    const isNotFound = notFoundHints.some((h) => message.toLowerCase().includes(h));

    if (isNotFound) {
      return sendJSON(res, 404, { found: false, error: "not_found", message: "ID tidak ditemukan atau tidak bisa diakses." });
    }

    console.error("[wa-helper] Error:", message);
    return sendJSON(res, 500, { error: "internal_error", message });
  }
});

server.listen(PORT, "127.0.0.1", () => {
  console.log(`[wa-helper] HTTP server jalan di http://127.0.0.1:${PORT}`);
  console.log("[wa-helper] Menghubungkan ke WhatsApp...\n");
  startSock();
});

process.on("SIGINT", () => {
  console.log("\n[wa-helper] Dimatikan.");
  process.exit(0);
});
