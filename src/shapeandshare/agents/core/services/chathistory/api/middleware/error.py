import logging
import traceback
from functools import wraps
from typing import Callable

from fastapi import HTTPException

from .....framework.contracts.errors.dao.conflict import DaoConflictError
from .....framework.contracts.errors.dao.doesnotexist import DaoDoesNotExistError

logger = logging.getLogger()


def error_handler(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException as error:
            logger.error(str(error))
            raise error from error
        except DaoConflictError as error:
            logger.error(str(error))
            raise HTTPException(status_code=409, detail=str(error)) from error
        except DaoDoesNotExistError as error:
            logger.error(str(error))
            raise HTTPException(status_code=404, detail=str(error)) from error
        except Exception as error:
            traceback.print_exc()
            logger.error(str(error))
            # catch everything else
            raise HTTPException(status_code=500, detail=f"Uncaught exception: {str(error)}") from error

    return wrapper
