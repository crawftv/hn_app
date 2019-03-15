from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

DB = SQLAlchemy()


class Comments(DB.Model):

    user_id = DB.Column(DB.String(15))
    comment_id = DB.Column(DB.BigInteger, primary_key=True)
    text = DB.Column(DB.Text)
    neg = DB.Column(DB.Float)
    neu = DB.Column(DB.Float)
    pos = DB.Column(DB.Float)
    compound = DB.Column(DB.Float)
    sentiment = DB.Column(DB.String)

    # def __repr__(self):
    #     return '<Comments {}, {}'.format(self.user_id, self.text)
