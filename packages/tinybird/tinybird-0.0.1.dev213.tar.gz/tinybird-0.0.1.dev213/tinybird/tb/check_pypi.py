from typing import Optional

import requests

from tinybird.syncasync import sync_to_async
from tinybird.tb.modules.common import getenv_bool

PYPY_URL = "https://pypi.org/pypi/tinybird/json"
requests_get = sync_to_async(requests.get, thread_sensitive=False)


class CheckPypi:
    async def get_latest_version(self) -> Optional[str]:
        version: Optional[str] = None
        try:
            disable_ssl: bool = getenv_bool("TB_DISABLE_SSL_CHECKS", False)
            response: requests.Response = await requests_get(PYPY_URL, verify=not disable_ssl)
            if response.status_code != 200:
                return None
            version = response.json()["info"]["version"]
        except Exception:
            return None

        return version
