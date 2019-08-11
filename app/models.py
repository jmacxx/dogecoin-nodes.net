from app import db


class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    node_ip = db.Column(db.String(64))
    node_version = db.Column(db.String(64))
    node_country = db.Column(db.String(4))
    node_height = db.Column(db.String(16))
    node_flags = db.Column(db.String(16))
    prize_txid = db.Column(db.String(80))
    prize_amount = db.Column(db.Integer)
    prize_notes = db.Column(db.String(128))

    def __repr__(self):
        return '<Inventory {}>'.format(self.node_ip)


