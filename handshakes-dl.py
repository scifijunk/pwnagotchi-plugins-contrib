import logging
import json
import os
import glob

import pwnagotchi
import pwnagotchi.plugins as plugins

from flask import abort, send_from_directory, render_template_string

TEMPLATE = """
{% extends "base.html" %}
{% set active_page = "handshakes" %}

{% block title %}
    {{ title }}
{% endblock %}

{% block styles %}
    {{ super() }}
    <style>
        #filter {
            width: 100%;
            font-size: 16px;
            padding: 12px 20px 12px 40px;
            border: 1px solid #ddd;
            margin-bottom: 12px;
        }
    </style>
{% endblock %}
{% block script %}
    var shakeList = document.getElementById('list');
    var filter = document.getElementById('filter');
    var filterVal = filter.value.toUpperCase();

    filter.onkeyup = function() {
        document.body.style.cursor = 'progress';
        var li = shakeList.getElementsByTagName("li");
        for (var i = 0; i < li.length; i++) {
            var txtValue = li[i].textContent || li[i].innerText;
            if (txtValue.toUpperCase().indexOf(filterVal) > -1) {
                li[i].style.display = "list-item";
            } else {
                li[i].style.display = "none";
            }
        }
        document.body.style.cursor = 'default';
    }
{% endblock %}

{% block content %}
    <input type="text" id="filter" placeholder="Search for ..." title="Type in a filter">
    <ul id="list" data-role="listview" style="list-style-type:disc;">
        {% for handshake in handshakes %}
            <li class="file">
                <a href="/plugins/handshakes-dl/{{ handshake }}">{{ handshake }}</a>
            </li>
        {% endfor %}
    </ul>
{% endblock %}
"""

class HandshakesDL(plugins.Plugin):
    __author__ = 'me@sayakb.com'
    __version__ = '0.2.1'
    __license__ = 'GPL3'
    __description__ = 'Download handshake captures from web-ui.'

    def __init__(self):
        self.ready = False

    def on_loaded(self):
        logging.info("HandshakesDL plugin loaded")

    def on_config_changed(self, config):
        self.config = config
        self.ready = True

    def on_webhook(self, path, request):
        if not self.ready:
            return "Plugin not ready"

        if path == "/" or not path:
            handshakes = glob.glob(os.path.join("/home/pi", "*.pcap"))
            handshakes = [os.path.basename(handshake) for handshake in handshakes]
            return render_template_string(TEMPLATE,
                                          title="Handshakes | " + pwnagotchi.name(),
                                          handshakes=handshakes)
        else:
            directory = "/home/pi"
            try:
                file_path = os.path.join(directory, path)
                logging.info(f"[HandshakesDL] serving {file_path}")
                return send_from_directory(directory=directory, filename=path, as_attachment=True)
            except FileNotFoundError:
                logging.error("File not found")
                abort(404)
            except Exception as e:
                logging.error(f"Error: {e}")
                abort(500)
