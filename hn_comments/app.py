from flask import Flask, request, render_template, jsonify, json
from decouple import config
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import func
from models import DB, Comments
import numpy as np
from collections import Counter
import functools
from datetime import datetime
import itertools


app = Flask(__name__)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = config("AWS_DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

DB.init_app(app)


@app.route("/")
def root():
    return render_template("root.html")


@app.route("/topic", methods=["GET"])
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
        query = (
            DB.session.query(Comments)
            .filter(Comments.text.like("%" + topic + "%"))
            .limit(2500)
            .all()
        )
        num_results = len(query)
        if num_results > 0:
            sentiment = [q.sentiment for q in query]
            hist = np.histogram(sentiment, bins=10, range=(-1, 1))
            data = json.dumps(
                [int(hist[0][i]) / num_results * 100 for i in range(len(hist[0]))]
            )
            sentiment = functools.reduce(lambda x, y: x + y, sentiment) / num_results
            return render_template(
                "topic_sentiment.html", sentiment=sentiment, topic=topic, data=data
            )
        else:
            return render_template("no_results.html")


@app.route("/user_sentiment", methods=["GET"])
def user_sentiment():
    user_id = request.values["user_id"]
    if request.method == "GET":
        query = DB.session.query(Comments).filter_by(by=user_id).limit(2500).all()
        num_results = len(query)
        if num_results > 0:
            user_average_sentiment = avg_sentiment(query, num_results)
            data = sentiment_histogram(query, num_results)

            return render_template(
                "user_sentiment.html",
                user_average_sentiment=user_average_sentiment,
                user_id=user_id,
                data=data,
            )
        else:
            return render_template("no_results.html")


@app.route("/topic-timeline/", methods=["POST"])
def topic_timeline():
    topic = request.values["topic"]
    data, labels = line_chart(topic)
    return render_template("linechart.html", data=data, labels=labels, topic=topic)


def avg_sentiment(query, num_results):
    avg_sentiment = (
        functools.reduce(lambda x, y: x + y, [q.sentiment for q in query]) / num_results
    )
    avg_sentiment = json.dumps(avg_sentiment)
    return avg_sentiment


def sentiment_histogram(query, num_results):
    sentiment = [q.sentiment for q in query]
    hist = np.histogram(sentiment, bins=10, range=(-1, 1))
    # converts histogram results to %'s
    hist = json.dumps(
        [int(hist[0][i]) / num_results * 100 for i in range(len(hist[0]))]
    )
    return hist


def line_chart(search):

    query = (
        DB.session.query(Comments)
        .filter(Comments.text.like("%" + search + "%"))
        .order_by(Comments.time.asc())
        .all()
    )
    if len(query) > 0:

        def get_date(ts):
            return datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d")

        query = [(get_date(int(q.time)), float(q.sentiment)) for q in query]
        y = [
            (key, list(num for _, num in value))
            for key, value in itertools.groupby(query, lambda x: x[0])
        ]

        def avg(lst):
            return sum(lst) / len(lst)

        labels = [y[i][0] for i in range(len(y))]
        data = [avg(y[i][1]) for i in range(len(y))]
        labels = json.dumps(labels)
        data = json.dumps(data)
        return data, labels


# def top_10_saltiest_comments(user_id):
#   top_10 = DB.session.query(Comments.text, Comments.compound).filter_by(
#                user_id=user_id).order_by(Comments.compound.asc()).limit(10).all()
#           top_10 =json.dumps(top_10)
#          return top_10
"""React App funtionality"""


@app.route("/user_lookup/<user_id>", methods=["GET"])
def user_lookup(user_id):
    def avg_sentiment(user_id):
        query = DB.session.query(Comments).filter_by(by=user_id).limit(500).all()
        num_results = len(query)
        sentiment = (
            functools.reduce(lambda x, y: x + y, [q.sentiment for q in query])
            / num_results
        )

        return sentiment

    def top_10_saltiest_comments(user_id):
        top_10 = (
            DB.session.query(Comments.text, Comments.sentiment)
            .filter_by(by=user_id)
            .order_by(Comments.compound.asc())
            .limit(10)
            .all()
        )
        return top_10

    return jsonify(
        user_average_sentiment=avg_sentiment(user_id),
        top_10=top_10_saltiest_comments(user_id),
    )


@app.route("/topic_sentiment/<topic>", methods=["GET"])
def topic_sentiment(topic):
    topic = topic.replace("_", " ")
    if request.method == "GET":
        query = (
            DB.session.query(Comments)
            .filter(Comments.text.like("%" + topic + "%"))
            .limit(2500)
            .all()
        )
        num_results = len(query)
        sentiment = (
            functools.reduce(lambda x, y: x + y, [q.sentiment for q in query])
            / num_results
        )
    return jsonify(sentiment=sentiment)


@app.route("/saltiest_commenters", methods=["GET"])
def saltiest_commenters():
    if request.method == "GET":
        query = (
            DB.session.query(
                Comments.sentiment,
                func.count(Comments.by),
                func.avg(Comments.sentiment),
            )
            .group_by(Comments.by)
            .having(func.count(Comments.by) > 49)
            .order_by(func.avg(Comments.sentiment).asc())
            .limit(10)
            .all()
        )

    return jsonify(query)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
# import numpy as np
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
