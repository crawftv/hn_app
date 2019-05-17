from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

DB = SQLAlchemy()


class Comments(DB.Model):

    by = DB.Column(DB.String(15))
    id = DB.Column(DB.BigInteger, primary_key=True)
    text = DB.Column(DB.Text)
    time = DB.Column(DB.DateTime)
    sentiment = DB.Column(DB.String)

    # def __repr__(self):
    #     return '<Comments {}, {}'.format(self.user_id, self.text)
