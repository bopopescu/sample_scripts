# Copyright (c) 2014 VMware
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

from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import sys

import testtools

import congress.utils as utils


class UtilsTest(testtools.TestCase):

    def test_value_to_congress(self):
        self.assertEqual("abc", utils.value_to_congress("abc"))
        self.assertEqual("True", utils.value_to_congress(True))
        self.assertEqual("False", utils.value_to_congress(False))
        self.assertEqual(0, utils.value_to_congress(0))
        self.assertEqual(1, utils.value_to_congress(1))
        self.assertEqual(123, utils.value_to_congress(123))
        if sys.version < '3':
            self.assertEqual(456.0, utils.value_to_congress(456.0))

    def test_pretty_rule(self):
        test_rule = "\t \n  head(1, 2)\t \n  "
        expected = "head(1, 2)"
        self.assertEqual(utils.pretty_rule(test_rule), expected)

        test_rule = "\t \n  head(1, 2)\t \n  :- \t \n"
        expected = "head(1, 2)"
        self.assertEqual(utils.pretty_rule(test_rule), expected)

        test_rule = ("\t \n server_with_bad_flavor(id)\t \n  :- \t \n  "
                     "nova:servers(id=id,flavor_id=flavor_id), \t \n "
                     "nova:flavors(id=flavor_id, name=flavor), "
                     "not permitted_flavor(flavor)\t \n ")
        expected = ("server_with_bad_flavor(id) :-\n"
                    "  nova:servers(id=id,flavor_id=flavor_id),\n"
                    "  nova:flavors(id=flavor_id, name=flavor),\n"
                    "  not permitted_flavor(flavor)")
        self.assertEqual(utils.pretty_rule(test_rule), expected)
