"""bluesky girls be like dracula bot"""

import json
import os
import requests
import secrets
import sys
from datetime import datetime, timezone
from typing import Dict


DRACULA_PATH = "./dracula_stoker_project_gutenberg.txt"

SEPARATOR = "*       *       *       *       *"

GIRLS_BE_LIKE = "Girls be like:\n\n"

HOST = os.environ.get("ATP_PDS_HOST", "https://bsky.social")
HANDLE = os.environ.get("BSKY_HANDLE")
PASSWORD = os.environ.get("BSKY_PASSWORD")


if not HANDLE or not PASSWORD:
    print("BSKY_HANDLE AND BSKY_PASSWORD env vars required, quitting", file=sys.stderr)
    sys.exit(1)


def bsky_login_session() -> Dict:
    resp = requests.post(
        HOST + "/xrpc/com.atproto.server.createSession",
        json={"identifier": HANDLE, "password": PASSWORD},
    )
    resp.raise_for_status()
    return resp.json()


def create_post(post_text: str) -> None:
    session = bsky_login_session()

    post = {
        "$type": "app.bsky.feed.post",
        "text": post_text,
        "createdAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }

    print("creating post:", file=sys.stderr)
    print(json.dumps(post, indent=2), file=sys.stderr)

    resp = requests.post(
        HOST + "/xrpc/com.atproto.repo.createRecord",
        headers={"Authorization": "Bearer " + session["accessJwt"]},
        json={
            "repo": session["did"],
            "collection": "app.bsky.feed.post",
            "record": post,
        },
    )
    print("createRecord response:", file=sys.stderr)
    print(json.dumps(resp.json(), indent=2))
    resp.raise_for_status()


def prepare_post() -> str:
    with open(os.path.abspath(DRACULA_PATH)) as book:
        dracula_txt = book.read()

    dracula_lines = [line.replace("\n", " ") for line in dracula_txt.split("\n\n") if line.strip() and not SEPARATOR in line.strip()]
    random_line = dracula_lines[secrets.randbelow(len(dracula_lines))]

    # Let's make this a bit less racist...
    random_line.replace("gypsy", "Roma")
    random_line.replace("gipsy", "Roma")
    random_line.replace("Gypsy", "Roma")
    random_line.replace("Gipsy", "Roma")

    random_line_truncated = random_line[:275]
    if random_line != random_line_truncated:
        return f"{GIRLS_BE_LIKE}{random_line_truncated}..."

    return f"{GIRLS_BE_LIKE}{random_line}"


def main() -> None:
    post = prepare_post()
    create_post(post)


if __name__ == "__main__":
    main()
