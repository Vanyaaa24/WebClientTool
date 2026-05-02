"""hether or not the web server supports http2,
• 2. the cookie name, the expire time (if any), and the domain name (in any)
of cookies that the web server will use,
• 3. whether or not the requested web page is password-protected.

Docstring for WebTester
""" 
import sys
import ssl
import socket

##protocol://host[:port]/path[?query][#fragment]
def parse_uri(uri):
    """Parse the given uri into its components."""
    
    if not uri.startswith('http://') and not uri.startswith('https://'):

        uri = 'http://' + uri
        # protocol = uri.split('://')[0]


    if uri.startswith('http://'):
        protocol = 'http'
        default_port = 80
        uri = uri[7:]
    elif uri.startswith('https://'):
        protocol = 'https'
        default_port = 443
        uri = uri[8:]
    else:
        protocol = 'http'
        default_port = 80
   
   #seperate host and path 

    if '/' in uri:
        host, path = uri.split('/', 1)
        path = '/' + path
    else:
        host = uri
        path = '/' 

    #check if host has defined port

    if ':' in host:
        host, host_port= host.split(':', 1)
        port = int(host_port)
    else:
        port = default_port

    return protocol, host, port, path 

def connect_server(host, port):
    #Af_INet; address family; IPv4, IPv6
    #SOCK_STREAM; socket type; TCP or UDP
    """Connect client to the server and return the socket."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Socket successfully created")



    client_socket.connect((host, port))
    print(f"Connected to {host} on port {port}")

    """Method to approach"""
    #wrap socket with SSL for HTTPS
    ##connection established 
    ##send msg
    ##tsl handshake
    ##generates encryption keys
    ##secure connection established
    """
    client key exchaneg
    """
    http2_supported = False
    if port == 443:
        try:
            context = ssl.create_default_context()
            context.set_alpn_protocols(['h2', 'http/1.1'])  # Set ALPN protocols to negotiate HTTP/2 or HTTP/1.1
            tls_socket = context.wrap_socket(client_socket, server_hostname=host)

            selected_protocol = tls_socket.selected_alpn_protocol()
            if selected_protocol == 'h2':
                print("HTTP/2 is supported by the server.")
                http2_supported = True

                tls_socket.close()

                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((host, port))

                context2 = ssl.create_default_context()
                context2.set_alpn_protocols([ 'http/1.1'])
                tls_socket2 = context2.wrap_socket(client_socket, server_hostname=host)
                return tls_socket2, http2_supported
            else:
                print("HTTP/2 is not supported by the server. Using HTTP/1.1.")
                http2_supported = False
                return tls_socket, http2_supported
            
            #return tls_socket, http2_supported #return the tls wrapped socket
        except ssl.SSLCertVerificationError as e:
            #print error msg
            print(f"SSL certificate verification error: {e}");
            print("Cannot establish uniform connection; Invalid URL or untrusted certificate.");
            client_socket.close()
            return None, False
        except ssl.SSLError as e:
            print(f"SSL error: {e}")
            client_socket.close()
            sys.exit(1)
    else:
        # tls_socket = client_socket
        return client_socket, False #return client socket for HTTP

def send_http_request(client_socket, host, path):
    """Send an HTTP GET request to the server."""

    #requets.send couln't work becaus eit returns bytes, so we need to encode the string to bytes
    request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"

    request_bytes=request.encode()
    client_socket.sendall(request_bytes)
    print("HTTP request sent")

def response_handler(client_socket):
    """Receive and print the HTTP response from the server."""

    response = client_socket.recv(4096)
    full_response = response
    #print("Response received from server:")

    while response:
        response = client_socket.recv(4096)
        full_response += response
    try:
        decoded_response = full_response.decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error decoding response: {e}")
        return None, None, None, None
    
    ######Trying####
   
    if '\r\n\r\n' not in decoded_response:
        response_header = decoded_response
        response_body = ""
    else:
      response_header, response_body = decoded_response.split('\r\n\r\n', 1)
    print("-----Response Header-----")
    print(response_header)
    print("-----Response Body-----")
    print(response_body[:4096])  #print only first 200 chars of body

    #parse status line
    try:
        status_line = response_header.splitlines()[0]
        http_version, status_code, status_message = status_line.split(' ', 2)
        status_code = int(status_code)
    except Exception as e:
        print(f"Error parsing status line: {e}")
        return None, None, None, response_header

    if status_code == 200:
        print("Ok: Successful Request")
    elif status_code == 401:
        print("Unauthorized: Indicates a password-protected page")
    elif status_code==301 or status_code==302:
        print("Redirection: The requested resource has been moved")
    else:
        print("Not Found: Document does not exist")

    return http_version, status_code, status_message, response_header
    #ccheck for HTTP2 support

    #set ALPN for HTTP
    


    #Send HTTP 
def setcookie(response_header):
    """Extract and print cookie information from the response header."""
    cookies = []
    for line in response_header.splitlines():
            if line.lower().startswith("set-cookie:"):
                cookie_split = line.split(":", 1)[1].strip()
                cookie_info= extractInfo(cookie_split)
                cookies.append(cookie_info)
    return cookies

def extractInfo(cookie_split):
    """
    Docstring for extractInfo
    
    :param cookie_str: Description
     Input: "SESSID=abc123; domain=.uvic.ca; expires=Thu, 01-Jan-1970..."
    Output: {'name': 'SESSID', 'domain': '.uvic.ca', 'expires': '...'}
    :return: Description
    """

    cookie_info={"name":None, "domain":None, "expires": None}

    parts = cookie_split.split(';')

    # ex
    """
    "SESSID_UV_128004=abc123; Domain=www.uvic.ca; Path=/; Expires=Thu, 04-Jan-2018 00:00:01 GMT"
    """
    name_val = parts[0].strip()
    name = name_val.split('=', 1)[0]

    cookie_info['name'] = name

    for part in parts[1:]:
        part = part.strip()
        if part.lower().startswith('domain='):
            domain = part.split('=', 1)[1]
            cookie_info['domain'] = domain
        elif part.lower().startswith('expires='):
            expires = part.split('=', 1)[1]
            cookie_info['expires'] = expires

    return cookie_info


def redirect_handling(uri):
    # Placeholder for redirect handling logic

    #no need to limit redirect count for this assignment

    protocol, host, port, path = parse_uri(uri)
    client_socket, http2_supported = connect_server(host, port)
    if not client_socket:
        print(f"Failed to connect to {host} on port {port}")
        return None, None, False
    try:
        send_http_request(client_socket, host, path)
        http_version, status_code, status_message, response_header = response_handler(client_socket)
    finally:
        client_socket.close()
    if status_code in [301,302]:
        print("Handling redirect...")

        for line in response_header.splitlines():
            if line.startswith("Location:"):
                new_url = line.split(":", 1)[1].strip()
                print(f"Redirecting to {new_url}")
                return redirect_handling(new_url)
    return response_header, status_code, http2_supported    
   

def detect_password_protection(status_code, response_header):
    """Detect if the page is password-protected based on status code."""
    if status_code == 401:
        return True
    
    for line in response_header.splitlines():
        if line.lower().startswith("www-authenticate:"):
            return True
        
    return False


"""
Step2: Connect to the server(SOCKET.CONNECT)
Send an HTTP request(SOCKET.SEND)
Recieve the HTTP response(SOCKET.RECV)
Make a routine that print out response from server marking header and the body
Analysze HTTP response to find out reqd. info


