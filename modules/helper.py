import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.box import ROUNDED

console = Console()

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

TIMEOUT = 15


def get_session() -> requests.Session:
    """Session requests dengan header default, dipakai semua module."""
    s = requests.Session()
    s.headers.update(DEFAULT_HEADERS)
    return s


def safe_get(url, session=None, headers=None, params=None, timeout=TIMEOUT, allow_redirects=True):
    """
    Wrapper requests.get yang aman dari exception jaringan.
    Return: (response_or_none, error_message_or_none)
    """
    sess = session or get_session()
    try:
        h = dict(sess.headers)
        if headers:
            h.update(headers)
        resp = sess.get(url, headers=h, params=params, timeout=timeout, allow_redirects=allow_redirects)
        return resp, None
    except requests.exceptions.Timeout:
        return None, "Timeout - server tidak merespon"
    except requests.exceptions.ConnectionError:
        return None, "Gagal konek - cek koneksi internet kamu"
    except requests.exceptions.RequestException as e:
        return None, f"Request error: {e}"


def safe_post(url, session=None, headers=None, json_data=None, data=None, timeout=TIMEOUT):
    """Sama seperti safe_get, tapi untuk POST."""
    sess = session or get_session()
    try:
        h = dict(sess.headers)
        if headers:
            h.update(headers)
        resp = sess.post(url, headers=h, json=json_data, data=data, timeout=timeout)
        return resp, None
    except requests.exceptions.Timeout:
        return None, "Timeout - server tidak merespon"
    except requests.exceptions.ConnectionError:
        return None, "Gagal konek - cek koneksi internet kamu"
    except requests.exceptions.RequestException as e:
        return None, f"Request error: {e}"


def print_banner():
    console.print(Panel.fit(
        "[bold cyan]KazXTols[/bold cyan]\n"
        "[dim]Tools Checker & Public Info Lookup[/dim]\n"
        "[yellow]Dev :[/yellow] XioNiV ID",
        border_style="cyan",
        box=ROUNDED,
    ))


def print_result(title: str, data: dict, found: bool = True):
    """
    Print hasil lookup dalam bentuk tabel rapi.
    data: dict key-value yang mau ditampilkan.
    found: True kalau ID/username ditemukan, False kalau tidak.
    """
    color = "green" if found else "red"
    status = "DITEMUKAN" if found else "TIDAK DITEMUKAN"

    table = Table(show_header=False, box=ROUNDED, border_style=color, title=title, title_style=f"bold {color}")
    table.add_column("Key", style="bold white", no_wrap=True)
    table.add_column("Value", style="white")

    table.add_row("Status", f"[bold {color}]{status}[/bold {color}]")
    for k, v in data.items():
        if v is None or v == "":
            v = "-"
        table.add_row(str(k), str(v))

    console.print(table)


def print_error(message: str):
    console.print(f"[bold red]✗ Error:[/bold red] {message}")


def print_info(message: str):
    console.print(f"[cyan]ℹ {message}[/cyan]")


def print_loading(message: str):
    console.print(f"[dim]⏳ {message}...[/dim]")


def ask_input(prompt: str) -> str:
    try:
        val = console.input(f"[bold cyan]{prompt}[/bold cyan] ").strip()
        return val
    except (KeyboardInterrupt, EOFError):
        console.print("\n[yellow]Dibatalkan.[/yellow]")
        return ""


def pause():
    try:
        console.input("\n[dim]Tekan ENTER untuk kembali ke menu...[/dim]")
    except (KeyboardInterrupt, EOFError):
        pass
