import httpx
from datetime import datetime
from .helpers import get_country_code, get_client_ip, get_request_method, get_request_path

class RateLimiter:
    def __init__(self, api_key, server_url="http://localhost:5000/rate-limit"):
        self.api_key = api_key
        self.server_url = server_url

    # async def check_limit(self, path, method=None, ip="0.0.0.0"):
    async def check_limit(self, request):
        path = get_request_path(request)
        method = get_request_method(request)
        ip = get_client_ip(request)
        
        print("Its checking time")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        country_code = get_country_code(ip)
        
        async with httpx.AsyncClient() as client:
            try:
                ip_address = ip if ip is not None else "0.0.0.0"

                response = await client.post(
                    self.server_url,
                    json={
                        "api_key": self.api_key,
                        "path": path,
                        "timestamp": timestamp,
                        "method": method,
                        "ip": ip_address,
                        "country_code": country_code
                    },
                    timeout=3.0
                )
                return response.status_code, response.json()
            except Exception as e:
                return 500, {"error": str(e)}
