# Copyright 2025 West University of Timisoara
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

import asyncio
import datetime
import os
import re
import threading
import xml.etree.ElementTree as ET
from urllib.parse import urlencode
from urllib.parse import urlparse

import backoff
import requests
import s3fs
from authlib.integrations.requests_client import OAuth2Session
from dateutil import parser as date_parser

from eocube.integrations.auth import ROCS_DEFAULT_STORAGE_ENDPOINT, ROCS_DISCOVERY_URL

MAX_RETRY_TIME = 200


def is_transient_error(e):
    if isinstance(e, requests.exceptions.HTTPError):
        status = e.response.status_code
        return status == 429 or (500 <= status < 600)
    return True  # Dacă e un alt `RequestException`, probabil e de retry


@backoff.on_exception(
    backoff.expo,
    (requests.exceptions.RequestException, requests.exceptions.HTTPError),
    max_time=MAX_RETRY_TIME,
    jitter="full",
    giveup=lambda e: not is_transient_error(e),
)
def fetch_token_with_backoff(
    client: OAuth2Session, url: str, grant_type="client_credentials"
):
    return client.fetch_token(url=url, grant_type=grant_type)


@backoff.on_exception(
    backoff.expo,
    requests.exceptions.RequestException,
    max_time=MAX_RETRY_TIME,
    jitter="full",
)
def do_requests_get(*args, **kwargs):
    return requests.get(*args, **kwargs)


@backoff.on_exception(
    backoff.expo,
    requests.exceptions.RequestException,
    max_time=MAX_RETRY_TIME,
    jitter="full",
)
def do_requests_post(*args, **kwargs):
    return requests.post(*args, **kwargs)


class StorageCredentials(object):
    def __init__(
        self,
        endpoint,
        access_key,
        secret_key,
        session_token,
        expiration: datetime.datetime,
        leeway=300,
    ):
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self.session_token = session_token
        self.expiration: datetime.datetime = expiration
        self.leeway = leeway

    def is_expired(self):
        """
        Checks whether the current token is expired based on the expiration time
        and a specified leeway.

        This method calculates the difference in seconds between the expiration time
        and the current time, adjusted for the UTC timezone. If the difference is less
        than the permissible leeway, the instance is considered expired.

        :return: Returns True if the instance is expired, otherwise False.
        :rtype: bool
        """
        now = datetime.datetime.now(datetime.timezone.utc)
        expiration = self.expiration
        diff = expiration.timestamp() - now.timestamp()
        if diff < self.leeway:
            return True
        else:
            return False


