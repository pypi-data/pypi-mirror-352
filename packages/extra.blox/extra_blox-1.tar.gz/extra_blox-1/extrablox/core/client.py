import httpx
from typing import Optional

class AsyncClient:
    def __init__(self):
        self._client =  httpx.AsyncClient()
    
    async def _get(self, 
                   url: str, 
                   params: Optional[dict] = None) -> httpx.Response:
        response = await self._client.get(url, params=params)
        response.raise_for_status()
        return response
    
    async def _post(self,
                     url: str, 
                     json: Optional[dict] = None) -> httpx.Response:
        
        response = await self._client.post(url, json=json)
        response.raise_for_status()
        return response
    
    async def _put(self,
                     url: str, 
                     json: Optional[dict] = None) -> httpx.Response:
          
        response = await self._client.put(url, json=json)
        response.raise_for_status()
        return response
    
    async def _delete(self,
                      url: str, 
                      params: Optional[dict] = None) -> httpx.Response:
        
        response = await self._client.delete(url, params=params)
        response.raise_for_status()
        return response
    
    async def close_connection(self):
        await self._client.aclose()
        return

    