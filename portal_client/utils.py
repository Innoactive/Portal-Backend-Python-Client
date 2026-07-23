from base64 import b64encode
from os import getenv

from .auth import get_stored_access_token


def get_authorization_header():
    try:
        return get_bearer_authorization_header()
    except Exception:
        # Fallback to basic auth if bearer token is not set
        pass

    if getenv("PORTAL_BACKEND_USERNAME") and getenv("PORTAL_BACKEND_PASSWORD"):
        return "Basic {}".format(
            b64encode(
                bytes(
                    "%s:%s"
                    % (
                        getenv("PORTAL_BACKEND_USERNAME"),
                        getenv("PORTAL_BACKEND_PASSWORD"),
                    ),
                    "utf-8",
                )
            ).decode("ascii")
        )

    raise Exception(
        "Missing authentication! Please run `innoactive-portal auth login`, or specify either PORTAL_BACKEND_ACCESS_TOKEN or PORTAL_BACKEND_USERNAME and PORTAL_BACKEND_PASSWORD"
    )


def get_bearer_authorization_header():
    # An explicit env var always wins; otherwise fall back to a token stored via
    # `innoactive-portal auth login`.
    access_token = getenv("PORTAL_BACKEND_ACCESS_TOKEN") or get_stored_access_token()
    if access_token:
        return "Bearer %s" % access_token

    raise Exception(
        "Missing authentication! Please run `innoactive-portal auth login`, or specify either PORTAL_BACKEND_ACCESS_TOKEN or PORTAL_BACKEND_USERNAME and PORTAL_BACKEND_PASSWORD"
    )
