import code
from flask import Flask, render_template, request, redirect, session

from config import BOT_TOKEN, CLIENT_SECRET, OAUTH_URL, REDIRECT_URI, PORT
from oauth import Oauth

app = Flask(__name__)

app.config["SECRET_KEY"] = CLIENT_SECRET


@app.route("/")
def home():
    access_token = session.get("access_token")

    if not access_token:
        return redirect("/login")

    user_json = Oauth.get_user_json(access_token)
    user_id = user_json.get("id")
    user_avatar = "https://cdn.discordapp.com/avatars/" + user_id + "/" + user_json.get("avatar")

    user_guils = Oauth.get_user_guilds(access_token)

    return render_template("index.html", user_avatar=user_avatar, user_guils=user_guils)

@app.route("/login")
def login():
    return redirect(OAUTH_URL)


@app.route("/logout")
def logout():
    session.pop("access_token")
    return redirect("/")


@app.route("/oauth/callback")
def oauth_callback():
    code = request.args["code"]
    access_token = Oauth.get_access_token(code)
    session["access_token"] = access_token

    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=PORT)