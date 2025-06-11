# scanner/vulns/xss.py
import requests
from urllib.parse import urlparse, parse_qs, urlencode
import html

XSS_PAYLOADS = [
    '<script>alert(1)</script>',
    '"><script>alert(1)</script>',
    '"><img src=x onerror=alert(1)>',
    '"><svg onload=alert(1)>',
    "javascript:alert(1)",
    '">><marquee><img src=x onerror=alert(1)></marquee>',
    '"><img src=x onerror=prompt(1)>',
    '<img src=`xx:xx`onerror=alert(1)>',
    '<div/onmouseover="alert(1)">',
    '<--`<img/src=` onerror=alert(1)>--!>',
]

def is_vulnerable(response_text, payload):
    """Check if the payload is reflected in a potentially dangerous way"""
    # Decode HTML entities in response
    decoded_resp = html.unescape(response_text)
    
    # Check for direct reflection
    if payload in decoded_resp:
        # Check if payload is within a script tag
        if f'<script>{payload}</script>' in decoded_resp:
            return True
        
        # Check if payload is in attribute
        if f'onerror={payload}' in decoded_resp or f'onload={payload}' in decoded_resp:
            return True
        
        # Check if payload is not escaped properly
        if '<' in payload and '&lt;' not in decoded_resp:
            return True
    
    return False

def check_xss(url):
    print("\n[+] Testing for reflected XSS...")
    parsed = urlparse(url)
    queries = parse_qs(parsed.query)
    findings = []
    
    if not queries:
        print("  [-] No query parameters to test")
        return "No query parameters found to test for XSS"

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'VAPT-Scanner/1.0 (Educational Purpose Only)'
    })

    for param in queries:
        print(f"  [*] Testing parameter: {param}")
        vulnerable = False
        
        for payload in XSS_PAYLOADS:
            new_query = queries.copy()
            new_query[param] = [payload]
            test_url = parsed._replace(query=urlencode(new_query, doseq=True)).geturl()
            
            try:
                resp = session.get(test_url, timeout=10)
                if is_vulnerable(resp.text, payload):
                    print(f"  [!] XSS vulnerability found in parameter '{param}' with payload: {payload}")
                    findings.append(f"Parameter '{param}' is vulnerable to XSS\nTest URL: {test_url}\nPayload: {payload}")
                    vulnerable = True
                    break
            except requests.RequestException as e:
                print(f"  [-] Error testing {param}: {str(e)}")
                continue
        
        if not vulnerable:
            print(f"  [-] Parameter '{param}' appears to be safe")

    if findings:
        return "\n\n".join(findings)
    return "No XSS vulnerabilities found in the tested parameters"
