import logging

import google.auth.transport.requests
from google.api_core import exceptions as google_exceptions
from google.auth import default
from google.auth import impersonated_credentials
from google.cloud import iam_credentials

_LOGGER = logging.getLogger(__name__)


class Client:
    """A credentials client may be used to generate access tokens and credentials object
    compatible with Google APIs.

    :param google.oauth2.credentials.Credentials credentials: A credentials object to
        override the default behavior of attempting to create credentials using the
        inferred gcloud environment. You probably do NOT need to supply this in
        most cases. Defaults to ``None``.
    """

    def __init__(self, credentials=None):
        self._client = iam_credentials.IAMCredentialsClient(credentials=credentials)

    def _ensure_valid_client(self):
        try:
            credentials = self._client._credentials
        except AttributeError:
            try:
                credentials = self._client._transport._credentials
            except AttributeError:
                _LOGGER.error("Could not verify credentials in client.")
                return
        if not credentials.valid or not credentials.expiry:
            _LOGGER.info(
                "Refreshing client credentials, token expired: "
                f"[{str(credentials.expiry)}]"
            )
            request = google.auth.transport.requests.Request()
            credentials.refresh(request=request)
            _LOGGER.info(f"New expiration: [{str(credentials.expiry)}]")
        else:
            _LOGGER.debug(
                f"Token is valid: [{credentials.valid}] "
                f"expires: [{str(credentials.expiry)}]"
            )
        return

    def get_access_token(
        self, target_acct, scopes=["https://www.googleapis.com/auth/cloud-platform"]
    ):
        """
        Generates an access token for a target service account which may be used
        to impersonate that service account in API calls. Requires the calling account
        have the "Service Account Token Creator" role on the target account.

        .. code:: python

            from bibt.gcp import iam
            from google.oauth2 import credentials
            def main(event, context):
                client = iam.Client()
                token = client.get_access_token(
                    target_acct="myserviceaccount@myproject.iam.gserviceaccount.com"
                )
                api_creds = credentials.Credentials(token=token)
                storage_client = storage.Client(credentials=api_creds)
                storage_client.get_bucket("mybucket")

        :type target_acct: :py:class:`str`
        :param target_acct: the email address of the account to impersonate.

        :type scopes: :py:class:`list`
        :param scopes: the scopes to request for the token. by default, will be set
            to ``["https://www.googleapis.com/auth/cloud-platform"]`` which
            should be sufficient for most uses cases.

        :rtype: :py:class:`str`
        :returns: an access token with can be used to generate credentials
            for Google APIs.
        """
        # Create credentials for _LOGGER API at the org level
        _LOGGER.info(
            f"Getting access token for account: [{target_acct}] with scope: [{scopes}]"
        )
        self._ensure_valid_client()
        try:
            resp = self._client.generate_access_token(
                name=target_acct,
                scope=scopes,
            )
        except google_exceptions.PermissionDenied as e:
            _LOGGER.critical(
                "Permission denied while attempting to create access token. "
                "Ensure that the account running this function has the "
                '"Service Account Token Creator" '
                f"role on the target account ({target_acct})."
            )
            raise e

        _LOGGER.info("Returning access token.")
        return resp.access_token

    def get_credentials(
        self,
        target_acct,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
        source_credentials=None,
        lifetime=3600,
    ):
        """
        Generates a credentials object for a target service account which may be used
        to impersonate that service account in API calls. Requires the calling account
        have the "Service Account Token Creator" role on the target account. This
        version takes care of credentials object creation for you.

        .. code:: python

            from bibt.gcp import iam
            from google.oauth2 import credentials
            def main(event, context):
                client = iam.Client()
                api_creds = client.get_credentials(
                    target_acct="myserviceaccount@myproject.iam.gserviceaccount.com"
                )
                storage_client = storage.Client(credentials=api_creds)
                storage_client.get_bucket("mybucket")

        :type target_acct: :py:class:`str`
        :param target_acct: the email address of the account to impersonate.

        :type scopes: :py:class:`list`
        :param scopes: the scopes to request for the token. by default, will be set
            to ``["https://www.googleapis.com/auth/cloud-platform"]`` which
            should be sufficient for most uses cases.

        :type source_credentials: ``google.oauth2.credentials.Credentials``
        :param source_credentials: The credentials of the source account attempting
            to impersonate the target account. If not supplied, default() is used.

        :type lifetime: :py:class:`int`
        :param lifetime: For how long the credentials should be valid, in seconds.

        :rtype: ``google.oauth2.credentials.Credentials``
        :returns: a credentials object with can be used for authentication
            with Google APIs.
        """
        if not source_credentials:
            _LOGGER.debug("No source credentials passed, using default credentials.")
            source_credentials, project_id = default()
        src_principal = "UNK"
        try:
            src_principal = source_credentials._service_account_email
        except AttributeError:
            try:
                src_principal = source_credentials._client_id
            except AttributeError:
                pass

        _LOGGER.info(
            f"Generating and returning credentials object for [{src_principal}] "
            f"to impersonate [{target_acct}] for [{lifetime}] seconds "
            f"with scopes {scopes}"
        )
        return impersonated_credentials.Credentials(
            source_credentials=source_credentials,
            target_principal=target_acct,
            target_scopes=scopes,
            lifetime=lifetime,
        )
