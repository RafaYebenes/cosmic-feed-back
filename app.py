from flask import Flask
from flask_cors import CORS
from routes.news_routes import news_bp
from routes.forum_routes import forum_bp
app = Flask(__name__)
CORS(app, supports_credentials=True, allow_headers=["Content-Type", "Authorization"])

app.register_blueprint(news_bp)
app.register_blueprint(forum_bp, url_prefix="/api")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5002, debug=True)
