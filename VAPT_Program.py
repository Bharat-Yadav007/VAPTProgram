from urllib.parse import urlparse
import validators
import sys
from scanner.fingerprint import identify_tech
from scanner.portscanner import scan_ports
from scanner.headers import check_headers
from scanner.vulns.xss import check_xss
from scanner.vulns.sqli import scan_sqli
from scanner.vulns.dirbuster import brute_force_dirs
from scanner.crawler import crawl
from utils.report import generate_html_report, Finding

def validate_url(url):
    """Validate and normalize the URL"""
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    if not validators.url(url):
        raise ValueError("Invalid URL format")
    return url

def run_vapt(url):
    try:
        url = validate_url(url)
    except ValueError as e:
        print(f"Error: {e}")
        return

    results = {}

    print(f"\n[+] Starting VAPT scan on: {url}")
    print("[i] This may take several minutes...")

    try:        # Technology Fingerprinting
        tech_info = identify_tech(url)
        if tech_info:
            tech_stack_info = "\n".join([f"{k}: {', '.join(v)}" for k, v in tech_info.items()])
        else:
            tech_stack_info = "No technology information detected"
        
        results["Technology Stack"] = [
            Finding(
                "Technology Detection Results",
                tech_stack_info,
                "INFO"
            )
        ]

        # Port Scanning
        open_ports = scan_ports(url)
        if open_ports:
            results["Open Ports"] = [
                Finding(
                    "Open Ports Detection",
                    "\n".join(str(port) for port in open_ports),
                    "MEDIUM" if any(port not in [80, 443] for port in open_ports) else "INFO",
                    ["Review and close unnecessary ports",
                     "Implement firewall rules",
                     "Use port knocking for sensitive services"]
                )
            ]

        # Security Headers
        header_results = check_headers(url)
        results["Security Headers"] = [
            Finding(
                "Security Headers Analysis",
                header_results,
                "HIGH",
                ["Implement all missing security headers",
                 "Configure Content Security Policy (CSP)",
                 "Enable HSTS for HTTPS"]
            )
        ]

        # Crawling
        crawled_urls = crawl(url)
        results["Crawled URLs"] = [
            Finding(
                "Site Structure Analysis",
                "\n".join(crawled_urls) if crawled_urls else "No URLs found",
                "INFO"
            )
        ]

        # XSS Testing
        xss_results = check_xss(url)
        if xss_results:
            results["XSS Vulnerabilities"] = [
                Finding(
                    "Cross-Site Scripting (XSS) Analysis",
                    xss_results,
                    "HIGH",
                    ["Implement proper input validation",
                     "Use Content Security Policy",
                     "Sanitize user input",
                     "Encode output"]
                )
            ]

        # SQL Injection Testing
        sqli_results = scan_sqli(url)
        if sqli_results:
            results["SQL Injection"] = [
                Finding(
                    "SQL Injection Analysis",
                    sqli_results,
                    "CRITICAL",
                    ["Use parameterized queries",
                     "Implement proper input validation",
                     "Use ORM when possible",
                     "Limit database user privileges"]
                )
            ]

        # Directory Enumeration
        dir_results = brute_force_dirs(url)
        if dir_results:
            results["Directory Enumeration"] = [
                Finding(
                    "Directory Enumeration Results",
                    dir_results,
                    "MEDIUM",
                    ["Remove or protect sensitive directories",
                     "Implement proper access controls",
                     "Use robots.txt and .htaccess appropriately"]
                )
            ]

        generate_html_report(results)
        print("\n[✓] Scan complete. Report saved to: output/report.html")
        
    except KeyboardInterrupt:
        print("\n[!] Scan interrupted by user")
        if results:
            generate_html_report(results)
            print("[i] Partial report saved with collected results")
    except Exception as e:
        print(f"\n[!] Error during scan: {e}")
        if results:
            generate_html_report(results)
            print("[i] Partial report saved with collected results")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python program.py <URL>")
        print("Example: python program.py example.com")
    else:
        run_vapt(sys.argv[1])
