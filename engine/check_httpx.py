import httpx
print(f"httpx version: {httpx.__version__}")
try:
    c = httpx.Client(proxy="http://localhost:8080")
    print("httpx.Client accepted proxy")
except TypeError as e:
    print(f"httpx.Client failed with proxy: {e}")
    try:
        c = httpx.Client(proxies="http://localhost:8080")
        print("httpx.Client accepted proxies")
    except TypeError as e2:
        print(f"httpx.Client failed with proxies: {e2}")
