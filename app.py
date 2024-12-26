from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from config import Config
from extensions import db
from routes.auth import auth_bp
from routes.chatbot import chatbot_bp
from routes.inventory import inventory_bp
import os
from flask_migrate import Migrate
from sqlalchemy import Text
from sqlalchemy.dialects import postgresql
from routes.analytics import analytics_bp

def create_app():
    app = Flask(__name__) 
    app.config.from_object(Config)
    
    CORS(app, supports_credentials=True)
    db.init_app(app)
    migrate = Migrate(app, db)
    app.register_blueprint(auth_bp)
    app.register_blueprint(chatbot_bp)
    # app.register_blueprint(inventory_bp)
    app.register_blueprint(analytics_bp)

    with app.app_context():
        db.create_all()
    
    return app

# Create the app instance at module level for Gunicorn to find
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
# from flask import Flask, send_from_directory
# from flask_cors import CORS
# from flask_sqlalchemy import SQLAlchemy
# from config import Config
# from extensions import db, mongo_client
# from routes.auth import auth_bp
# from routes.chatbot import chatbot_bp
# from routes.inventory import inventory_bp
# import os
# from flask_migrate import Migrate
# from sqlalchemy import Text
# from sqlalchemy.dialects import postgresql
# from routes.analytics import analytics_bp
# from waitress import serve

# def create_app():
#     app = Flask(__name__, static_url_path='/static')  # Ensure static files are served from the correct path
#     app.config.from_object(Config)
    
#     CORS(app, supports_credentials=True)
#     db.init_app(app)
#     migrate = Migrate(app, db)
#     app.register_blueprint(auth_bp)
#     app.register_blueprint(chatbot_bp)  # Ensure this blueprint includes the new route for chatbot integration
#     app.register_blueprint(inventory_bp)
#     app.register_blueprint(analytics_bp)

#     # Serve static files from the 'static' directory
#     @app.route('/static/<path:path>')
#     def send_static(path):
#         return send_from_directory('static', path)

#     with app.app_context():
#         db.create_all()
    
#     return app

# # if __name__ == '__main__':
# #     port = int(os.environ.get('PORT', 5000))
# #     app = create_app()
# #     app.run(host='0.0.0.0', port=port, debug=True)


# if __name__ == "__main__":
#     app = create_app()
#     serve(app, host='0.0.0.0', port=8000)


