# scanner/portscanner.py
import socket
import asyncio
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

COMMON_PORTS = [
    20, 21,  # FTP
    22,      # SSH
    23,      # Telnet
    25,      # SMTP
    53,      # DNS
    80,      # HTTP
    110,     # POP3
    143,     # IMAP
    443,     # HTTPS
    445,     # SMB
    1433,    # MSSQL
    1521,    # Oracle
    3306,    # MySQL
    3389,    # RDP
    5432,    # PostgreSQL
    8080,    # HTTP Alternate
    8443,    # HTTPS Alternate
    27017,   # MongoDB
]

TIMEOUT = 2
MAX_RETRIES = 3

async def check_port(hostname, port, retry_count=0):
    try:
        future = await asyncio.get_event_loop().run_in_executor(
            None, 
            lambda: socket.create_connection((hostname, port), timeout=TIMEOUT)
        )
        future.close()
        return port, None  # Success case
    except socket.timeout:
        if retry_count < MAX_RETRIES:
            return await check_port(hostname, port, retry_count + 1)
        return port, "Timeout"
    except socket.error as e:
        return port, str(e)
    except Exception as e:
        return port, f"Unexpected error: {str(e)}"

async def scan_ports_async(hostname):
    tasks = [check_port(hostname, port) for port in COMMON_PORTS]
    results = await asyncio.gather(*tasks)
    return [(port, error) for port, error in results if error is None]

def scan_ports(url):
    print("\n[+] Scanning common ports...")
    try:
        hostname = urlparse(url).netloc.split(':')[0]
        if not hostname:
            hostname = url.replace("http://", "").replace("https://", "").split("/")[0]
        
        # Run the async port scanner
        results = asyncio.run(scan_ports_async(hostname))
        
        if results:
            print(f"  [+] Found {len(results)} open ports:")
            for port, _ in results:
                service = get_service_name(port)
                print(f"  [!] Port {port} ({service})")
            return [port for port, _ in results]
        else:
            print("  [-] No common ports found open")
            return []
    except Exception as e:
        print(f"  [!] Error during port scan: {str(e)}")
        return []

def get_service_name(port):
    services = {
        20: 'FTP-DATA', 21: 'FTP', 22: 'SSH', 23: 'Telnet',
        25: 'SMTP', 53: 'DNS', 80: 'HTTP', 110: 'POP3',
        143: 'IMAP', 443: 'HTTPS', 445: 'SMB', 1433: 'MSSQL',
        1521: 'Oracle', 3306: 'MySQL', 3389: 'RDP', 5432: 'PostgreSQL',
        8080: 'HTTP-ALT', 8443: 'HTTPS-ALT', 27017: 'MongoDB'
    }
    return services.get(port, 'Unknown')
