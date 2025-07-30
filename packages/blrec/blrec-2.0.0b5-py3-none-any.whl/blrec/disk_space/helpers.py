import asyncio
import os
import shutil
from typing import Literal

from loguru import logger


def is_space_enough(path: str, size: int) -> bool:
    return shutil.disk_usage(path).free > size


async def delete_file(path: str, log_level: Literal['INFO', 'DEBUG'] = 'INFO') -> None:
    loop = asyncio.get_running_loop()

    try:
        await loop.run_in_executor(None, os.remove, path)
    except Exception as e:
        logger.error(f'Failed to delete {path!r}, due to: {repr(e)}')
    else:
        logger.log(log_level, f'Deleted {path!r}')
