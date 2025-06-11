import requests
from urllib.parse import urljoin

COMMON_DIRS = {
    'admin_panels': [
        'admin', 'administrator', 'admin.php', 'admin.html',
        'wp-admin', 'admincp', 'admin_cp', 'cp'
    ],
    'login_pages': [
        'login', 'login.php', 'signin', 'login.html',
        'user/login', 'auth', 'authentication'
    ],
    'sensitive': [
        '.git', '.env', '.htaccess', 'backup', 'backups',
        'wp-config.php', 'config.php', 'configuration.php',
        'database.yml', 'credentials.txt'
    ],
    'common': [
        'uploads', 'images', 'img', 'static', 'assets',
        'css', 'js', 'api', 'docs', 'documentation',
        'test', 'temp', 'files', 'download'
    ]
}

def brute_force_dirs(base_url):
    print("\n[+] Brute forcing directories...")
    findings = []
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'VAPT-Scanner/1.0 (Educational Purpose Only)'
    })

    for category, dirs in COMMON_DIRS.items():
        print(f"\n  [+] Scanning {category}...")
        for directory in dirs:
            url = urljoin(base_url.rstrip('/') + '/', directory)
            try:
                res = session.get(url, timeout=5, allow_redirects=False)
                status = res.status_code
                
                if status == 200:
                    print(f"  [!] Found: {url} (Status: {status})")
                    findings.append(f"{url} (Status: {status})")
                elif status in [301, 302, 403]:
                    print(f"  [*] Interesting: {url} (Status: {status})")
                    findings.append(f"{url} (Status: {status})")
                
            except requests.Timeout:
                print(f"  [-] Timeout: {url}")
            except requests.RequestException as e:
                print(f"  [-] Error accessing {url}: {str(e)}")
            except Exception as e:
                print(f"  [-] Unexpected error for {url}: {str(e)}")

    return "\n".join(findings) if findings else "No interesting directories found."
