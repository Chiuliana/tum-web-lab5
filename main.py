import socket
import ssl

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


def http_request(
    host,
    port=80,
    path="/",
    method="GET",
    headers=None,
    body=None,
    timeout=10,
    accept=None,
    protocol="http",
):
    s = socket.socket()
    s.settimeout(timeout)

    # Use HTTPS if specified
    if protocol == "https":
        context = ssl.create_default_context()
        s = context.wrap_socket(s, server_hostname=host)
        if port == 80:  # Use default HTTPS port if standard HTTP port was specified
            port = 443

    try:
        s.connect((host, port))

        # Creating the Request structure
        request = f"{method} {path} HTTP/1.1\r\n"
        request += f"Host: {host}\r\n"
        request += "Connection: close\r\n"
        if accept:
            request += f"Accept: {accept}\r\n"
        if headers:
            for key, value in headers.items():
                request += f"{key}: {value}\r\n"
        if body:
            request += f"Content-Length: {len(body)}\r\n"
            request += "\r\n"
            request += body
        else:
            request += "\r\n"

        s.sendall(request.encode())

        response = b""
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            response += chunk

        response = response.decode('utf-8', errors='replace')
        return response

    finally:
        s.close()


if __name__ == '__main__':
    protocol, host, port, path = extract_request_parts("https://github.com/Chiuliana/tum-web-lab5")
    print(f"Protocol: {protocol}")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Path: {path}")
    response = http_request(
        host=host,
        port=port,
        path=path,
        protocol=protocol
    )
    print("Response:")
    print(response)