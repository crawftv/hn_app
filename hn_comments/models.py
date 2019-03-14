from flask_sqlalchemy import SQLAlchemy

DB = SQLAlchemy()


class Comments(DB.Model):
    
    user_id = DB.Column(DB.String(15))
    
    deleted = DB.Column(DB.Boolean)
    id = DB.Column(DB.BigInteger,primary_key=True)
    kids = DB.Column(DB.String)
    parent = DB.Column(DB.Integer)
    text = DB.Column(DB.Text)
    time = DB.Column(DB.String(10))
    neg = DB.Column(DB.Float)
    neu = DB.Column(DB.Float)
    pos = DB.Column(DB.Float)
    compound = DB.Column(DB.Float)
    sentiment = DB.Column(DB.String)

    # def __repr__(self):
    #     return '<Comments {}, {}'.format(self.user_id, self.text)
