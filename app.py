# from flask import Flask, send_from_directory
# from flask_cors import CORS
# from flask_sqlalchemy import SQLAlchemy
# from config import Config
# from extensions import db
# from routes.auth import auth_bp
# from routes.chatbot import chatbot_bp
# # from routes.inventory import inventory_bp
# import os
# from flask_migrate import Migrate
# from sqlalchemy import Text
# from sqlalchemy.dialects import postgresql
# from routes.analytics import analytics_bp

# # def create_app():
# #     app = Flask(__name__) 
# #     app.config.from_object(Config)
    
# #     CORS(app, supports_credentials=True)
# #     db.init_app(app)
# #     migrate = Migrate(app, db)
# #     app.register_blueprint(auth_bp)
# #     app.register_blueprint(chatbot_bp)
# #     # app.register_blueprint(inventory_bp)
# #     app.register_blueprint(analytics_bp)

# #     with app.app_context():
# #         db.create_all()
    
# #     return app

# def create_app():
#     app = Flask(__name__) 
#     app.config.from_object(Config)
    
#     # # Update CORS configuration
#     # CORS(app, 
#     #      resources={r"/*": {
#     #          "origins": [
#     #              "https://xavier-ai-frontend.vercel.app",  # Your Vercel domain
#     #              "http://localhost:4200",  # Local development
#     #              "http://localhost:3000"   # Local development alternative
#     #          ],
#     #          "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
#     #          "allow_headers": ["Content-Type", "Authorization"],
#     #          "supports_credentials": True
#     #      }})
#     # CORS(app, resources={r"/*": {"origins": ["http://localhost:4200","https://xavier-ai-frontend-3wwy89gjm-temis-projects-568593b8.vercel.app"]}})

#     CORS(app, resources={r"/*": {"origins": [
#     "https://xavier-ai-frontend.vercel.app"  # Add this
#     ]}})
    
#     db.init_app(app)
#     migrate = Migrate(app, db)
#     app.register_blueprint(auth_bp)
#     app.register_blueprint(chatbot_bp)
#     # app.register_blueprint(inventory_bp)
#     app.register_blueprint(analytics_bp)

#     with app.app_context():
#         db.create_all()
    
#     return app

# # Create the app instance at module level for Gunicorn to find
# app = create_app()

# if __name__ == '__main__':
#     port = int(os.environ.get('PORT', 5000))
#     app.run(host='0.0.0.0', port=port, debug=True)
# # from flask import Flask, send_from_directory
# # from flask_cors import CORS
# # from flask_sqlalchemy import SQLAlchemy
# # from config import Config
# # from extensions import db, mongo_client
# # from routes.auth import auth_bp
# # from routes.chatbot import chatbot_bp
# # from routes.inventory import inventory_bp
# # import os
# # from flask_migrate import Migrate
# # from sqlalchemy import Text
# # from sqlalchemy.dialects import postgresql
# # from routes.analytics import analytics_bp
# # from waitress import serve

# # def create_app():
# #     app = Flask(__name__, static_url_path='/static')  # Ensure static files are served from the correct path
# #     app.config.from_object(Config)
    
# #     CORS(app, supports_credentials=True)
# #     db.init_app(app)
# #     migrate = Migrate(app, db)
# #     app.register_blueprint(auth_bp)
# #     app.register_blueprint(chatbot_bp)  # Ensure this blueprint includes the new route for chatbot integration
# #     app.register_blueprint(inventory_bp)
# #     app.register_blueprint(analytics_bp)

# #     # Serve static files from the 'static' directory
# #     @app.route('/static/<path:path>')
# #     def send_static(path):
# #         return send_from_directory('static', path)

# #     with app.app_context():
# #         db.create_all()
    
# #     return app

# # # if __name__ == '__main__':
# # #     port = int(os.environ.get('PORT', 5000))
# # #     app = create_app()
# # #     app.run(host='0.0.0.0', port=port, debug=True)


# # if __name__ == "__main__":
# #     app = create_app()
# #     serve(app, host='0.0.0.0', port=8000)







# from flask import Flask, send_from_directory
# from flask_cors import CORS
# from flask_sqlalchemy import SQLAlchemy
# from config import Config
# from extensions import db
# from routes.auth import auth_bp
# from routes.chatbot import chatbot_bp
# from routes.analytics import analytics_bp
# import os
# from flask_migrate import Migrate
# from sqlalchemy import Text
# from sqlalchemy.dialects import postgresql

# def create_app():
#     app = Flask(__name__)
#     app.config.from_object(Config)
    
    
#     # Configure CORS with all necessary settings
#     CORS(app, 
#          resources={r"/*": {
#              "origins": ["https://xavier-ai-frontend.vercel.app"],
#              "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
#              "allow_headers": ["Content-Type", "Authorization"],
#              "expose_headers": ["Content-Type", "Authorization"],
#              "supports_credentials": True,
#              "send_wildcard": False,
#              "max_age": 86400
#          }})
    
#     # Initialize extensions
#     db.init_app(app)
#     migrate = Migrate(app, db)
    
#     # Register blueprints
#     app.register_blueprint(auth_bp)
#     app.register_blueprint(chatbot_bp)
#     app.register_blueprint(analytics_bp)
    
#     # Create database tables
#     with app.app_context():
#         db.create_all()
    
#     # Add CORS headers to all responses
#     @app.after_request
#     def after_request(response):
#         response.headers.add('Access-Control-Allow-Origin', 'https://xavier-ai-frontend.vercel.app')
#         response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
#         response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
#         response.headers.add('Access-Control-Allow-Credentials', 'true')
#         return response
    
#     return app

# # Create the app instance for Gunicorn
# app = create_app()

# if __name__ == '__main__':
#     port = int(os.environ.get('PORT', 5000))
#     app.run(host='0.0.0.0', port=port, debug=True)


from flask import Flask, send_from_directory,request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from config import Config
from extensions import db
from routes.auth import auth_bp
from routes.chatbot import chatbot_bp
from routes.analytics import analytics_bp
import os
from flask_migrate import Migrate
from sqlalchemy import Text
from sqlalchemy.dialects import postgresql

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Add session cookie configuration
    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_SAMESITE='None',
        SESSION_COOKIE_HTTPONLY=True
    )
    
    # Configure CORS with all necessary settings
    CORS(app, 
         resources={r"/*": {
             "origins": [
                 "https://xavier-ai-frontend.vercel.app",
                 "http://localhost:4200"  # Add this for local development
             ],
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization", "X-CSRFToken"],
             "expose_headers": ["Content-Type", "Authorization", "X-CSRFToken"],
             "supports_credentials": True,
             "send_wildcard": False,
             "max_age": 86400
         }})
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(chatbot_bp)
    app.register_blueprint(analytics_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'https://xavier-ai-frontend.vercel.app')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-CSRFToken')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Expose-Headers', 'Content-Type,Authorization,X-CSRFToken')
    return response
    
    return app

# Create the app instance for Gunicorn
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
