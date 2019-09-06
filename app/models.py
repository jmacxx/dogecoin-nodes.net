from app import app,db


class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    node_ip = db.Column(db.String(64))
    node_ver_org = db.Column(db.String(64))
    node_ver_new = db.Column(db.String(64))
    node_country = db.Column(db.String(4))
    node_height = db.Column(db.Integer)
    node_flags = db.Column(db.String(16))
    last_seen = db.Column(db.String(16))
    prize_txid = db.Column(db.String(80))
    prize_amount = db.Column(db.Integer)
    prize_notes = db.Column(db.String(128))

    def __repr__(self):
        return '<Inventory {}>'.format(self.node_ip)

    def needs_update(self):
        if self.node_ver_org == app.config['DOGECOIN_NODE_VERSION']:
            return False
        return True

    def has_been_updated(self):
        # if the original (snapshot) version is different to target version
        # and the new detected version equals the target version
        if self.node_ver_new == app.config['DOGECOIN_NODE_VERSION'] and self.node_ver_org != app.config['DOGECOIN_NODE_VERSION']:
            return True
        return False

    def is_current(self):
        if self.node_ver_org == app.config['DOGECOIN_NODE_VERSION'] or self.node_ver_new == app.config['DOGECOIN_NODE_VERSION']:
            return True
        return False

    def reward_claimed(self):
        if self.prize_txid is None:
            return False
        return True
