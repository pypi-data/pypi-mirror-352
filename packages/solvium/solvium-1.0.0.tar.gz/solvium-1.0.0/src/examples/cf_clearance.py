import base64
import os
import httpx
from solvium import Solvium

# Step 0. Change Parameters
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
PROXY = os.environ.get("PROXY")
assert PROXY is not None, "Please set the PROXY environment variable."
WEBSITE_WITH_CLOUDFLARE_WALL = "https://loyalty.campnetwork.xyz/loyalty"
API_KEY = os.environ.get("API_KEY")
assert API_KEY is not None, "Please set the API_KEY environment variable."

solvium = Solvium(API_KEY, verbose=True)
session = httpx.Client(headers={"User-Agent": USER_AGENT}, proxy=PROXY, verify=False)

# Step 1. Obtain Challenge Token
response = session.get(WEBSITE_WITH_CLOUDFLARE_WALL)

# Step 2. Solve Challenge Using Solvium API
solution = solvium.cf_clearance_sync(
    WEBSITE_WITH_CLOUDFLARE_WALL, base64.b64encode(response.content).decode(), PROXY
)
assert solution is not None

session.cookies.update(
    {"cf_clearance": solution},
)

# Step 3. Make Requests With Cookie
response = session.get(WEBSITE_WITH_CLOUDFLARE_WALL)

print(response.status_code)
