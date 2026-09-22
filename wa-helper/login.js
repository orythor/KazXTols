/**
 * KazXTols - wa-helper - login.js
 * Dev: XioNiV ID
 *
 * Jalankan file ini SEKALI SAJA di awal buat login ke WhatsApp (scan QR).
 * Setelah berhasil, session tersimpan di ./auth_info dan kamu bisa langsung
 * pakai `npm start` (server.js) tanpa perlu scan ulang.
 *
 * Kalau ./auth_info sudah ada dan masih valid, script ini bakal langsung
 * bilang "sudah login" tanpa nunjukin QR lagi.
 */

const path = require("path");
const fs = require("fs");
const qrcodeTerminal = require("qrcode-terminal");
const pino = require("pino");

const {
  default: makeWASocket,
  useMultiFileAuthState,
  fetchLatestBaileysVersion,
} = require("baileys");

const AUTH_DIR = path.join(__dirname, "auth_info");
const logger = pino({ level: "silent" });

async function login() {
  if (!fs.existsSync(AUTH_DIR)) {
    fs.mkdirSync(AUTH_DIR, { recursive: true });
  }

  const { state, saveCreds } = await useMultiFileAuthState(AUTH_DIR);
  const { version } = await fetchLatestBaileysVersion();

  console.log("Menghubungkan ke WhatsApp...\n");

  const sock = makeWASocket({
    version,
    auth: state,
    logger,
    browser: ["KazXTols", "Chrome", "1.0.0"],
  });

  sock.ev.on("creds.update", saveCreds);

  sock.ev.on("connection.update", (update) => {
    const { connection, qr, lastDisconnect } = update;

    if (qr) {
      console.log("=== Scan QR ini pakai WhatsApp kamu ===");
      console.log("(WhatsApp di HP > Perangkat Tertaut > Tautkan Perangkat)\n");
      qrcodeTerminal.generate(qr, { small: true });
    }

    if (connection === "open") {
      console.log("\n✓ Login berhasil! Session tersimpan di ./auth_info");
      console.log("✓ Sekarang jalankan: npm start");
      console.log("  (server akan otomatis pakai session ini, tanpa scan ulang)\n");
      setTimeout(() => process.exit(0), 1500);
    }

    if (connection === "close") {
      const statusCode = lastDisconnect?.error?.output?.statusCode;
      if (statusCode === 401) {
        console.log("\n✗ Login gagal / ditolak. Hapus folder auth_info lalu coba lagi.");
        process.exit(1);
      }
    }
  });
}

login().catch((err) => {
  console.error("Error saat login:", err.message || err);
  process.exit(1);
});
