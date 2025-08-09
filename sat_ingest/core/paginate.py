from typing import Iterable, Callable, Optional

def page_through(fetch: Callable[[Optional[str]], dict]) -> Iterable[dict]:
    """Generic page iterator.

    `fetch(next_token) -> {"items": [...], "next": token or None}`
    """
    token = None
    while True:
        batch = fetch(token)
        for it in batch.get("items", []):
            yield it
        token = batch.get("next")
        if not token:
            break
        
        