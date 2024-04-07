from twikit import Client

client = Client("ja-JP")
client.load_cookies("cookies.json")

# ツイートを作成
client.create_tweet("テストツイート")