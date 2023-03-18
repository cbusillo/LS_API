#!/usr/bin/env python
"""File to run flask server"""

import locale

from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from flask_sse import sse
from flask_wtf.csrf import CSRFProtect

from shiny_api.modules import load_config as config
from shiny_api.modules.flask_helpers import LazyView

locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
app = Flask(__name__)
app.config['SECRET_KEY'] = config.FLASK_SECRET_KEY
app.config["REDIS_URL"] = "redis://localhost"
app.template_folder = '../views/templates'
app.debug = False
app.running_function = {}

csrf = CSRFProtect(app)

app.register_blueprint(sse, url_prefix='/ls_functions')

toolbar = DebugToolbarExtension(app)


def flask_url(import_name, url_rules=[], **options):  # pylint: disable=dangerous-default-value
    """Lazy load a view and add it to the app"""
    view = LazyView(f"shiny_api.views.{import_name}")
    for url_rule in url_rules:
        app.add_url_rule(url_rule, view_func=view, **options)


flask_url(
    'ls_functions.ls_functions_view',
    ['/ls_functions/', '/ls_functions/<module_function_name>'],
    methods=['GET', 'POST'])
flask_url('api.workorder_label', ['/api/wo_label/'])
flask_url('api.ring_central_send_message', ['/api/rc_send_message/'])
flask_url('label_printer.label_printer_view', [
    '/label_printer/<active_label_group>',
    '/label_printer/'], methods=['GET', 'POST'])


def start_flask_server():
    """Start flask server"""
    app.run(host="0.0.0.0", port=8000)
