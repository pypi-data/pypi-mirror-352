from __future__ import annotations

import logging
import typing as T

from . import _core as core

logger = logging.getLogger(__name__)


# https://stackoverflow.com/a/72832981/592289
# Types
ETopoDataset = T.Literal["bedrock", "ice_surface"]
# Constants
ETOPO1: T.Literal["ETOPO1"] = "ETOPO1"


def get_etopo_filename(dataset: ETopoDataset) -> str:
    filename = f"ETOPO1_{dataset}_g_gdal.nc"
    return filename


def etopo1(
    dataset: ETopoDataset,
    *,
    registry_url: str | None = None,
) -> str:
    core.enforce_literals(etopo1)
    registry = core.load_registry(registry_url=registry_url)
    record = registry[ETOPO1][dataset]
    cache_dir = core.get_cache_path() / ETOPO1
    filename = str(record["filename"])
    path = cache_dir / filename
    if not path.exists():
        cache_dir.mkdir(parents=True, exist_ok=True)
        url = str(record["url"])
        archive_path = cache_dir / record["archive"]
        # core.download(url, archive_path)
        core.extract_gzip(archive_path, path)
        # core.lenient_remove(archive_path)
    core.check_hash(path, str(record["hash"]))
    return str(path)
