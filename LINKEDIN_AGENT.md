# LinkedIn Agent

Personal agent: daily post drafts, custom posts, profile audit, analytics. Posts to your **personal profile** (not a Page).

## What's possible (LinkedIn API limits)
| Goal | How | Status |
|---|---|---|
| Post to personal profile | `Share on LinkedIn` (`w_member_social`) + OpenID Connect | Automated |
| Profile audit / gap filling | Your LinkedIn data export (CSV) in `exports/` + Claude analysis | Manual export |
| Analytics | Analytics CSV export from LinkedIn in `exports/` | Manual export (Community Management API skipped — restricted) |

## Pieces
- `server.py` — MCP server, tools: `linkedin_auth_url`, `linkedin_exchange_code`, `get_my_urn`, `create_post`, `read_export`
- `mcp_config.json` — registers the `linkedin` server
- `.env` — client id/secret (gitignored). `token.json` — access token (gitignored, ~60 days)
- `topics.md` — your pillars, voice, schedule, projects
- `exports/` — drop LinkedIn CSVs here; `drafts/` — daily drafts

## Flows
- **Daily post**: Claude reads `topics.md` → drafts → saves `drafts/DATE.md` → you approve → `create_post`.
- **Custom post**: tell Claude what to say → it polishes → you approve → `create_post`.
- **Profile audit**: Claude reads the export via `read_export` → gap list + rewritten headline/About/Experience/Skills.
- **Analytics**: Claude reads analytics CSVs → what worked, best topics/times, next actions.

## Steps for you
1. `pip install -r requirements.txt` (in `Linkedin Mcp/`).
2. Reload the MCP servers in your client so `linkedin` appears.
3. One-time login: ask Claude to run `linkedin_auth_url`, open it, approve, copy the `code=` value from the redirect URL (the page may not load — fine), give it to Claude (`linkedin_exchange_code`).
4. Test: ask Claude `get_my_urn`, then a `create_post` with visibility `CONNECTIONS`; delete the test post by hand.
5. Send me the profile data export when it arrives (unzip into `exports/`) and the automation document.
6. Fill the **Projects** section in `topics.md`.
7. **Rotate the client secret** (it was pasted in chat), update `.env`.
8. Tell me when to set up the daily scheduled routine (default: draft + approval, not auto-post).

## Posting times (Asia/Karachi)
- Weekdays: Tue–Thu 19:30 (≈10:30 ET / 15:30 UK / 18:30 Gulf); Mon/Fri 19:30, lighter content.
- Weekend: Sat 11:00; Sun optional 20:00.
- Tune after 2–3 weeks using your own analytics.

## Notes
- Token expires in ~60 days: re-run the login.
- `create_post` escapes LinkedIn markup characters; hashtags post as plain text. Mentions/links previews not supported.
- Not built: images/carousels, auto-commenting (ToS risk), history DB.
