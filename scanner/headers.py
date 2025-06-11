import requests

def check_headers(url):
    print("\n[+] Checking security headers...")
    try:
        res = requests.get(url)
        headers = res.headers

        security_headers = [
            "Content-Security-Policy",
            "Strict-Transport-Security",
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
            "Referrer-Policy"
        ]

        for header in security_headers:
            if header in headers:
                print(f"  [+] {header}: {headers[header]}")
            else:
                print(f"  [-] Missing: {header}")
    except:
        print("  [!] Unable to fetch headers.")
