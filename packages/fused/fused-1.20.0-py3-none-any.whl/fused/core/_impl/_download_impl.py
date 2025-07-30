from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import urlparse

import requests
from loguru import logger

from fused._global_api import get_api
from fused._optional_deps import HAS_FSSPEC
from fused._options import StorageStr, get_data_dir
from fused._options import options as OPTIONS
from fused.core._impl._context_impl import context_in_batch, context_in_realtime

if TYPE_CHECKING:
    import fsspec


def data_path(storage: StorageStr = "auto") -> Path:
    if storage != "auto":
        return get_data_dir(storage)
    return OPTIONS.data_directory


def filesystem(protocol: str, **storage_options) -> fsspec.AbstractFileSystem:
    """Get an fsspec filesystem for the given protocol.

    Args:
        protocol: Protocol part of the URL, such as "s3" or "gs".
        storage_options: Additional arguments to pass to the storage backend.

    Returns:
        An fsspec AbstractFileSystem.
    """
    if not HAS_FSSPEC:
        raise ImportError("fsspec is required to use this method")

    import fsspec
    from fsspec.implementations.dirfs import DirFileSystem

    if protocol == "fd":
        # fused team directory
        # Save an API call when set by rt2 or job2
        if OPTIONS.fd_prefix:
            root = OPTIONS.fd_prefix
            root_parsed = urlparse(root)
        else:
            api = get_api()
            root = api._resolve("fd://")
            root_parsed = urlparse(root)

        return DirFileSystem(
            path=root, fs=fsspec.filesystem(root_parsed.scheme, **storage_options)
        )
    else:
        return fsspec.filesystem(protocol, **storage_options)


def _download_requests(url: str) -> bytes:
    # this function is shared
    response = requests.get(url, headers={"User-Agent": ""})
    response.raise_for_status()
    return response.content


def _download_signed(url: str) -> bytes:
    from fused.api._public_api import get_api

    api = get_api()
    return _download_requests(api.sign_url(url))


def _download_object(protocol: str, url: str) -> bytes:
    """

    Args:
        protocol: Protocol part of the URL, such as "s3" or "gs".
        url: Object URL with or without the protocol.

    Returns:
        The object's content in bytes
    """
    # Local needs to use signed URL to impersonal remote IAM role to download the file while remote can assume it has
    # direct access to S3 resources due to its IAM role.
    if not context_in_realtime() and not context_in_batch():
        logger.debug("Trying a signed URL")
        try:
            return _download_signed(url)
        except Exception as e:
            logger.debug(str(e))

    if not HAS_FSSPEC:
        raise ImportError("fsspec is required to use this method")

    fs = filesystem(protocol)
    with fs.open(url, "rb") as f:
        return f.read()
