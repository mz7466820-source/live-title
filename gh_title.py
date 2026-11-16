import os, json, time
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

VIDEO_ID = "YzMvgrI_58M"
TEMPLATE = "What If You're The {n} Person To Watch This… And The Last?"
ROUNDS, GAP = 35, 600  # 4 checks, 10 minutes apart

def ordinal(n):
    suf = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n:,}{suf}"

creds = Credentials.from_authorized_user_info(json.loads(os.environ["TOKEN_JSON"]), ["https://www.googleapis.com/auth/youtube"])
for r in range(ROUNDS):
    if not creds.valid: creds.refresh(Request())
    yt = build("youtube", "v3", credentials=creds)
    v = yt.videos().list(part="snippet,statistics", id=VIDEO_ID).execute()["items"][0]
    views = int(v["statistics"].get("viewCount", 0))
    title = TEMPLATE.format(n=ordinal(views + 1))
    sn = v["snippet"]
    if sn["title"] == title:
        print(time.strftime("%H:%M"), "no change", views)
    else:
        body = {"id": VIDEO_ID, "snippet": {"title": title, "categoryId": sn["categoryId"], "description": sn.get("description", ""),
                                            "tags": sn.get("tags", []), "defaultLanguage": sn.get("defaultLanguage", "en")}}
        yt.videos().update(part="snippet", body=body).execute()
        print(time.strftime("%H:%M"), "updated ->", title)
    if r < ROUNDS - 1: time.sleep(GAP)
