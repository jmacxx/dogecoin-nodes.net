from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from app import app, db
from app.models import Inventory
from app.forms import ClaimPrizeForm
import urllib.request
import json


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home', posts=None)


@app.route('/list-inventory')
def list_inventory():
    # we are only going to allow the ones that are in the original database list to be eligible for prize
    # this is to prevent people gaming the system by intentionally setting up new nodes with old versions
    posts = getCurrentNodeListFromWeb()
    count = 0
    for post in posts:
        count = count + 1
        post.count = count
        db_rec = db.session.query(Inventory).filter(Inventory.node_ip == post.node_ip).first()
        if db_rec is None:
            post.id = 0
        else:
            post.id = db_rec.id
    return render_template('list-inventory.html', title='List Nodes', posts=posts)


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
                i.node_ip = str(nodes_key)
                i.node_version = str(nodes[nodes_key]['version'])
                i.node_country = str(nodes[nodes_key]['country'])
                i.node_height = str(nodes[nodes_key]['height'])
                i.node_flags = str(nodes[nodes_key]['flags'])
                # only include dogecoin nodes (shibetoshi)
                if i.node_version[:12] == '/Shibetoshi:':
                    retInventory.append(i)
    return retInventory



@app.route('/item-detail/<item_id>')
def item_detail(item_id):
    inv = Inventory.query.get(item_id)
    inv.reward_amount = app.config['DOGECOIN_REWARD']
    return render_template('item-detail.html', title='Item Detail', post=inv)


@app.route('/claim/<item_id>', methods=['GET', 'POST'])
def claim(item_id):
    inv = Inventory.query.get(item_id)
    sr = request.remote_addr
    form = ClaimPrizeForm(nodeversion=inv.node_version, nodeipaddress=inv.node_ip, youripaddress=sr)
    if form.validate_on_submit():
        dogecoinaddress = form.dogecoinaddress
        # note we should obtain the user's IP address programmatically
        flash('Congratulations, you have claimed you prize of much dogecoin!')
        return redirect('/index')
    return render_template('claim.html', title='Claim', form=form, post=inv)



