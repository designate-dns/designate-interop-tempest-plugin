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

import time

from oslo_log import log as logging
from tempest.lib.common.utils import misc as misc_utils
from tempest.lib import exceptions as lib_exc

LOG = logging.getLogger(__name__)


def wait_for_zone_404(client, zone_id):
    """Waits for a zone to 404."""
    LOG.info('Waiting for zone %s to 404', zone_id)
    start = int(time.time())

    while True:
        time.sleep(client.build_interval)

        try:
            _, zone = client.show_zone(zone_id)
        except lib_exc.NotFound:
            LOG.info('Zone %s is 404ing', zone_id)
            return

        if int(time.time()) - start >= client.build_timeout:
            message = ('Zone %(zone_id)s failed to 404 within the required '
                       'time (%(timeout)s s). Current status: '
                       '%(status_curr)s' %
                       {'zone_id': zone_id,
                        'status_curr': zone['status'],
                        'timeout': client.build_timeout})

            caller = misc_utils.find_test_caller()

            if caller:
                message = '(%s) %s' % (caller, message)

            raise lib_exc.TimeoutException(message)


def wait_for_zone_status(client, zone_id, status):
    """Waits for a zone to reach given status."""
    LOG.info('Waiting for zone %s to reach %s', zone_id, status)

    _, zone = client.show_zone(zone_id)
    start = int(time.time())

    while zone['status'] != status:
        time.sleep(client.build_interval)
        _, zone = client.show_zone(zone_id)
        status_curr = zone['status']
        if status_curr == status:
            LOG.info('Zone %s reached %s', zone_id, status)
            return

        if int(time.time()) - start >= client.build_timeout:
            message = ('Zone %(zone_id)s failed to reach status=%(status)s '
                       'within the required time (%(timeout)s s). Current '
                       'status: %(status_curr)s' %
                       {'zone_id': zone_id,
                        'status': status,
                        'status_curr': status_curr,
                        'timeout': client.build_timeout})

            caller = misc_utils.find_test_caller()

            if caller:
                message = '(%s) %s' % (caller, message)

            raise lib_exc.TimeoutException(message)