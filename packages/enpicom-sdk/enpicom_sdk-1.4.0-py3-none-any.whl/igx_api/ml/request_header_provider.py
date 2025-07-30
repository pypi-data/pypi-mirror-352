"""@private
Nothing in this module is useful for customers to invoke directly, hide it from the docs.

Gets the public API key from the environment variable and adds it to the header of all requests
performed by MLflow
"""

import mlflow
from igx_api.l2.util.env import get_api_key_or_error
from mlflow.tracking.request_header.abstract_request_header_provider import RequestHeaderProvider


class PluginRequestHeaderProvider(RequestHeaderProvider):
    """RequestHeaderProvider provided through plugin system"""

    def in_context(self) -> bool:
        return True

    def request_headers(self) -> dict[str, str]:
        host = mlflow.get_tracking_uri()

        # If host contains igx.bio/mlflow or localhost, we assume it's an IGX MLflow server
        if "igx.bio/mlflow" in host or "localhost" in host:
            return {"igx-api-key": get_api_key_or_error()}

        return {}
