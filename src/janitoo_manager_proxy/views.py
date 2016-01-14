# -*- coding: utf-8 -*-

"""The proxy views
"""

__license__ = """

This file is part of **janitoo** project https://github.com/bibi21000/janitoo.

License : GPL(v3)

**janitoo** is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

**janitoo** is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with janitoo. If not, see http://www.gnu.org/licenses.
"""
__author__ = 'Sébastien GALLET aka bibi21000'
__email__ = 'bibi21000@gmail.com'
#~ from gevent import monkey
#~ monkey.patch_all()

import logging
logger = logging.getLogger(__name__)

import os, sys
import time
from threading import Thread
import httplib
import re
import urllib
import urlparse
import json

from flask import Blueprint, flash
from flask import Flask, session, request, current_app, g
from flask import Response, url_for
from werkzeug.datastructures import Headers
from werkzeug.exceptions import NotFound
from flask_themes2 import get_themes_list
from flask_babelex import gettext as _

from janitoo_manager.extensions import babel, janitoo
from janitoo_manager.utils.helpers import render_template

#~ from flask import Flask, render_template, session, request, current_app, g
#~ from flask.ext.socketio import SocketIO, emit, join_room, leave_room, close_room, disconnect
#~ from flask import Response, url_for
#~ from werkzeug.datastructures import Headers
#~ from werkzeug.exceptions import NotFound
#~
#~ from janitoo_web.app import socketio, app, sort_application_entries, sorted_application_entries
#~ from janitoo_web.app.listener import listener

#~ app.extensions['application_entries']['/proxy'] = { 'order':99, 'label':'Proxy'}
#~ app.extensions['sorted_application_entries'] = sort_application_entries(app.extensions['application_entries'])

# You can insert Authentication here.
#proxy.before_request(check_login)

# Filters.
HTML_REGEX = re.compile(r'((?:src|action|href)=["\'])/')
JQUERY_REGEX = re.compile(r'(\$\.(?:get|post)\(["\'])/')
JS_LOCATION_REGEX = re.compile(r'((?:window|document)\.location.*=.*["\'])/')
CSS_REGEX = re.compile(r'(url\(["\']?)/')

REGEXES = [HTML_REGEX, JQUERY_REGEX, JS_LOCATION_REGEX, CSS_REGEX]

def get_blueprint():
    return proxy, "/proxy"

def get_leftmenu():
    return "<a href='/proxy/'>Proxy</a>"

def iterform(multidict):
    for key in multidict.keys():
        for value in multidict.getlist(key):
            yield (key.encode("utf8"), value.encode("utf8"))

def parse_host_port(h):
    """Parses strings in the form host[:port]"""
    host_port = h.split(":", 1)
    if len(host_port) == 1:
        return (h, 80)
    else:
        host_port[1] = int(host_port[1])
        return host_port

proxy = Blueprint("proxy", __name__, template_folder='templates', static_folder='static')

@proxy.route('')
@proxy.route('/')
def index():
    network=janitoo.listener.network
    web_servers=network.find_webcontrollers()
    web_resources=network.find_webresources()
    return render_template('proxy/index.html', web_servers=web_servers, web_resources=web_resources)

@proxy.route('/<string:host>', methods=["GET", "POST", "PUT", "DELETE"])
@proxy.route('/<string:host>/', methods=["GET", "POST", "PUT", "DELETE"])
@proxy.route('/<string:host>/<path:file>', methods=["GET", "POST", "PUT", "DELETE"])
def proxy_request(host, file=""):
    hostname, port = parse_host_port(host)

    #~ print "H: '%s' P: %d" % (hostname, port)
    #~ print "F: '%s'" % (file)
    # Whitelist a few headers to pass on
    request_headers = {}
    for h in ["Cookie", "Referer", "X-Csrf-Token"]:
        if h in request.headers:
            request_headers[h] = request.headers[h]

    if request.query_string:
        path = "/%s?%s" % (file, request.query_string)
    else:
        path = "/" + file

    if request.method == "POST" or request.method == "PUT":
        form_data = list(iterform(request.form))
        form_data = urllib.urlencode(form_data)
        request_headers["Content-Length"] = len(form_data)
    else:
        form_data = None

    conn = httplib.HTTPConnection(hostname, port)
    conn.request(request.method, path, body=form_data, headers=request_headers)
    resp = conn.getresponse()

    # Clean up response headers for forwarding
    d = {}
    response_headers = Headers()
    for key, value in resp.getheaders():
        print "HEADER: '%s':'%s'" % (key, value)
        d[key.lower()] = value
        if key in ["content-length", "connection", "content-type"]:
            continue

        if key == "set-cookie":
            cookies = value.split(",")
            [response_headers.add(key, c) for c in cookies]
        else:
            response_headers.add(key, value)

    # If this is a redirect, munge the Location URL
    if "location" in response_headers:
        redirect = response_headers["location"]
        parsed = urlparse.urlparse(request.url)
        redirect_parsed = urlparse.urlparse(redirect)

        redirect_host = redirect_parsed.netloc
        if not redirect_host:
            redirect_host = "%s:%d" % (hostname, port)

        redirect_path = redirect_parsed.path
        if redirect_parsed.query:
            redirect_path += "?" + redirect_parsed.query

        munged_path = url_for(".proxy_request",
                              host=redirect_host,
                              file=redirect_path[1:])

        url = "%s://%s%s" % (parsed.scheme, parsed.netloc, munged_path)
        response_headers["location"] = url

    # Rewrite URLs in the content to point to our URL schemt.method == " instead.
    # Ugly, but seems to mostly work.
    root = url_for(".proxy_request", host=host)
    contents = resp.read()

    #~ print root
    #~ print contents
    # Restructing Contents.
    if d["content-type"].find("application/json") >= 0:
        # JSON format conentens will be modified here.
        jc = json.loads(contents)
        if jc.has_key("nodes"):
            del jc["nodes"]
        contents = json.dumps(jc)

    else:
        # Generic HTTP.
        for regex in REGEXES:
           contents = regex.sub(r'\1%s' % root, contents)

    #~ print contents
    flask_response = Response(response=contents,
                              status=resp.status,
                              headers=response_headers,
                              content_type=resp.getheader('content-type'))
    return flask_response

