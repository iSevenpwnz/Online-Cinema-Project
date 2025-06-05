from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from routes import (
    movie_router,
    accounts_router,
    profiles_router,
    shopping_cart_router
)

app = FastAPI(
    title="Online Cinema API",
    description="""
    # Online Cinema API Documentation
    
    This API provides endpoints for managing an online cinema platform, including:
    
    * User authentication and account management
    * Movie catalog and details
    * User profiles
    * Shopping cart functionality
    
    ## Authentication
    
    Most endpoints require authentication using JWT tokens. To authenticate:
    1. Register a new account using `/api/v1/accounts/register/`
    2. Login using `/api/v1/accounts/login/` to get access and refresh tokens
    3. Include the access token in the Authorization header: `Bearer <your_access_token>`
    
    ## Rate Limiting
    
    API requests are rate-limited to prevent abuse. Please contact support if you need higher limits.
    
    ## Error Handling
    
    The API uses standard HTTP status codes and returns detailed error messages in the response body.
    """,
    version="1.0.0",
    docs_url=None,  # Disable default docs URL
    redoc_url=None,  # Disable default redoc URL
    openapi_url="/api/v1/openapi.json"
)

api_version_prefix = "/api/v1"

# Custom Swagger UI endpoint
@app.get("/api/v1/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/api/v1/openapi.json",
        title="Online Cinema API - Swagger UI",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
    )

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add security scheme
    openapi_schema["components"] = {
        "securitySchemes": {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        }
    }
    
    # Add global security requirement
    openapi_schema["security"] = [{"bearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Include routers
app.include_router(accounts_router, prefix=f"{api_version_prefix}/accounts", tags=["accounts"])
app.include_router(profiles_router, prefix=f"{api_version_prefix}/profiles", tags=["profiles"])
app.include_router(movie_router, prefix=f"{api_version_prefix}/theater", tags=["theater"])
app.include_router(shopping_cart_router, prefix=f"{api_version_prefix}/cart", tags=["cart"])
