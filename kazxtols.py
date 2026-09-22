#!/usr/bin/env python3
"""
KazXTols
Dev  : XioNiV ID
Lang : Python

Tools Checker ID & Public Info Lookup untuk berbagai platform.
Semua fitur hanya mengambil data PUBLIK (via API resmi atau halaman publik),
tidak ada scraping data privat/lokasi/aktivitas pribadi.
"""

import os
import sys

from modules.helper import console, print_banner, print_error, pause
from modules import whatsapp, telegram, roblox, social, youtube


def clear():
    os.system("cls" if os.name == "nt" else "clear")


MENU_CHECK_ID = [
    ("1", "Check ID Channel WhatsApp", whatsapp.check_channel),
    ("2", "Check ID Group WhatsApp", whatsapp.check_group),
    ("3", "Check ID Numbers WhatsApp", whatsapp.check_number),
    ("4", "Check ID Telegram", telegram.check_user_or_channel),
    ("5", "Check ID Group Telegram", telegram.check_group),
    ("6", "Check ID Roblox", roblox.check_id),
    ("7", "Check ID TikTok", social.check_tiktok),
    ("8", "Check ID Instagram", social.check_instagram),
    ("9", "Check ID Facebook", social.check_facebook),
    ("10", "Check ID Patreon", social.check_patreon),
    ("11", "Check ID X/Twitter", social.check_x),
    ("12", "Check ID YouTube", youtube.check_id),
]

MENU_STALKER = [
    ("13", "Stalker YouTube", youtube.stalk),
    ("14", "Stalker X/Twitter", social.stalk_x),
    ("15", "Stalker Patreon", social.stalk_patreon),
    ("16", "Stalker Facebook", social.stalk_facebook),
    ("17", "Stalker Instagram", social.stalk_instagram),
    ("18", "Stalker Roblox", roblox.stalk),
    ("19", "Stalker TikTok", social.stalk_tiktok),
    ("20", "Stalker Telegram", telegram.check_user_or_channel),
]

ALL_ITEMS = MENU_CHECK_ID + MENU_STALKER


def print_menu():
    print_banner()
    console.print("\n[bold underline]== CHECK ID ==[/bold underline]")
    for num, label, _ in MENU_CHECK_ID:
        console.print(f"  [cyan]{num:>2}[/cyan]. {label}")

    console.print("\n[bold underline]== STALKER (Data Publik) ==[/bold underline]")
    for num, label, _ in MENU_STALKER:
        console.print(f"  [cyan]{num:>2}[/cyan]. {label}")

    console.print("\n  [cyan] 0[/cyan]. Keluar")
    console.print()


def main():
    action_map = {num: func for num, _, func in ALL_ITEMS}

    while True:
        clear()
        print_menu()

        try:
            choice = console.input("[bold green]Pilih menu >[/bold green] ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Keluar dari KazXTols. Sampai jumpa![/yellow]")
            sys.exit(0)

        if choice == "0":
            console.print("[yellow]Terima kasih sudah pakai KazXTols![/yellow]")
            sys.exit(0)

        func = action_map.get(choice)
        if not func:
            print_error("Pilihan tidak ada di menu, coba lagi.")
            pause()
            continue

        clear()
        print_banner()
        console.print()
        try:
            func()
        except KeyboardInterrupt:
            console.print("\n[yellow]Dibatalkan.[/yellow]")
        except Exception as e:
            print_error(f"Terjadi kesalahan tak terduga: {e}")
        pause()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Keluar dari KazXTols.[/yellow]")
        sys.exit(0)
