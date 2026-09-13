import aiohttp
from config import LINK_BASE


def get_file_link(uid: str) -> str:
    return f"{LINK_BASE}{uid}"


def get_batch_link(batch_id: str) -> str:
    return f"{LINK_BASE}batch_{batch_id}"


def human_size(size_bytes: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


async def shorten_url(api_key: str, domain: str, long_url: str) -> str:
    """Generic shortener — works with ShrinkMe/AdFly style APIs."""
    try:
        api_url = f"https://{domain}/api?api={api_key}&url={long_url}"
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                data = await resp.json()
                return data.get("shortenedUrl") or data.get("short_url") or long_url
    except Exception:
        return long_url  # Fallback to original link on failure


def is_valid_user_id(uid) -> bool:
    try:
        int(uid)
        return True
    except (ValueError, TypeError):
        return False
