from flask import Flask, request, render_template, jsonify
from decouple import config
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import func
from .models import DB, Comments
import functools


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = config("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    DB.init_app(app)

    @app.route('/')
    def root():
        return "root"

    @app.route('/user_lookup/<user_id>', methods=['GET'])
    def user_lookup(user_id):

        if request.method == "GET":
            def avg_sentiment(user_id):
                query = DB.session.query(Comments).filter_by(
                    user_id=user_id).limit(500).all()
                num_results = len(query)
                compound_sentiment = functools.reduce(
                    lambda x, y: x+y, [q.compound for q in query]) / num_results

                return compound_sentiment

            def top_10_saltiest_comments(user_id):
                top_10 = DB.session.query(Comments.text, Comments.compound).filter_by(
                    user_id=user_id).order_by(Comments.compound.asc()).limit(10).all()
                return top_10

        return jsonify(user_average_sentiment=avg_sentiment(user_id), top_10=top_10_saltiest_comments(user_id))

    @app.route('/topic_sentiment/<topic>', methods=['GET'])
    def topic_sentiment(topic):

        if request.method == "GET":
            query = DB.session.query(Comments).filter(
                Comments.text.like('%'+topic+'%')).limit(2500).all()
            num_results = len(query)

            compound_sentiment = functools.reduce(
                lambda x, y: x+y, [q.compound for q in query]) / num_results
        return jsonify(compound_sentiment=compound_sentiment)

    @app.route('/saltiest_commenters', methods=["GET"])
    def saltiest_commenters():
        if request.method == "GET":
            query = DB.session.query(Comments.user_id, func.count(
                Comments.user_id), func.avg(Comments.compound)).group_by(Comments.user_id).having(func.count(Comments.user_id) > 49).order_by(func.avg(Comments.compound).asc()).limit(10).all()

        return jsonify(query)
    return app
