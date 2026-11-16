import os, json, time
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

VIDEO_ID = "c9lYTCgD7_o"
ROUNDS, GAP = 23, 900          # ~6 hour run, checks every 15 minutes

def make_title(views):
    n = views + 1
    suf = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"What If You're The {n:,}{suf} Person… And I Heard Your Secret?"

creds = Credentials.from_authorized_user_info(json.loads(os.environ["TOKEN_JSON"]), ["https://www.googleapis.com/auth/youtube"])
for r in range(ROUNDS):
    try:
        if not creds.valid: creds.refresh(Request())
        yt = build("youtube", "v3", credentials=creds, cache_discovery=False)
        v = yt.videos().list(part="snippet,statistics", id=VIDEO_ID).execute()["items"][0]
        views = int(v["statistics"].get("viewCount", 0)); title = make_title(views); sn = v["snippet"]
        if sn["title"] != title:
            body = {"id": VIDEO_ID, "snippet": {"title": title, "categoryId": sn["categoryId"], "description": sn.get("description", ""),
                    "tags": sn.get("tags", []), "defaultLanguage": sn.get("defaultLanguage", "en")}}
            yt.videos().update(part="snippet", body=body).execute(); print(time.strftime("%H:%M"), "updated ->", title, flush=True)
        else: print(time.strftime("%H:%M"), "no change", views, flush=True)
    except Exception as e: print("error:", e, flush=True)
    if r < ROUNDS - 1: time.sleep(GAP)