"""

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 WebTester.py <URL>")
        return
    
    url = sys.argv[1]
    
    # Get final response after following redirects
    final_response_header, final_status_code, http2_supported = redirect_handling(url)
    
    if final_response_header and final_status_code is not None:
        password_protected = detect_password_protection(final_status_code, final_response_header)
    else:
        print("Failed to get response")
        password_protected = False
        # return
    
    # Extract ALL cookies using setcookie (not extractInfo!)
    cookies = setcookie(final_response_header)  
    
    password_protected = detect_password_protection(final_status_code, final_response_header)
    # Display cookies
    print("\n" + "="*60)
    print(f"website: {url}")
    print("1. Supports HTTP/2: ", "yes" if http2_supported else "no")  # TODO: Add HTTP/2 detection
    print("2. List of Cookies:")
    
    if cookies:
        for cookie in cookies:
            output = f"cookie name: {cookie['name']}"
            if cookie.get('expires'):
                output += f", expires time: {cookie['expires']}"
            if cookie.get('domain'):
                output += f", domain name: {cookie['domain']}"
            print(output)
    else:
        print("No cookies found")
    
    print(f"3. Password-protected: {'yes' if password_protected else 'no'}")  # TODO: Add password detection
    print("\n")
    
    print("\n Process completed.")
    

if __name__ == "__main__":
    main()
