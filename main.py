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

        header_end = response.find(b'\r\n\r\n')
        
        if header_end == -1:
            # No header/body separator found
            return None, None, None
            
        headers_data = response[:header_end]
        body_data = response[header_end + 4:]
        
        # Decode headers safely
        headers_text = headers_data.decode('utf-8', errors='replace')
        headers = headers_text.split("\r\n")
        
        # Parse status code
        status_line = headers[0]
        status_parts = status_line.split(" ", 2)
        if len(status_parts) >= 2:
            status_code = int(status_parts[1])
        else:
            status_code = None
            
        # Parse headers into dictionary
        header_dict = {}
        for header in headers[1:]:
            if ": " in header:
                key, value = header.split(": ", 1)
                header_dict[key] = value
        
        # Try to decode the body - handle potential errors
        try:
            body_text = body_data.decode('utf-8', errors='replace')
        except Exception as e:
            body_text = f"[Error decoding body: {str(e)}]"
            
        return status_code, header_dict, body_text

    finally:
        s.close()


def follow_redirects(host, port, path, max_redirects=5, accept=None, protocol="http", visited_urls=None):
    if visited_urls is None:
        visited_urls = set()
    
    current_url = f"{protocol}://{host}:{port}{path}"
    redirect_count = 0
    
    while redirect_count < max_redirects:

        if current_url in visited_urls:
            print(f"Warning: Redirect loop detected at {current_url}")
            return None, None, None
        
        visited_urls.add(current_url)

        status_code, headers, body = http_request(
            host=host, port=port, path=path, accept=accept, protocol=protocol
        )
        
        if status_code in (301, 302, 303, 307, 308) and 'Location' in headers: # Check for redirect status codes
            redirect_url = headers['Location']
            print(f"Following redirect to: {redirect_url}")

            # Handle relative URLs
            if redirect_url.startswith('/'):
                redirect_url = f"{protocol}://{host}:{port}{redirect_url}"
            elif not redirect_url.startswith(('http://', 'https://')):
                redirect_url = f"{protocol}://{redirect_url}"
            
            protocol, host, port, path = extract_request_parts(redirect_url)
            current_url = redirect_url
            redirect_count += 1
        else:
            return status_code, headers, body
    
    print(f"Warning: Maximum number of redirects ({max_redirects}) followed.")
    return status_code, headers, body



if __name__ == '__main__':
    protocol, host, port, path = extract_request_parts("https://httpbin.org/redirect/6")
    print(f"Protocol: {protocol}")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Path: {path}")
    code, headers, body = follow_redirects(
        host=host, port=port, path=path, accept="text/html", protocol=protocol
    )
    print(f"Status Code: {code}")
    print(f"Headers: {headers}")
    print(f"Body:") 
    print(body)