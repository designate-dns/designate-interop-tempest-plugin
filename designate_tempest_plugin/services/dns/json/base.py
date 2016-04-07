# Copyright 2016 Hewlett Packard Enterprise Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import functools

from oslo_log import log as logging
from oslo_serialization import jsonutils as json
from tempest.lib.common import rest_client
from six.moves.urllib import parse as urllib


LOG = logging.getLogger(__name__)


def handle_errors(f):
    """A decorator that allows to ignore certain types of errors."""

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        param_name = 'ignore_errors'
        ignored_errors = kwargs.get(param_name, tuple())

        if param_name in kwargs:
            del kwargs[param_name]

        try:
            return f(*args, **kwargs)
        except ignored_errors as e:
            # Silently ignore errors as requested
            LOG.debug('Ignoring exception of type %s, as requested', type(e))

    return wrapper


class DnsClientBase(rest_client.RestClient):
    """Base Tempest REST client for Designate API"""

    uri_prefix = ''

    def serialize(self, object_dict):
        return json.dumps(object_dict)

    def deserialize(self, object_str):
        return json.loads(object_str)

    def _get_uri(self, resource_name, uuid=None, params=None):
        """Get URI for a specific resource or object.
        :param resource_name: The name of the REST resource, e.g., 'zones'.
        :param uuid: The unique identifier of an object in UUID format.
        :param params: A Python dict that represents the query paramaters to
                       include in the request URI.
        :returns: Relative URI for the resource or object.
        """
        uri_pattern = '{pref}/{res}{uuid}{params}'

        uuid = '/%s' % uuid if uuid else ''
        params = '?%s' % urllib.urlencode(params) if params else ''

        return uri_pattern.format(pref=self.uri_prefix,
                                  res=resource_name,
                                  uuid=uuid,
                                  params=params)

    def _create_request(self, resource, object_dict, params=None):
        """Create an object of the specified type.
        :param resource: The name of the REST resource, e.g., 'zones'.
        :param object_dict: A Python dict that represents an object of the
                            specified type.
        :param params: A Python dict that represents the query paramaters to
                       include in the request URI.
        :returns: A tuple with the server response and the deserialized created
                 object.
        """
        body = self.serialize(object_dict)
        uri = self._get_uri(resource, params=params)

        resp, body = self.post(uri, body=body)
        self.expected_success([201, 202], resp['status'])

        return resp, self.deserialize(body)

    def _show_request(self, resource, uuid, params=None):
        """Gets a specific object of the specified type.
        :param uuid: Unique identifier of the object in UUID format.
        :param params: A Python dict that represents the query paramaters to
                       include in the request URI.
        :returns: Serialized object as a dictionary.
        """
        uri = self._get_uri(resource, uuid=uuid, params=params)

        resp, body = self.get(uri)

        self.expected_success(200, resp['status'])

        return resp, self.deserialize(body)

    def _delete_request(self, resource, uuid, params=None):
        """Delete specified object.
        :param resource: The name of the REST resource, e.g., 'zones'.
        :param uuid: The unique identifier of an object in UUID format.
        :param params: A Python dict that represents the query paramaters to
                       include in the request URI.
        :returns: A tuple with the server response and the response body.
        """
        uri = self._get_uri(resource, uuid=uuid, params=params)

        resp, body = self.delete(uri)
        self.expected_success([202, 204], resp['status'])
        return resp, self.deserialize(body)
