#!/usr/bin/python2.7

from flask import Flask, render_template, request
from flask import redirect, url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from catalog_database import Base, Item, Item_adds, User

from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json',
                            'r').read())['web']['client_id']
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBsession = sessionmaker(bind=engine)
session = DBsession()


@app.route('/login')
def login():
    state = ''.join(random.choice(string.ascii_uppercase+string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('invalid login'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    print("attempting")
    try:
        # Up grade auth flow into a redentials objects
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade login'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token

    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("""Token's user ID
                                  doesn't match given id"""), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
# Check for token tampering in this statement
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("""Token's client ID doesn't
                                    match client id"""), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # check if user is already logged in as well.
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('User is connected'), 200)
        response.headers['Content-Type'] = 'application/json'

# store the access credentials for later use
    login_session['credentials'] = credentials.access_token
    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

# Get User Info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    print(data)

    login_session['username'] = data['email']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = create_user(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += """ style = "width: 300px; height: 300px; border-radius: 150px;
                -webkit-border-radius: 150px; -moz-border-radius: 150px; "> """
    flash("you are now logged in as %s" % login_session['username'])
    print (login_session)
    print ("done!")
    return output


@app.route("/gdisconnect", methods=['GET'])
def gdisconnect():
    # only disconnect a user
    at = str(login_session.get('credentials'))
# print(login_session)
    if at is None:
        response = make_response(json.dumps('Current user not connected'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
# execute token revoke method
# access_token = credentials.access_token
    url = ('https://accounts.google.com/o/oauth2/revoke?token=%s'
           % at)
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print(result)
# Attempting to revoke token with google API was not LoginSuccessful
# OPted to delete session information locally on log out
    del login_session['credentials']
    del login_session['gplus_id']
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['user_id']
    del login_session['access_token']
    del login_session['state']
    flash("You are now logged out")
    return redirect(url_for('basic'))


@app.route('/')
def basic():
    print(login_session)
    return render_template('index.html')


@app.route('/catalog', methods=['GET'])
def all_items():
    print(login_session)
    if 'username' not in login_session:
        all = session.query(Item).all()
        session.close()
        return render_template('catalog_public.html', items=all)
    else:
        all = session.query(Item).all()
        session.close()
        return render_template('catalog.html', items=all)


@app.route('/catalog/new', methods=['GET', 'POST'])
def new_item():
    if 'username' not in login_session:
        flash("User not logged in, action denied")
        return redirect(url_for('all_items'))
    if request.method == 'POST':
        if len([i for i in request.form['name'] if i.isalpha()]) == 0:
            flash("Invalid input, must contain characters please try again")
            return redirect(url_for('all_items'))
        newitem = Item(item_name=request.form['name'],
                       description=request.form['description'],
                       user_id=login_session['user_id'])
        session.add(newitem)
        session.commit()
        print(newitem.user_id, login_session['user_id'])
        flash("New Item Created")
        session.close()
        return redirect(url_for('all_items'))
    else:
        return render_template('new_item.html')


@app.route('/catalog/<int:item_id>/delete', methods=['GET', 'POST'])
def delete_item(item_id):
    if 'username' not in login_session:
        flash("User not logged in, action denied")
        return redirect(url_for('all_items'))
    if request.method == 'POST':
        item_del = session.query(Item).filter_by(id=item_id).one()
        if item_del.user_id != login_session['user_id']:
            flash("mismatched user! Action Denied!")
            return redirect(url_for('all_items'))
        session.delete(item_del)
        session.commit()
        session.close()
        return redirect(url_for('all_items'))
    else:
        item_id = item_id
        return render_template('delete_item.html', item_id=item_id)


@app.route('/catalog/<int:item_id>/edit', methods=['GET', 'POST'])
def edit_item(item_id):
    if 'username' not in login_session:
        flash("User not logged in, action denied")
        return redirect(url_for('all_items'))
    if request.method == 'POST':
        item_edit = session.query(Item).filter_by(id=item_id).one()
        print(item_edit.item_name)
        if item_edit.user_id != login_session['user_id']:
            flash("mismatched user! Action Denied!")
            return redirect(url_for('all_items'))
        if len([i for i in request.form['name'] if i.isalpha()]) == 0:
            flash("Invalid input, must contain characters please try again")
            return redirect(url_for('all_items'))
        if request.form['name']:
            item_edit.item_name = request.form['name']
        if request.form['description']:
            item_edit.description = request.form['description']
        session.add(item_edit)
        session.commit()
        session.close()
        return redirect(url_for('all_items'))
    else:
        return render_template('edit_item.html', item_id=item_id)


@app.route('/catalog/<int:item_id>/')
def view_item(item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    adds = session.query(Item_adds).filter_by(item_id=item_id).all()
    session.close()
    if 'username' not in login_session:
        return render_template('item_public.html', item=item, item_adds=adds)
    else:
        return render_template('item.html', item=item, item_adds=adds)


@app.route('/catalog/<int:item_id>/new_addition/', methods=['GET', 'POST'])
def new_item_add(item_id):
    if 'username' not in login_session:
        flash("User not logged in, action denied")
        return redirect(url_for('all_items'))
    if request.method == 'POST':
        if len([i for i in request.form['name'] if i.isalpha()]) == 0:
            flash("Invalid input, must contain characters please try again")
            return redirect(url_for('all_items'))
        newitem = Item_adds(item_add_name=request.form['name'],
                            description=request.form['description'],
                            item_id=item_id,
                            user_id=login_session['user_id'])
        session.add(newitem)
        session.commit()
        session.close()
        return redirect(url_for('view_item', item_id=item_id))
    else:
        return render_template('new_item_add.html', item_id=item_id)


@app.route('/catalog/<int:item_id>/delete/<int:item_add_id>',
           methods=['GET', 'POST'])
def delete_item_add(item_id, item_add_id):
    if 'username' not in login_session:
        flash("User not logged in, action denied")
        return redirect(url_for('all_items'))
    if request.method == 'POST':
        item_del = session.query(Item_adds).filter_by(id=item_add_id).one()
        if item_del.user_id != login_session['user_id']:
            flash("mismatched user! Action Denied!")
            return redirect(url_for('all_items'))
        session.delete(item_del)
        session.commit()
        session.close()
        return redirect(url_for('view_item', item_id=item_id))
    else:
        return render_template('delete_item_add.html',
                               item_id=item_id, item_add_id=item_add_id)


@app.route('/catalog/<int:item_id>/edit/<int:item_add_id>',
           methods=['GET', 'POST'])
def edit_item_add(item_id, item_add_id):
    if 'username' not in login_session:
        flash("User not logged in, action denied")
        return redirect(url_for('all_items'))
    if request.method == 'POST':
        item_ed = session.query(Item_adds).filter_by(id=item_add_id).one()
        if item_ed.user_id != login_session['user_id']:
            flash("mismatched user! Action Denied!")
            session.close()
            return redirect(url_for('all_items'))
        if len([i for i in request.form['name'] if i.isalpha()]) == 0:
            flash("Invalid input, must contain characters please try again")
            return redirect(url_for('all_items'))
        if request.form['name']:
            item_ed.item_add_name = request.form['name']
        if request.form['description']:
            item_ed.description = request.form['description']
        session.add(item_ed)
        session.commit()
        session.close()
        return redirect(url_for('view_item', item_id=item_id))
    else:
        return render_template('edit_item_add.html',
                               item_id=item_id, item_add_id=item_add_id)


# info for adding new user
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    session.close()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except ImportError:
        return None


def create_user(login_session):
    newUser = User(name=login_session['email'], email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    session.close()
    user = session.query(User).filter_by(email=login_session['email']).one()

    return user.id


# implementation of API JSON endpoints for usage
@app.route('/catalog/JSON')
def catalog_json():
    catalog = session.query(Item).all()
    return jsonify(it=[i.serialize for i in catalog])


@app.route('/catalog/<int:item_id>/JSON')
def items_json(item_id):
    items = session.query(Item_adds).filter_by(item_id=item_id)
    return jsonify(its=[i.serialize for i in items])


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