class AuthClient(object):
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        scope: list = ["openid", "email", "profile", "eocube-object-storage"],
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope
        self.metadata = do_requests_get(ROCS_DISCOVERY_URL).json()
        self.token_endpoint = self.metadata["token_endpoint"]
        self._token_lock = threading.Lock()
        self._storage_tokens = {}
        self._storage_tokens_lock = threading.Lock()

        self.client = OAuth2Session(
            client_id=client_id, client_secret=client_secret, scope=scope
        )

        self._token = None

    @property
    def token(self):
        if self._token is None or self._token.is_expired():
            with self._token_lock:
                self._token = fetch_token_with_backoff(
                    self.client,
                    url=self.token_endpoint,
                    grant_type="client_credentials",
                )
        return self._token

    def _credentials_are_valid(self, endpoint):
        if (
            endpoint not in self._storage_tokens
            or self._storage_tokens[endpoint].is_expired()
        ):
            return False
        else:
            return True

    def get_storage_fs(self, credentials: StorageCredentials = None):
        """Returns a fsspec filesystem for the configured credentials"""
        if credentials is None:
            credentials = self.get_storage_credentials()
        fs = s3fs.S3FileSystem(
            key=credentials.access_key,
            secret=credentials.secret_key,
            token=credentials.session_token,
            endpoint_url=credentials.endpoint,
        )
        return fs

    def get_storage_credentials(
        self, endpoint: str = None, duration_seconds: int = 3600, policy: str = None
    ):
        """
        Retrieves temporary storage credentials for a given endpoint. The credentials
        allow access to the specified storage service for a limited duration. This
        function enables fine-grained access control to the storage by optionally
        providing a policy that defines the access permissions.

        :param endpoint: The URL of the storage endpoint for which the credentials
            will be generated. If not specified, the default endpoint will be used.
        :type endpoint: str
        :param duration_seconds: The duration for which the temporary credentials
            remain valid, in seconds. If not specified, the default duration is 3600
            seconds (1 hour).
        :type duration_seconds: int
        :param policy: URL-encoded JSON-formatted policy to use as an inline session policy.
            If not provided, the policy in the JWT token will be used.
        :type policy: str
        :return: A dictionary containing the temporary credentials, including access
            keys, secret keys, and any other relevant details required to access the
            storage service.
        :rtype: dict
        """

        if endpoint is None:
            endpoint = ROCS_DEFAULT_STORAGE_ENDPOINT
        if not self._credentials_are_valid(
            endpoint
        ):  # We don't have a valid token for this endpoint
            with self._storage_tokens_lock:
                if not self._credentials_are_valid(
                    endpoint
                ):  # Double check -- due to potential concurency
                    creds = self._get_storage_credentials_using_token(
                        endpoint=endpoint,
                        token=self.token,
                        duration_seconds=duration_seconds,
                        policy=policy,
                    )
                    self._storage_tokens[endpoint] = creds
        return self._storage_tokens[endpoint]

    def _get_storage_credentials_using_access_token(
        self,
        endpoint: str,
        token: str,
        duration_seconds: int = 3600,
        policy: str = None,
    ):
        params = {
            "Action": "AssumeRoleWithWebIdentity",
            "Version": "2011-06-15",
            "WebIdentityToken": token,
            "DurationSeconds": duration_seconds,
        }

        if policy is not None:
            params["Policy"] = policy

        response = do_requests_post(
            endpoint,
            data=urlencode(params),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        root = ET.fromstring(response.text)
        ns = {"ns": "https://sts.amazonaws.com/doc/2011-06-15/"}
        creds = root.find(".//ns:Credentials", ns)
        if creds is None:
            raise Exception("Could not parse credentials from response")

        expiration_str = creds.find("ns:Expiration", ns).text
        expiration_dt = date_parser.parse(expiration_str)

        return StorageCredentials(
            endpoint=endpoint,
            access_key=creds.find("ns:AccessKeyId", ns).text,
            secret_key=creds.find("ns:SecretAccessKey", ns).text,
            session_token=creds.find("ns:SessionToken", ns).text,
            expiration=expiration_dt,
            leeway=300,
        )

    def _get_storage_credentials_using_token(
        self,
        endpoint: str,
        token: str,
        duration_seconds: int = 3600,
        policy: str = None,
    ):
        access_token = token["access_token"]
        return self._get_storage_credentials_using_access_token(
            endpoint=endpoint,
            token=access_token,
            duration_seconds=duration_seconds,
            policy=policy,
        )


def discover_client_token():
    client_id = os.environ.get("EOCUBE_CLIENT_ID", None)
    client_secret = os.environ.get("EOCUBE_CLIENT_SECRET", None)
    client_scope = os.environ.get("EOCUBE_CLIENT_SCOPE", None)
    if client_id is None or client_secret is None:
        raise Exception("EOCUBE_CLIENT_ID and EOCUBE_CLIENT_SECRET must be set")

    kws = {"client_id": client_id, "client_secret": client_secret}
    if client_scope is not None:
        scope = re.split(r"\s+", client_scope)
        kws["scope"] = scope

    return AuthClient(**kws)


def get_presigned_url(fs, bucket, key, validity=3600):
    async def _gen_url():
        return await fs.s3.generate_presigned_url(
            "get_object", Params={"Bucket": bucket, "Key": key}, ExpiresIn=validity
        )

    return asyncio.run(_gen_url())


def get_eocube_sign(fs, validity=60 * 60 * 24 * 7):
    def _sign(obj):
        if isinstance(obj, dict):
            features = obj.get("features", [])
            for feature in features:
                assets = feature.get("assets")
                for asset_name, asset_spec in assets.items():
                    asset_href = asset_spec.get("href")
                    if not asset_href:
                        continue
                    url_spec = urlparse(asset_href)
                    if url_spec.scheme != "s3":
                        continue
                    bucket_name = url_spec.netloc
                    path = url_spec.path
                    new_url = get_presigned_url(fs, bucket_name, path, validity)
                    asset_spec["href"] = new_url

    return _sign
