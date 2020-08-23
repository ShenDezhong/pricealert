import json
from flask import Blueprint, render_template, request, redirect, url_for, session
from model.alert import Alert
from model.item import Item
from model.store import Store
from model.user import requires_login


alert_blueprint = Blueprint('alerts', __name__)


@alert_blueprint.route('/')
# @requires_login
def index():
    alerts = Alert.all()
    return render_template('alerts/index.html', alerts=alerts)


@alert_blueprint.route('/new', methods=['GET', 'POST'])
# @requires_login
def new_alert():
    if request.method == 'POST':
        alert_name = request.form['name']
        item_url = request.form['item_url']
        price_limit = float(request.form['price_limit'])

        store = Store.find_by_url(item_url)
        item = Item(item_url, store.tag_name, store.query)
        item.load_price()
        item.save_to_mongo()

        Alert(alert_name, item.get_item_id(), price_limit).save_to_mongo()

    return render_template('alerts/new_alert.html')


@alert_blueprint.route("/edit/<string:alert_id>", methods=["GET", "POST"])
# @requires_login
def edit_alert(alert_id):
    if request.method == "POST":
        price_limit = float(request.form["price_limit"])

        alert = Alert.get_by_id(alert_id)
        alert.price_limit = price_limit
        alert.save_to_mongo()

        return redirect(url_for(".index"))

    # What happens if it's a GET request
    return render_template("alerts/edit_alert.html", alert=Alert.get_by_id(alert_id))


@alert_blueprint.route("/delete/<string:alert_id>")
# @requires_login
def delete_alert(alert_id):
    alert = Alert.get_by_id(alert_id)
    if alert.user_email == session["email"]:
        alert.remove_from_mongo()
    return redirect(url_for(".index"))