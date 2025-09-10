from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_cors import CORS
from flask_login import LoginManager, current_user

class MockUser:
    def is_authenticated(self):
        return False
        
    def is_admin(self):
        return False
        
    def is_police(self):
        return False

# Create a mock current_user for templates
mock_user = MockUser()

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    app.config['SECRET_KEY'] = 'dev-key-for-testing'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fir.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Setup login manager with minimal functionality
    login_manager = LoginManager()
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return None
    
    # Add template context processor to provide current_user
    @app.context_processor
    def inject_user():
        return {'current_user': mock_user}
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/health')
    def health_check():
        return {'status': 'ok', 'message': 'Application is running'}
        
    @app.route('/api/speech/languages')
    def get_languages():
        # Mock language data to prevent JavaScript errors
        languages = [
            {
                "code": "en-US",
                "name": "English (United States)",
                "native_name": "English",
                "flag": "🇺🇸"
            },
            {
                "code": "hi-IN",
                "name": "Hindi (India)",
                "native_name": "हिन्दी",
                "flag": "🇮🇳"
            }
        ]
        return {'languages': languages, 'current': 'en-US'}
        
    @app.route('/api/user/set-language', methods=['POST'])
    def set_language():
        # Mock endpoint to handle language setting
        return {'success': True}
        
    @app.route('/api/speech/upload', methods=['POST'])
    def upload_audio():
        # Mock endpoint for speech upload
        return {'success': True, 'message': 'Audio received'}
    
    # Add URL rule for speech.upload_audio endpoint
    app.add_url_rule('/api/speech/upload', 'speech.upload_audio', upload_audio, methods=['POST'])
    
    # Voice transcription route is defined below
        
    # Add auth routes
    @app.route('/login')
    def login():
        return render_template('login.html')
        
    @app.route('/register')
    def register():
        return render_template('register.html')
        
    @app.route('/profile')
    def profile():
        return render_template('profile.html')
        
    @app.route('/logout')
    def logout():
        return redirect(url_for('index'))
    
    # Add FIR routes
    @app.route('/fir/new')
    def new_fir():
        return render_template('fir/new.html')
        
    @app.route('/fir/dashboard')
    def fir_dashboard():
        return render_template('fir/dashboard.html')
        
    @app.route('/voice-transcription')
    def voice_transcription():
        transcription_text = ''
        return render_template('voice_transcription.html', transcription_text=transcription_text)
        
    # Add admin routes
    @app.route('/admin/dashboard')
    def admin_dashboard():
        return render_template('admin/dashboard.html')
        
    # Add chatbot routes
    @app.route('/chatbot')
    def chatbot_interface():
        return render_template('chatbot/index.html')
        
    @app.route('/chatbot/api/query', methods=['POST'])
    def chatbot_query():
        # Get the query from the request
        data = request.get_json()
        query = data.get('query', '') if data else ''
        
        # Log the query (for debugging)
        print(f"Received chatbot query: {query}")
        
        # Mock chatbot response
        return jsonify({
            'text': f'You asked: "{query}". This is a mock response from the chatbot. The actual chatbot functionality requires the full application.',
            'data': {
                'analysis': {
                    'sections': []
                }
            }
        })
        
    # Add blueprint-like route structure
    # Auth blueprint routes
    app.add_url_rule('/login', 'auth.login', login)
    app.add_url_rule('/register', 'auth.register', register)
    app.add_url_rule('/profile', 'auth.profile', profile)
    app.add_url_rule('/logout', 'auth.logout', logout)
    
    # FIR blueprint routes
    app.add_url_rule('/', 'fir.index', index)  # Add this line for the navbar
    app.add_url_rule('/fir/new', 'fir.new_fir', new_fir)
    app.add_url_rule('/fir/dashboard', 'fir.dashboard', fir_dashboard)
    app.add_url_rule('/voice-transcription', 'fir.voice_transcription', voice_transcription)
    
    # Admin blueprint routes
    app.add_url_rule('/admin/dashboard', 'admin.dashboard', admin_dashboard)
    
    # Chatbot blueprint routes
    app.add_url_rule('/chatbot', 'chatbot.index', chatbot_interface)
    app.add_url_rule('/chatbot/api/query', 'chatbot.api_query', chatbot_query, methods=['POST'])
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)