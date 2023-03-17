import requests
from config import BOT_TOKEN, CLIENT_SECRET, OAUTH_URL, REDIRECT_URI, PORT, CLIENT_ID, SCOPE

class Oauth:
    client_id = CLIENT_ID
    client_secret = CLIENT_SECRET
    redirect_uri = REDIRECT_URI
    scope = SCOPE
    discord_login_url = "https://discord.com/api/oauth2/authorize?client_id=479295552467763201&redirect_uri=http%3A%2F%2Flocalhost%3A5000%2Foauth%2Fcallback&response_type=code&scope=identify%20guilds" # Paste the generated Oauth2 link here
    discord_token_url = "https://discord.com/api/oauth2/token"
    discord_api_url = "https://discord.com/api"
 
    @staticmethod
    def get_access_token(code):
        payload = {
            "client_id": Oauth.client_id,
            "client_secret": Oauth.client_secret,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": Oauth.redirect_uri,
            "scope": Oauth.scope
        }
        access_token = requests.post(url = Oauth.discord_token_url, data = payload).json()
        return access_token.get("access_token")

    @staticmethod
    def get_user_json(access_token):
        url = f"{Oauth.discord_api_url}/users/@me"
        headers = {"Authorization": f"Bearer {access_token}"}
 
        user_object = requests.get(url = url, headers = headers).json()
        return user_object

    @staticmethod
    def get_user_guilds(access_token):
        url = f"{Oauth.discord_api_url}/users/@me/guilds"
        headers = {"Authorization": f"Bearer {access_token}"}
 
        user_guilds = requests.get(url = url, headers = headers).json()
        return user_guilds

    @staticmethod
    def get_any_user(user_id):
        url = f"{Oauth.discord_api_url}/users/{user_id}"
        headers = {"Authorization": f"Bot {BOT_TOKEN}"}
 
        user_object = requests.get(url = url, headers = headers).json()
        return user_object