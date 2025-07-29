import geoip2.database
from pathlib import Path

def get_country_code(ip: str) -> str:
    try:
        db_path = Path(__file__).parent.parent / "GeoLite2-Country.mmdb"
        reader = geoip2.database.Reader(str(db_path))
        response = reader.country(ip)
        return response.country.iso_code or "NA"
    except:
        return "NA"

def get_client_ip(request) -> str:
    # Common proxy headers
    x_forwarded_for = getattr(request, 'headers', {}).get("X-Forwarded-For")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()

    x_real_ip = getattr(request, 'headers', {}).get("X-Real-IP")
    if x_real_ip:
        return x_real_ip.strip()

    # Framework-specific IP extraction
    # 1. FastAPI/Starlette
    if hasattr(request, 'client') and request.client:
        return request.client.host
    
    # 2. Flask
    if hasattr(request, 'remote_addr'):
        return request.remote_addr
    
    # 3. Django
    if hasattr(request, 'META'):
        return request.META.get('REMOTE_ADDR', '127.0.0.1')
    
    # Default fallback
    return '127.0.0.1'

def get_request_path(request) -> str:
    """Get request path from any framework"""
    # 1. FastAPI/Starlette
    if hasattr(request, 'url') and hasattr(request.url, 'path'):
        return request.url.path
    
    # 2. Flask
    if hasattr(request, 'path'):
        return request.path
    
    # 3. Django
    if hasattr(request, 'path_info'):
        return request.path_info
    
    # Fallback for other frameworks
    return '/'

def get_request_method(request) -> str:
    """Get request method from any framework"""
    # 1. FastAPI/Starlette
    if hasattr(request, 'method'):
        return request.method
    
    # 2. Flask
    if hasattr(request, 'method'):
        return request.method
    
    # 3. Django
    if hasattr(request, 'method'):
        return request.method
    
    # Fallback for other frameworks
    return 'GET'