# Copyright (c) 2013 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import calendar
import json
import time

import fixtures
from oslo.config import cfg
import requests
import testtools
from testtools import matchers

from os_collect_config import collect
from os_collect_config import exc
from os_collect_config import request


META_DATA = {u'int1': 1,
             u'strfoo': u'foo',
             u'map_ab': {
                 u'a': 'apple',
                 u'b': 'banana',
             }}


class FakeResponse(dict):
    def __init__(self, text, headers=None):
        self.text = text
        self.headers = headers

    def raise_for_status(self):
        pass


class FakeRequests(object):
    exceptions = requests.exceptions

    class Session(object):
        def get(self, url):
            return FakeResponse(json.dumps(META_DATA))

        def head(self, url):
            return FakeResponse('', headers={
                'last-modified': time.strftime(
                    "%a, %d %b %Y %H:%M:%S %Z", time.gmtime())})


class FakeFailRequests(object):
    exceptions = requests.exceptions

    class Session(object):
        def get(self, url):
            raise requests.exceptions.HTTPError(403, 'Forbidden')

        def head(self, url):
            raise requests.exceptions.HTTPError(403, 'Forbidden')


class TestRequestBase(testtools.TestCase):
    def setUp(self):
        super(TestRequestBase, self).setUp()
        self.log = self.useFixture(fixtures.FakeLogger())
        collect.setup_conf()
        cfg.CONF.request.metadata_url = 'http://127.0.0.1:8000/my_metadata'


class TestRequest(TestRequestBase):

    def test_collect_request(self):
        req_collect = request.Collector(requests_impl=FakeRequests)
        self.assertIsNone(req_collect.last_modified)
        req_md = req_collect.collect()
        self.assertIsNotNone(req_collect.last_modified)
        self.assertThat(req_md, matchers.IsInstance(list))
        self.assertEqual('request', req_md[0][0])
        req_md = req_md[0][1]

        for k in ('int1', 'strfoo', 'map_ab'):
            self.assertIn(k, req_md)
            self.assertEqual(req_md[k], META_DATA[k])

        self.assertEqual('', self.log.output)

    def test_collect_request_fail(self):
        req_collect = request.Collector(requests_impl=FakeFailRequests)
        self.assertRaises(exc.RequestMetadataNotAvailable, req_collect.collect)
        self.assertIn('Forbidden', self.log.output)

    def test_collect_request_no_metadata_url(self):
        cfg.CONF.request.metadata_url = None
        req_collect = request.Collector(requests_impl=FakeRequests)
        self.assertRaises(exc.RequestMetadataNotConfigured,
                          req_collect.collect)
        self.assertIn('No metadata_url configured', self.log.output)

    def test_check_fetch_content(self):
        req_collect = request.Collector()

        now_secs = calendar.timegm(time.gmtime())
        now_str = time.strftime("%a, %d %b %Y %H:%M:%S %Z",
                                time.gmtime(now_secs))

        future_secs = calendar.timegm(time.gmtime()) + 10
        future_str = time.strftime("%a, %d %b %Y %H:%M:%S %Z",
                                   time.gmtime(future_secs))

        past_secs = calendar.timegm(time.gmtime()) - 10
        past_str = time.strftime("%a, %d %b %Y %H:%M:%S %Z",
                                 time.gmtime(past_secs))

        self.assertIsNone(req_collect.last_modified)

        # first run always collects
        self.assertEqual(
            now_secs,
            req_collect.check_fetch_content({'last-modified': now_str}))

        # second run unmodified, does not collect
        req_collect.last_modified = now_secs
        self.assertRaises(exc.RequestMetadataNotAvailable,
                          req_collect.check_fetch_content,
                          {'last-modified': now_str})

        # run with later date, collects
        self.assertEqual(
            future_secs,
            req_collect.check_fetch_content({'last-modified': future_str}))

        # run with earlier date, does not collect
        self.assertRaises(exc.RequestMetadataNotAvailable,
                          req_collect.check_fetch_content,
                          {'last-modified': past_str})

        # run no last-modified header, collects
        self.assertIsNone(req_collect.check_fetch_content({}))
