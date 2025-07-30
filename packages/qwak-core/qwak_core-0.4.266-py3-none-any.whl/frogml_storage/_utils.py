from typing import Optional
from urllib.parse import urlparse

from requests.auth import AuthBase

from frogml_storage.frogml_entity_type_info import FrogMLEntityTypeInfo


class BearerAuth(AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["Authorization"] = f"Bearer {self.token}"
        return r

    def __eq__(self, other):
        if not isinstance(other, BearerAuth):
            return False
        return self.token == other.token


class EmptyAuth(AuthBase):
    def __call__(self, r):
        return r


def join_url(base_uri: str, *parts: Optional[str]) -> str:
    if base_uri.endswith("/"):
        base_uri = base_uri[:-1]

    cleaned_parts = [
        part.strip("/") for part in parts if part is not None and part.strip("/")
    ]
    return f"{base_uri}/{'/'.join(cleaned_parts)}"


def assemble_artifact_url(uri: Optional[str]) -> str:
    if uri is None:
        raise Exception("Artifactory URI is required")

    parsed_url = urlparse(uri)
    if parsed_url.scheme not in ["http", "https"]:
        raise Exception(
            f"Not a valid Artifactory URI: {uri}. "
            f"Artifactory URI example: `https://frogger.jfrog.io/artifactory/ml-local`"
        )

    return f"{parsed_url.scheme}://{parsed_url.netloc}/artifactory"


# The following method affect e2e tests.
def build_download_success_log(
    entity_type_info: FrogMLEntityTypeInfo, entity_name: str, version: str
) -> str:
    return (
        f'{entity_type_info.entity_type.capitalize()}: "{entity_name}", version: "{version}"'
        f" has been downloaded successfully"
    )


# The following method affect e2e tests.
def build_upload_success_log(
    entity_type_info: FrogMLEntityTypeInfo, entity_name: str, version: str
) -> str:
    return (
        f'{entity_type_info.entity_type.capitalize()}: "{entity_name}", version: "{version}"'
        f" has been uploaded successfully"
    )
