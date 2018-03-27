# -*- coding:utf8 -*-
# !/usr/bin/env python
# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os
import sportslive
from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)

SL = sportslive.SportsLive()

@app.route('/news-reader', methods=['GET'])
def newsreader():
    """Given an query, return that news."""
    query = request.args.get('query')
    if query is None:
      return 'No provided.', 400
    result = SL.news_check(query)
    if result is None:
      return 'not found : %s' % query, 400
    return result, 200


@app.route('/debug/news-reader', methods=['GET'])
def newsreader_debug():
    """Given an query, return that news debug mode."""
    query = request.args.get('query')
    if query is None:
      return 'No provided.', 400
    result = SL.news_check(query, debug=True)
    if result is None:
      return 'not found : %s' % query, 400
    return result, 200

    return {
        "speech": speech,
        "displayText": speech,
        "source": "apiai-crypt"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
