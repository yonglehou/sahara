# Copyright (c) 2013 Mirantis Inc.
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

import os

from oslo_concurrency import processutils
import paramiko
import six

from sahara import exceptions as ex
from sahara.i18n import _
from sahara.utils import tempfiles


def to_paramiko_private_key(pkey):
    """Convert private key (str) to paramiko-specific RSAKey object."""
    return paramiko.RSAKey(file_obj=six.StringIO(pkey))


def generate_key_pair(key_length=2048):
    """Create RSA key pair with specified number of bits in key.

    Returns tuple of private and public keys.
    """
    with tempfiles.tempdir() as tmpdir:
        keyfile = os.path.join(tmpdir, 'tempkey')
        args = [
            'ssh-keygen',
            '-q',  # quiet
            '-N', '',  # w/o passphrase
            '-t', 'rsa',  # create key of rsa type
            '-f', keyfile,  # filename of the key file
            '-C', 'Generated-by-Sahara'  # key comment
        ]
        if key_length is not None:
            args.extend(['-b', key_length])
        processutils.execute(*args)
        if not os.path.exists(keyfile):
            raise ex.SystemError(_("Private key file hasn't been created"))
        private_key = open(keyfile).read()
        public_key_path = keyfile + '.pub'
        if not os.path.exists(public_key_path):
            raise ex.SystemError(_("Public key file hasn't been created"))
        public_key = open(public_key_path).read()

        return private_key, public_key
