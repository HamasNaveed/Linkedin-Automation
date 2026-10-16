"""LinkedIn MCP: post to your personal profile + read exported data. Claude does the thinking."""
import json, os, re
from pathlib import Path
import httpx
from mcp.server.fastmcp import FastMCP

HERE = Path(__file__).parent
TOKEN = HERE / "token.json"
API_VERSION = "202609"  # LinkedIn-Version header; bump if API says version is sunset

for line in (HERE / ".env").read_text().splitlines() if (HERE / ".env").exists() else []:
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

CID, SECRET = os.environ["LINKEDIN_CLIENT_ID"], os.environ["LINKEDIN_CLIENT_SECRET"]
REDIRECT = os.environ.get("LINKEDIN_REDIRECT_URI", "http://localhost:8080/callback")
mcp = FastMCP("linkedin")


def _token() -> str:
    if not TOKEN.exists():
        raise RuntimeError("Not authorised. Call linkedin_auth_url, then linkedin_exchange_code.")
    return json.loads(TOKEN.read_text())["access_token"]


@mcp.tool()
def linkedin_auth_url() -> str:
    """Step 1 of one-time login: open this URL in a browser and approve."""
    return ("https://www.linkedin.com/oauth/v2/authorization?response_type=code"
            f"&client_id={CID}&redirect_uri={REDIRECT}&scope=openid%20profile%20w_member_social&state=x")


@mcp.tool()
def linkedin_exchange_code(code: str) -> str:
    """Step 2: paste the `code` param from the redirect URL (page may fail to load; copy URL anyway)."""
    r = httpx.post("https://www.linkedin.com/oauth/v2/accessToken", data={
        "grant_type": "authorization_code", "code": code, "client_id": CID,
        "client_secret": SECRET, "redirect_uri": REDIRECT})
    r.raise_for_status()
    TOKEN.write_text(r.text)  # token lasts ~60 days; re-run login when expired
    return "Token saved."


@mcp.tool()
def get_my_urn() -> str:
    """Your member URN (author id for posts)."""
    r = httpx.get("https://api.linkedin.com/v2/userinfo", headers={"Authorization": f"Bearer {_token()}"})
    r.raise_for_status()
    return f"urn:li:person:{r.json()['sub']}"


def _escape(t: str) -> str:
    # LinkedIn "little text" treats these as markup; unescaped they truncate the post
    return re.sub(r"([\|{}@\[\]()<>#*_~])", r"\\1", t)


@mcp.tool()
def create_post(text: str, visibility: str = "PUBLIC") -> str:
    """Publish a text post on the personal profile. visibility: PUBLIC or CONNECTIONS.
    Hashtags: write them as plain text; they are escaped, so they appear as text not links."""
    r = httpx.post("https://api.linkedin.com/rest/posts", json={
        "author": get_my_urn(), "commentary": _escape(text), "visibility": visibility,
        "distribution": {"feedDistribution": "MAIN_FEED", "targetEntities": [], "thirdPartyDistributionChannels": []},
        "lifecycleState": "PUBLISHED", "isReshareDisabledByAuthor": False},
        headers={"Authorization": f"Bearer {_token()}", "LinkedIn-Version": API_VERSION,
                 "X-Restli-Protocol-Version": "2.0.0"})
    if r.status_code != 201:
        return f"FAILED {r.status_code}: {r.text}"
    return f"Posted. id={r.headers.get('x-restli-id')}"


@mcp.tool()
def read_export(name: str = "") -> str:
    """List files in exports/ (no name) or return a file's text (first 30k chars). Use for profile audit + analytics."""
    d = HERE / "exports"
    if not name:
        return "\n".join(str(p.relative_to(d)) for p in d.rglob("*") if p.is_file()) or "exports/ is empty"
    p = (d / name).resolve()
    if d.resolve() not in p.parents:
        return "Invalid path"
    return p.read_text(encoding="utf-8-sig", errors="replace")[:30000]


if __name__ == "__main__":
    mcp.run()
