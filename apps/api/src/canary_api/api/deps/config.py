"""Settings dependency."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from canary_api.core.config import Settings, get_settings

SettingsDep = Annotated[Settings, Depends(get_settings)]
