from .routes import Flask,clipit_bp,jsonify,get_bp,request,abort,send_from_directory,CORS
def abstract_clip_app():
    app = Flask(__name__)
    CORS(app)

    # Register blueprint
    app.register_blueprint(clipit_bp)

    # Serve the HTML at “/” if localhost, else 403
    @app.route('/', methods=['GET'])
    def index():
        remote = request.remote_addr
        if remote not in ('127.0.0.1', '::1'):
            abort(403)

        html_dir = os.path.join(os.path.dirname(__file__), 'html')
        return send_from_directory(html_dir, 'drop-n-copy.html')

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return {'error': 'Not found'}, 404

    @app.errorhandler(403)
    def forbidden(e):
        return {'error': 'Forbidden'}, 403

    return app
