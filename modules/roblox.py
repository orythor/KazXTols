"""
KazXTols - Roblox module
Check ID/username Roblox pakai API publik resmi Roblox (users.roblox.com).
"""

from modules.helper import safe_get, safe_post, print_result, print_error, print_loading, ask_input


def check_id():
    raw = ask_input("Masukkan Username Roblox:")
    if not raw:
        return

    username = raw.strip()
    print_loading("Mengecek username")

    lookup_url = "https://users.roblox.com/v1/usernames/users"
    payload = {"usernames": [username], "excludeBannedUsers": False}

    resp, err = safe_post(lookup_url, json_data=payload)
    if err:
        print_error(err)
        return

    if resp.status_code != 200:
        print_error(f"API Roblox merespon status {resp.status_code}, coba lagi nanti.")
        return

    data = resp.json()
    results = data.get("data", [])

    if not results:
        print_result("Roblox", {"Username": username}, found=False)
        return

    user = results[0]
    user_id = user.get("id")
    display_name = user.get("displayName")

    # Ambil detail tambahan (deskripsi, created date, banned status)
    detail = {}
    if user_id:
        detail_resp, derr = safe_get(f"https://users.roblox.com/v1/users/{user_id}")
        if not derr and detail_resp.status_code == 200:
            detail = detail_resp.json()

    # Ambil headshot thumbnail
    avatar_url = None
    if user_id:
        thumb_resp, terr = safe_get(
            "https://thumbnails.roblox.com/v1/users/avatar-headshot",
            params={"userIds": user_id, "size": "150x150", "format": "Png", "isCircular": "false"},
        )
        if not terr and thumb_resp.status_code == 200:
            thumb_data = thumb_resp.json().get("data", [])
            if thumb_data:
                avatar_url = thumb_data[0].get("imageUrl")

    print_result("Roblox", {
        "User ID": user_id,
        "Username": user.get("name"),
        "Display Name": display_name,
        "Verified Badge": user.get("hasVerifiedBadge"),
        "Deskripsi": detail.get("description") or "-",
        "Akun Dibuat": detail.get("created"),
        "Banned/Terminated": detail.get("isBanned"),
        "Foto Profil": avatar_url,
        "URL Profil": f"https://www.roblox.com/users/{user_id}/profile" if user_id else None,
    }, found=True)


def stalk():
    """Data publik tambahan: friends count, followers, following (semua publik di Roblox)."""
    raw = ask_input("Masukkan Username Roblox yang mau dilihat datanya:")
    if not raw:
        return

    username = raw.strip()
    print_loading("Mengambil data publik")

    lookup_url = "https://users.roblox.com/v1/usernames/users"
    resp, err = safe_post(lookup_url, json_data={"usernames": [username], "excludeBannedUsers": False})
    if err:
        print_error(err)
        return

    results = resp.json().get("data", []) if resp.status_code == 200 else []
    if not results:
        print_result("Stalker Roblox", {"Username": username}, found=False)
        return

    user_id = results[0].get("id")

    friends_count = followers_count = following_count = None
    if user_id:
        f_resp, _ = safe_get(f"https://friends.roblox.com/v1/users/{user_id}/friends/count")
        if f_resp and f_resp.status_code == 200:
            friends_count = f_resp.json().get("count")

        fol_resp, _ = safe_get(f"https://friends.roblox.com/v1/users/{user_id}/followers/count")
        if fol_resp and fol_resp.status_code == 200:
            followers_count = fol_resp.json().get("count")

        fing_resp, _ = safe_get(f"https://friends.roblox.com/v1/users/{user_id}/followings/count")
        if fing_resp and fing_resp.status_code == 200:
            following_count = fing_resp.json().get("count")

    avatar_url = None
    if user_id:
        thumb_resp, _ = safe_get(
            "https://thumbnails.roblox.com/v1/users/avatar-headshot",
            params={"userIds": user_id, "size": "150x150", "format": "Png", "isCircular": "false"},
        )
        if thumb_resp and thumb_resp.status_code == 200:
            thumb_data = thumb_resp.json().get("data", [])
            if thumb_data:
                avatar_url = thumb_data[0].get("imageUrl")

    print_result("Stalker Roblox (Data Publik)", {
        "Username": results[0].get("name"),
        "Display Name": results[0].get("displayName"),
        "Friends": friends_count,
        "Followers": followers_count,
        "Following": following_count,
        "Foto Profil": avatar_url,
        "URL Profil": f"https://www.roblox.com/users/{user_id}/profile" if user_id else None,
    }, found=True)
