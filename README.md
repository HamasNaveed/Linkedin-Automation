# LinkedIn Automation

MCP server that lets Claude draft and publish posts to a personal LinkedIn profile, and analyse profile/analytics exports.

## Setup
1. `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and fill in your LinkedIn app credentials.
3. Copy `mcp_config.example.json` into your MCP client config and fix the path.
4. Run `linkedin_auth_url`, approve, then `linkedin_exchange_code` with the `code` from the redirect URL.

## Tools
`linkedin_auth_url`, `linkedin_exchange_code`, `get_my_urn`, `create_post`, `read_export`

See [LINKEDIN_AGENT.md](LINKEDIN_AGENT.md) for the full plan and flows.
