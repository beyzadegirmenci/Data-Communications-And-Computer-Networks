import socket
import sys

# Global variables to store the posted data
data_storage = []
prevent_scraping = '--prevent-scraping' in sys.argv

def handle_request(client_socket):
    request = client_socket.recv(4096).decode('utf-8')
    headers, body = request.split('\r\n\r\n', 1)
    header_lines = headers.split('\r\n')
    
    # Print headers for debugging
    print("Received headers:")
    for header in header_lines:
        print(header)
    
    first_line = header_lines[0]
    method, path, _ = first_line.split()
    
    if prevent_scraping:
        if any("User-Agent: curl" in header for header in header_lines):
            client_socket.sendall(b"HTTP/1.1 401 Unauthorized\r\n\r\n")
            client_socket.close()
            return

    if method == 'POST':
        content_length = 0
        for header in header_lines:
            if header.startswith('Content-Length:'):
                content_length = int(header.split()[1])
                break
        
        while len(body) < content_length:
            body += client_socket.recv(4096).decode('utf-8')
        
        data_storage.append(body)
        response = b"HTTP/1.1 200 OK\r\nContent-Length: 0\r\n\r\n"
    elif method == 'GET':
        response_body = "\r\n".join(data_storage)
        response = f"HTTP/1.1 200 OK\r\nContent-Length: {len(response_body)}\r\n\r\n{response_body}"
        response = response.encode('utf-8')
    else:
        response = b"HTTP/1.1 405 Method Not Allowed\r\n\r\n"

    client_socket.sendall(response)
    client_socket.close()

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('127.0.0.1', 8080))
    server_socket.listen(5)
    print("Server is listening on port 8080...")
    
    while True:
        client_socket, addr = server_socket.accept()
        handle_request(client_socket)

if __name__ == "__main__":
    start_server()
