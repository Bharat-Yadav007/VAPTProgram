# Uses sqlmap via subprocess
import subprocess

def scan_sqli(url):
    print("\n[+] Testing for SQL Injection with sqlmap...")
    try:
        result = subprocess.run(
            ["sqlmap", "-u", url, "--batch", "--level=2", "--risk=1", "--random-agent"],
            capture_output=True,
            text=True,
            timeout=120
        )
        print(result.stdout)
    except Exception as e:
        print(f"  [!] SQLMap failed: {e}")
