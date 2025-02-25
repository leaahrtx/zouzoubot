from flask import Flask
import os

app = Flask(__name__)

os.environ["REPLIT_DB_URL"] = "https://ton-bot.repl.co/"

@app.route('/')
def home():
    return "Le bot est en ligne !"

def run():
    app.run(host="0.0.0.0", port=8080)

if __name__ == "__main__":
    run()