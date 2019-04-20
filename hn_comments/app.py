from flask import Flask, request, render_template, jsonify,json
from decouple import config
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import func
from .models import DB, Comments
import numpy as np
from collections import Counter
import functools


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = config("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    DB.init_app(app)

    @app.route('/')
    def root():
        return render_template('root.html')


    @app.route('/topic', methods=['GET'])
    def topic():
        """ query the db,
        store number of results for reuse,
        make a list comprehension of the results,
        convert it to a histogram,
        use json.dumps to put it into a frontend-usable format,
        average the compound sentiment,
        pass it to the frontend.
        Or return error message.
        """

        topic = request.values["topic"]
        topic = topic.replace("_", " ")
        if request.method == "GET":
            query = DB.session.query(Comments).filter(
                Comments.text.like('%'+topic+'%')).limit(2500).all()
            num_results = len(query)
            if num_results > 0:
                sentiment = [q.sentiment for q in query]
                hist = np.histogram(sentiment, bins=10, range=(-1,1))
                data = json.dumps([int(hist[0][i])/num_results*100  for i in range(len(hist[0]))] )
                sentiment = functools.reduce(
                    lambda x, y: x+y, sentiment) / num_results
                return render_template("topic_sentiment.html",
                sentiment =sentiment, topic= topic, data = data)
            else:
                return render_template("no_results.html")
    @app.route('/user_sentiment', methods=['GET'])
    def user_sentiment():
        user_id = request.values["user_id"]
        query = DB.session.query(Comments).filter_by(
               by =user_id).limit(500).all()
        if len(query)> 0:
            def avg_sentiment(query):
                num_results = len(query)
                sentiment = functools.reduce(
                    lambda x, y: x+y, [q.sentiment for q in query]) / num_results
                sentiment = json.dumps(sentiment)
                return compound_sentiment
            def sentiment_dictionary(query):
                sentiment = [q.sentiment for q in query]
                sentiment =  Counter(sentiment)
                keys = json.dumps(list(sentiment.keys()))
                values = json.dumps(list(sentiment.values()))
                return keys, values
            #def top_10_saltiest_comments(user_id): 
            #   top_10 = DB.session.query(Comments.text, Comments.compound).filter_by(
    #                user_id=user_id).order_by(Comments.compound.asc()).limit(10).all()
     #           top_10 =json.dumps(top_10)
      #          return top_10
            keys, values = sentiment_dictionary(query)
            return render_template("user_sentiment.html",
                    user_average_sentiment=avg_sentiment(query), keys = keys,  values =
                    values, user_id=user_id)
        else:
            return render_template("no_results.html")




















    """React App funtionality"""
    @app.route('/user_lookup/<user_id>', methods=['GET'])
    def user_lookup(user_id):

        def avg_sentiment(user_id):
            query = DB.session.query(Comments).filter_by(
                by=user_id).limit(500).all()
            num_results = len(query)
            sentiment = functools.reduce(
                lambda x, y: x+y, [q.sentiment for q in query]) / num_results

            return sentiment

        def top_10_saltiest_comments(user_id): 
            top_10 = DB.session.query(Comments.text, Comments.sentiment).filter_by(
                by=user_id).order_by(Comments.compound.asc()).limit(10).all()
            return top_10

        return jsonify(user_average_sentiment=avg_sentiment(user_id), top_10=top_10_saltiest_comments(user_id))

    @app.route('/topic_sentiment/<topic>', methods=['GET'])
    def topic_sentiment(topic):
        topic = topic.replace("_", " ")
        if request.method == "GET":
            query = DB.session.query(Comments).filter(
                Comments.text.like('%'+topic+'%')).limit(2500).all()
            num_results = len(query)
            sentiment = functools.reduce(
                lambda x, y: x+y, [q.sentiment for q in query]) / num_results
        return jsonify(sentiment=sentiment)

    @app.route('/saltiest_commenters', methods=["GET"])
    def saltiest_commenters():
        if request.method == "GET":
            query = DB.session.query(Comments.sentiment, func.count(
                Comments.by),
                func.avg(Comments.sentiment)).group_by(Comments.by).having(func.count(Comments.by)
                        > 49).order_by(func.avg(Comments.sentiment).asc()).limit(10).all()

        return jsonify(query)

    return app
    #import numpy as np
    # @app.route('/topic_sentiment_chart/<topic>', methods=['GET'])
    # def topic_sentiment_chart(topic):

    #     if request.method == "GET":
    #         query = DB.session.query(Comments).filter(
    #             Comments.text.like('%'+topic+'%')).limit(2500).all()
    #         compound = [q.compound for q in query]
    #         hist = np.histogram(compound, bins=10)
    #         hist = (list(hist[0]), list(hist[1]))
    #         hist = jsonify(hist)

    #     return render_template('topic.html', hist=hist)
