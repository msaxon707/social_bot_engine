import base64
import http.server
import socketserver
import webbrowser
import urllib.parse
import requests
import threading
import os

# === CONFIG ===
CLIENT_ID = os.getenv("PINTEREST_APP_ID", "1536738")
CLIENT_SECRET = os.getenv("PINTEREST_APP_SECRET", "dcff73XXXXXX")  # replace with your secret
REDIRECT_URI = "http://localhost:8080"
SCOPES = "pins:read,pins:write,boards:read,boards:write,user_accounts:read"
STATE = "1234"


# === Step 1: Small temporary HTTP server to catch redirect ===
class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        if "code" in params:
            code = params["code"][0]
            print(f"\n✅ Got authorization code: {code}\n")
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"<h2>Pinterest Auth Successful! You can close this window.</h2>")
            threading.Thread(target=exchange_code_for_token, args=(code,)).start()
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"<h2>Missing code parameter</h2>")


def run_server():
    with socketserver.TCPServer(("", 8080), Handler) as httpd:
        print("🌐 Waiting for Pinterest OAuth redirect...")
        httpd.serve_forever()


# === Step 2: Exchange code for access token ===
def exchange_code_for_token(code: str):
    print("🔄 Exchanging code for access token...")
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded_auth = base64.b64encode(auth_str.encode()).decode()

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }

    headers = {
        "Authorization": f"Basic {encoded_auth}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    response = requests.post("https://api.pinterest.com/v5/oauth/token", headers=headers, data=data)

    if response.ok:
        token_data = response.json()
        print("\n🎉 SUCCESS! Here are your Pinterest tokens:\n")
        print(response.text)
        print("\n💾 Save this to your .env as:")
        print(f"PINTEREST_ACCESS_TOKEN={token_data['access_token']}")
        if "refresh_token" in token_data:
            print(f"PINTEREST_REFRESH_TOKEN={token_data['refresh_token']}")
    else:
        print("\n❌ ERROR: Could not exchange token\n")
        print(response.text)
    os._exit(0)


# === Step 3: Open Pinterest OAuth ===
if __name__ == "__main__":
    auth_url = (
        f"https://www.pinterest.com/oauth/?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
        f"&scope={SCOPES}"
        f"&state={STATE}"
    )
    print(f"🚀 Opening Pinterest OAuth in your browser...\n{auth_url}\n")
    threading.Thread(target=run_server, daemon=True).start()
    webbrowser.open(auth_url)
    input("Press ENTER to quit when done...\n")
