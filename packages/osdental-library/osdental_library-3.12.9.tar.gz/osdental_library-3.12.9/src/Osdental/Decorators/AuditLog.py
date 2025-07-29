import json
import asyncio
from typing import List, Any
from functools import wraps
from Osdental.InternalHttp.Request import CustomRequest
from Osdental.InternalHttp.Response import CustomResponse
from Osdental.Exception.ControlledException import OSDException
from Osdental.Handlers.DBSecurityQuery import DBSecurityQuery
from Osdental.Handlers.Instances import aes, batch
from Osdental.Shared.Logger import logger

def split_into_batches(data: List[Any], batch:int = 250):
    for i in range(0, len(data), batch):
        yield data[i:i + batch]


def handle_audit_and_exception(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            legacy = await DBSecurityQuery.get_legacy_data()
            _, info = args[:2] 
            request = info.context.get('request')
            headers = info.context.get('headers')
            if request:
                CustomRequest(request)

            response = await func(*args, **kwargs)
            data = aes.decrypt(legacy.aes_key_auth, response.get('data'))
            if data and isinstance(data, list) and batch > 0 and len(data) > batch:
                batches = split_into_batches(data, batch)
                for idx, data in enumerate(batches, start=1):
                    CustomResponse(content=json.dumps(data), headers=headers, batch=idx)
            else:
                CustomResponse(content=json.dumps(data), headers=headers)
            
            return response

        except OSDException as ex:
            logger.warning(f'Controlled server error: {str(ex.error)}')
            asyncio.create_task(ex.send_to_service_bus())
            return ex.get_response()
        
        except Exception as e:
            logger.error(f'Unexpected server error: {str(e)}')            
            ex = OSDException(error=str(e), headers=headers)
            asyncio.create_task(ex.send_to_service_bus())
            return ex.get_response()

    return wrapper