from flask import Flask, request, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from .models import DB, Comments

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hn.db'
    DB.init_app(app)
    @app.route('/')
    def root():
        return "root"

    @app.route('/user_lookup/<user_id>' ,methods=['GET'])
    def user_lookup(user_id):
        
        if request.method == "GET":
            results = []
            query = DB.session.query(Comments).filter_by(user_id= user_id).limit(5).all()
            for q in query:
                result = {"user_id" : q.user_id, "text" : q.text, "neg":q.neg,"neu":q.neu, "pos":q.pos, "compound" : q.compound, "sentiment" : q.sentiment}
                results.append(result)
            

        return jsonify(results)
    return app