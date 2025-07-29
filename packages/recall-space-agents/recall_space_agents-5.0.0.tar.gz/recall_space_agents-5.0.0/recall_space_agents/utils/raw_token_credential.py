try:
    from azure.core.credentials import AccessToken
except:
    print("azure.core.credentials not found, please install azure-core package.")

import time

class RawTokenCredential:
    """A TokenCredential implementation that adapts your raw_token dictionary."""
    def __init__(self, raw_token: dict):
        self._access_token = raw_token['access_token']
        # Calculate the absolute expiration time (seconds since epoch), as needed by azure.core.credentials.AccessToken
        self._expires_on = int(time.time()) + int(raw_token.get('expires_in', 3600))

    def get_token(self, *scopes, **kwargs):
        # Could add logic here to refresh using the refresh_token if needed!
        return AccessToken(self._access_token, self._expires_on)