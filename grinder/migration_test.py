# Copyright 2013 GridCentric Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from novaclient.exceptions import ClientException
import py.test

from . import harness
from . logger import log
from . util import assert_raises
from . host import Host

class TestMigration(harness.TestCase):

    @harness.platformtest(exclude=["windows"])
    def test_migration_one(self, image_finder):
        if self.harness.config.skip_migration_tests:
            py.test.skip('Skipping migration tests')
        if len(self.harness.config.hosts) < 2:
            py.test.skip('Need at least 2 hosts to do migration.')
        with self.harness.booted(image_finder) as master:
            host = master.get_host()
            dest = Host([h for h in self.config.hosts if h != host.id][0], self.harness.config)
            assert host.id != dest.id
            master.migrate(host, dest)

    @harness.platformtest(exclude=["windows"])
    def test_migration_errors(self, image_finder):
        if self.harness.config.skip_migration_tests:
            py.test.skip('Skipping migration tests')
        if len(self.harness.config.hosts_without_gridcentric) == 0:
            py.test.skip('Need at least one host without gridcentric to test for migration errors.')
        with self.harness.booted(image_finder) as master:
            host = master.get_host()

            def fail_migrate(dest):
                log.info('Expecting Migration %s to %s to fail', str(master.id), dest)
                master.breadcrumbs.add('pre expected fail migration to %s' % dest.id)
                e = assert_raises(ClientException,
                                  master.migrate,
                                  host, dest)
                assert e.code / 100 == 4 or e.code / 100 == 5
                master.assert_alive(host)
                master.breadcrumbs.add('post expected fail migration to %s' % dest.id)

            # Destination does not exist.
            fail_migrate(Host('this-host-does-not-exist', self.harness.config))

            # Destination does not have gridcentric.
            dest = Host(self.config.hosts_without_gridcentric[0], self.harness.config)
            fail_migrate(dest)

            # Cannot migrate to self.
            fail_migrate(host)

    @harness.platformtest(exclude=["windows"])
    def test_back_and_forth(self, image_finder):
        if self.harness.config.skip_migration_tests:
            py.test.skip('Skipping migration tests')
        if len(self.harness.config.hosts) < 2:
            py.test.skip('Need at least 2 hosts to do migration.')
        with self.harness.booted(image_finder) as master:
            host = master.get_host()
            dest = Host([h for h in self.config.hosts if h != host.id][0], self.harness.config)
            assert host.id != dest.id
            master.migrate(host, dest)
            master.migrate(dest, host)
            master.migrate(host, dest)
            master.migrate(dest, host)
