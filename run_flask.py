#!/usr/bin/env python
"""File to run flask server"""
import locale
import sys
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from shiny_api.modules.flask_helpers import LazyView
from shiny_api.modules import load_config as config

locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
app = Flask(__name__)
app.config['SECRET_KEY'] = config.FLASK_SECRET_KEY
app.template_folder = 'shiny_api/views/templates'
csrf = CSRFProtect(app)


def flask_url(import_name, url_rules=[], **options):  # pylint: disable=dangerous-default-value
    """Lazy load a view and add it to the app"""
    view = LazyView(f"shiny_api.views.{import_name}")
    for url_rule in url_rules:
        app.add_url_rule(url_rule, view_func=view, **options)


flask_url('api.workorder_label', ['/api/wo_label/'])
flask_url('api.ring_central_send_message', ['/api/rc_send_message/'])
flask_url('label_printer.label_printer_view', [
    '/label_printer/<active_label_group>',
    '/label_printer/'], methods=['GET', 'POST'])


if __name__ == "__main__":
    if len(sys.argv) == 1:
        app.debug = True
    app.run(port=8000)
