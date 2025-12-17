import sys
try:
    import pydantic
    print(f"Pydantic version: {pydantic.VERSION}")
except ImportError as e:
    print(f"Pydantic error: {e}")

try:
    import pydantic_core
    print(f"Pydantic Core version: {pydantic_core.__version__}")
except ImportError as e:
    print(f"Pydantic Core error: {e}")

try:
    from playwright.async_api import async_playwright
    print("Playwright imported successfully")
except ImportError as e:
    print(f"Playwright error: {e}")
