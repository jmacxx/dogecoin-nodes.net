from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from app import app, db
from app.models import Inventory
from app.forms import ClaimPrizeForm
import urllib.request
import json
from datetime import datetime


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home', reward_amount=current_dogecoin_reward())


@app.route('/list-inventory')
def list_inventory():
    # we are only going to allow the ones that are in the original database list to be eligible for prize
    # this is to prevent people gaming the system by intentionally setting up new nodes with old versions
    filter = request.args.get('filter')
    country = request.args.get('country')
    invRecords = Inventory.query.all()
    dispRecords = []
    count = 0
    for post in invRecords:
        if post.has_been_updated():
            post.status_text = "VERY UPGRADED!"
            if filter is not None and filter != "very-upgraded":
                continue
        elif post.needs_update():
            post.status_text = "SUCH UPGRADE NEEDED"
            if filter is not None and filter != "such-upgrade-needed":
                continue
        else:
            post.status_text = "SO CURRENT"
            if filter is not None and filter != "so-current":
                continue
        if country is not None and country != post.node_country:
            continue
        count = count + 1
        post.count = count
        dispRecords.append(post)
    countries = get_countries()
    return render_template('list-inventory.html', title='List Nodes', posts=dispRecords, countries=countries, reward_amount=current_dogecoin_reward())


@app.route('/init-db')
def init_db():
    # one-time database initialization
    # populate the database only if it is empty
    invRecords = Inventory.query.all()
    if len(invRecords) == 0:
        invRecords = getCurrentNodeListFromWeb()
        for i in invRecords:
            db.session.add(i)
        db.session.commit()
    return redirect('/index')


#this refreshes our original snapshot records with new information,
# such as the latest version number and the last_seen timestamp
# NB: it intentionally does not add new records to the snapshot
@app.route('/refresh-db')
def refresh_db():
    db_list = db.session.query(Inventory).all()
    posts = getCurrentNodeListFromWeb()
    for db_rec in db_list:
        for new_rec in posts:
            if new_rec.node_ip == db_rec.node_ip:
                db_rec.last_seen = new_rec.last_seen
                db_rec.node_ver_new = new_rec.node_ver_org
                break
    db.session.commit()  # write the changed fields to the database
    return redirect('/index')


@app.route('/item-detail/<item_id>')
def item_detail(item_id):
    inv = Inventory.query.get(item_id)
    inv.reward_amount = app.config['DOGECOIN_REWARD']
    return render_template('item-detail.html', title='Item Detail', post=inv, reward_amount=current_dogecoin_reward())


@app.route('/claim/<item_id>', methods=['GET', 'POST'])
def claim(item_id):
    inv = Inventory.query.get(item_id)
    sr = request.remote_addr
    node_ver_new = inv.node_ver_new
    if node_ver_new == None:
        node_ver_new = "Please upgrade!"
    if inv.reward_claimed():            # don't let them claim more than once!
        flash("Reward for that node has already been claimed!")
        return redirect('/index')
    form = ClaimPrizeForm(nodeversionorg=inv.node_ver_org, nodeversionnew=node_ver_new, nodeipaddress=inv.node_ip, youripaddress=sr)
    if form.validate_on_submit():
        dogecoinaddress = form.dogecoinaddress
        inv = send_prize(inv, dogecoinaddress)
        return render_template('broadcast.html', title='Broadcast', prize_amount=inv.prize_amount,
                               prize_txid=inv.prize_txid)
    return render_template('claim.html', title='Claim', form=form, post=inv, reward_amount=current_dogecoin_reward())


def send_prize(inv, dogecoinaddress):
    # create a transaction to send some doge to dogecoinaddress
    # broadcast it and get the txid
    # save the txid in the Inventory record
    inv.prize_amount = 1234
    inv.prize_txid = '23487623498762349872364823469823746928346239874629387'
    db.session.commit()  # write the changed fields to the database
    return inv


# utility routines
def getCurrentNodeListFromWeb():
    retInventory = list()
    response = urllib.request.urlopen('https://api.blockchair.com/dogecoin/nodes')
    json_nodes = json.loads(response.read().decode('utf-8'))
    for key in json_nodes:
        value = json_nodes[key]
        if key == 'data':
            nodes = value['nodes']
            for nodes_key in nodes:
                i = Inventory()
                i.node_ip = normalise_ip_strip_port(str(nodes_key))
                i.node_ver_org = str(nodes[nodes_key]['version'])
                i.node_country = str(nodes[nodes_key]['country'])
                i.node_height = nodes[nodes_key]['height']
                i.node_flags = str(nodes[nodes_key]['flags'])
                i.last_seen = datetime.utcnow().strftime("%Y-%m-%d %H:%M")+" UTC"
                # only include dogecoin nodes (shibetoshi)
                if i.node_ver_org[:12] == '/Shibetoshi:' and i.node_height > 0:
                    retInventory.append(i)
    return retInventory

def normalise_ip_strip_port(in_ip):
    # the last : and digits are the port, strip it off
    port_start = in_ip.rfind(':')
    retVal = in_ip[0:port_start]  # remove the port designator from
    return retVal

def current_dogecoin_reward():
    return app.config['DOGECOIN_REWARD']

def get_countries():
    retVal = []
    for value in db.session.query(Inventory.node_country).distinct():
        retVal.append(value.node_country)
    return retVal
