# from flask import Flask, send_from_directory, request
# from flask_cors import CORS
# from flask_sqlalchemy import SQLAlchemy
# from flask_socketio import SocketIO
# from config import Config
# from extensions import db
# from routes.auth import auth_bp
# from routes.chatbot import chatbot_bp
# from routes.analytics import analytics_bp
# import os
# from flask_migrate import Migrate
# from sqlalchemy import Text
# from sqlalchemy.dialects import postgresql
# from models import User

# # Initialize Socket.IO without an app instance
# socketio = SocketIO()

# def create_app():
#     app = Flask(__name__)
#     app.config.from_object(Config)
    
#     app.config.update(
#         SESSION_COOKIE_SECURE=True,
#         SESSION_COOKIE_SAMESITE='None',
#         SESSION_COOKIE_HTTPONLY=True,
#         GOOGLE_CLIENT_ID='322331794855-65p20krn34skfti51505m84o1gukdn7l.apps.googleusercontent.com',
#         GOOGLE_CLIENT_SECRET='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',
#         GOOGLE_REDIRECT_URI='http://localhost:5000/oauth2callback'
#     )

#     # Configure CORS with all necessary settings
#     CORS(app, 
#          resources={r"/*": {
#              "origins": [
#                  "http://localhost:4200","null"
#              ],
#              "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS","PATCH"],
#              "allow_headers": ["Content-Type", "Authorization", "X-CSRFToken","User-ID"],
#              "expose_headers": ["Content-Type", "Authorization", "X-CSRFToken"],
#              "supports_credentials": True,
#              "send_wildcard": False,
#              "max_age": 86400
#          }})
    
#     # Initialize Socket.IO with your Flask app
#     socketio.init_app(app, 
#                      cors_allowed_origins=[
#                          "http://localhost:4200"
#                      ],
#                      async_mode='eventlet')
    
#     # Initialize extensions
#     db.init_app(app)
#     migrate = Migrate(app, db)
    
#     # Register blueprints
#     app.register_blueprint(auth_bp)
#     app.register_blueprint(chatbot_bp)
#     app.register_blueprint(analytics_bp)
    
#     # Create database tables and default user
#     with app.app_context():
#         try:
#             db.create_all()
#             default_user = User.query.get(4269)
#             if not default_user:
#                 default_user = User(
#                     id=4269,
#                     username='default_ticket_user',
#                     password_hash='default_not_used'
#                 )
#                 db.session.add(default_user)
#                 db.session.commit()
#                 print("Default user created successfully")
#             else:
#                 print("Default user already exists")
#         except Exception as e:
#             print(f"Database initialization error: {e}")
#             db.session.rollback()
    
#     return app

# # Create the app instance
# app = create_app()


# if __name__ == '__main__':
#     port = int(os.environ.get('PORT', 5000))
#     # Use socketio.run instead of app.run
#     socketio.run(app, host='0.0.0.0', port=port, debug=True)






from flask import Flask, send_from_directory, request
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
from models import User  # Add this import


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Add session cookie configuration
    # app.config.update(
    #     SESSION_COOKIE_SECURE=True,
    #     SESSION_COOKIE_SAMESITE='None',
    #     SESSION_COOKIE_HTTPONLY=True
    #     GOOGLE_CLIENT_ID='322331794855-65p20krn34skfti51505m84o1gukdn7l.apps.googleusercontent.com',
    #     GOOGLE_CLIENT_SECRET='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',
    #     GOOGLE_REDIRECT_URI='http://localhost:5000/oauth2callback'
    # )

    #     # Add session cookie configuration
    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_SAMESITE='None',
        SESSION_COOKIE_HTTPONLY=True,
        GOOGLE_CLIENT_ID='322331794855-65p20krn34skfti51505m84o1gukdn7l.apps.googleusercontent.com',
        GOOGLE_CLIENT_SECRET='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',
        GOOGLE_REDIRECT_URI='http://localhost:5000/oauth2callback'
    )

    
    # Configure CORS with all necessary settings
    CORS(app, 
         resources={r"/*": {
             "origins": [
                #  "https://xavierai.vercel.app",
                 "http://localhost:4200",  
             ],
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS","PATCH"],
             "allow_headers": ["Content-Type", "Authorization", "X-CSRFToken","User-ID"],
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
    
    # Create database tables and default user
    with app.app_context():
        try:
            db.create_all()
            # Check if default user exists
            default_user = User.query.get(4269)
            if not default_user:
                default_user = User(
                    id=4269,
                    username='default_ticket_user',
                    password_hash='default_not_used'
                )
                db.session.add(default_user)
                db.session.commit()
                print("Default user created successfully")
            else:
                print("Default user already exists")
        except Exception as e:
            print(f"Database initialization error: {e}")
            db.session.rollback()
    
    return app

# Create the app instance for Gunicorn
app = create_app()


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
    




# from flask import Flask, send_from_directory, request
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
# from models import User, GmailIntegration  # Add GmailIntegration here

# def create_app():
#     app = Flask(__name__)
#     app.config.from_object(Config)
    
#     # Add session cookie configuration
#     app.config.update(
#         SESSION_COOKIE_SECURE=True,
#         SESSION_COOKIE_SAMESITE='None',
#         SESSION_COOKIE_HTTPONLY=True,
#         GOOGLE_CLIENT_ID='322331794855-65p20krn34skfti51505m84o1gukdn7l.apps.googleusercontent.com',
#         GOOGLE_CLIENT_SECRET='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',
#         GOOGLE_REDIRECT_URI='http://localhost:5000/oauth2callback'
#     )
    
#     # Rest of your CORS configuration...
    
#     # Initialize extensions
#     db.init_app(app)
#     migrate = Migrate(app, db)
    
#     # Register blueprints
#     app.register_blueprint(auth_bp)
#     app.register_blueprint(chatbot_bp)
#     app.register_blueprint(analytics_bp)
    
#     # Create database tables and default user
#     with app.app_context():
#         try:
#             db.create_all()
#             # Check if default user exists
#             default_user = User.query.get(4269)
#             if not default_user:
#                 default_user = User(
#                     id=4269,
#                     username='default_ticket_user',
#                     password_hash='default_not_used'
#                 )
#                 db.session.add(default_user)
#                 db.session.commit()
#                 print("Default user created successfully")
#             else:
#                 print("Default user already exists")
#         except Exception as e:
#             print(f"Database initialization error: {e}")
#             db.session.rollback()
    
#     return app

# # Create the app instance for Gunicorn
# app = create_app()

# if __name__ == '__main__':
#     port = int(os.environ.get('PORT', 5000))
#     app.run(host='0.0.0.0', port=port, debug=True)