from urllib import parse

PORT = 5000
BOT_TOKEN = "NDc5Mjk1NTUyNDY3NzYzMjAx.GF1vkA.-7xPUBk9g_sNYGoRtix043JXxzMS5KjF1Bs2BE"
CLIENT_SECRET = "04tXa91HNFY3VkKs2k3_5olq8j_bVpp6"
CLIENT_ID = "479295552467763201"
REDIRECT_URI = f"http://localhost:{PORT}/oauth/callback"
SCOPE = f"identify%20guilds"
OAUTH_URL = f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={parse.quote(REDIRECT_URI)}&response_type=code&scope={SCOPE}"
