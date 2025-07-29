# Limitify

A simple api-rate-limiting library for Python web frameworks with support for FastAPI, Flask, and Django.

## Installation

### Python
```bash
pip install limitify
```


## Quick Start

### FastAPI Implementation

#### Option 1: Middleware (Application-wide rate limiting)

```python
from fastapi import Request, HTTPException, FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from limitify import RateLimiter

app = FastAPI()

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, api_key: str):
        super().__init__(app)
        self.limiter = RateLimiter(api_key)
    
    async def dispatch(self, request: Request, call_next):
        status, data = await self.limiter.check_limit(request)
        
        if status != 200:
            detail = data.get("detail", "Rate limit error")
            raise HTTPException(status_code=status, detail=detail)
            
        response = await call_next(request)
        return response

app.add_middleware(RateLimitMiddleware, api_key="<api_key>")

@app.get("/users")
async def get_users():
    return {"msg": "hello world!"}
```

#### Option 2: Dependency Injection (Route-specific rate limiting)

```python
from fastapi import Request, HTTPException, FastAPI, Depends
from functools import wraps
from limitify import RateLimiter
import asyncio

app = FastAPI()
limiter = RateLimiter("<api_key>")

def rate_limit():
    """FastAPI dependency for rate limiting"""
    async def check_rate_limit(request: Request):
        status, data = await limiter.check_limit(request)
        
        if status != 200:
            detail = data.get("detail", "Rate limit error")
            raise HTTPException(status_code=status, detail=detail)
        
        return True
    
    return check_rate_limit

@app.get("/users")
async def get_users(request: Request, _: bool = Depends(rate_limit())):
    return {"msg": "hello world!"}

@app.get("/posts")
async def get_posts(request: Request, _: bool = Depends(rate_limit())):
    return {"posts": ["post1", "post2"]}

```

### Flask Implementation

```python
from flask import request, jsonify, Flask
from limitify import RateLimiter
import asyncio

app = Flask(__name__)

def ratelimit_middleware(api_key):
    limiter = RateLimiter(api_key)
    
    def decorator(f):
        def wrapper(*args, **kwargs):
            # Run async code inside sync Flask
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            status, data = loop.run_until_complete(limiter.check_limit(request))
            loop.close()

            if status != 200:
                return jsonify({"error": data.get("detail", "Rate limit error")}), status
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

@app.route("/admin")
@ratelimit_middleware("<api_key>")
def main():
    return "hello world!"

if __name__ == '__main__':
    app.run(port=8000)
```

### Django Implementation

#### Settings Configuration

```python
# myproject/settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    # ...other apps...
    'myapp',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # ...other middleware...
    'myapp.middleware.RateLimitMiddleware',
]
```

#### Middleware Implementation

```python
# myapp/middleware.py
import asyncio
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from limitify import RateLimiter

class RateLimitMiddleware(MiddlewareMixin):
    API_KEY = "GdnGypZSjvxcvqSxitX6EiGyVNYboaitSvOL4f0hIUY"
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.limiter = RateLimiter(self.API_KEY)
        self.loop = asyncio.new_event_loop()
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Skip rate limiting for admin URLs (optional)
        if request.path.startswith('/admin/'):
            return None
        
        # Run rate limiter check
        status, data = self.loop.run_until_complete(
            self.limiter.check_limit(request)
        )
        
        if status != 200:
            return JsonResponse(
                {"error": data.get("detail", "Rate limit error")},
                status=status
            )
        return None  # Continue processing
    
    def __del__(self):
        self.loop.close()
```

## API Reference

### Configuration Options

- **apiKey** (required) - Your API key for the rate limiting service

### RateLimiter Class

The main class for implementing rate limiting functionality.

#### Methods

- `check_limit(request)` - Checks if the current request should be rate limited
  - Returns: `(status_code, data)` tuple
  - `status_code`: HTTP status code (200 for allowed, 4xx for rate limited)
  - `data`: Dictionary containing error details if rate limited

## Framework Support

- ✅ **FastAPI** - Full async support with middleware
- ✅ **Flask** - Decorator-based implementation with async compatibility
- ✅ **Django** - Middleware implementation with optional path exclusions

## Usage Notes

### FastAPI
- Uses async middleware for optimal performance
- Integrates seamlessly with FastAPI's dependency injection system
- Supports all FastAPI features including automatic API documentation
- **Two implementation options:**
  - **Middleware**: Application-wide rate limiting for all routes
  - **Dependency**: Route-specific rate limiting with more granular control

### Flask
- Uses decorator pattern for easy route-specific rate limiting
- Handles async operations within Flask's synchronous context
- Compatible with Flask blueprints and extensions

### Django
- Implements as Django middleware for application-wide rate limiting
- Supports path-based exclusions (e.g., admin URLs)
- Follows Django's middleware patterns and conventions

## Contributing

We welcome contributions! Please see our contributing guidelines for more information.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please visit our documentation or contact our support team.
