def extract_request_parts(url):
    # Extract protocol, host, port, and path from a URL depending on its format.
    if "://" in url:
        protocol, rest = url.split("://", 1)
    else:
        protocol, rest = "http", url
    
    if "/" in rest:
        host_part, path = rest.split("/", 1)
        path = "/" + path
    else:
        host_part = rest
        path = "/"
    
    port = 443 if protocol == "https" else 80  # 443 for HTTPS, 80 for HTTP
    if ":" in host_part:
        host, port_str = host_part.split(":", 1)
        port = int(port_str)
    else:
        host = host_part

    return protocol, host, port, path


if __name__ == '__main__':
    protocol, host, port, path = extract_request_parts("https://github.com/Chiuliana/tum-web-lab5")
    print(f"Protocol: {protocol}")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Path: {path}")