from flask import Flask
from flask_cors import CORS
from routes.news_routes import news_bp

app = Flask(__name__)
CORS(app)  # permite llamadas desde tu app React Native

app.register_blueprint(news_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
