# scanner/fingerprint.py
import builtwith
import requests

def identify_tech(url):
    print("[+] Technologies used:")
    try:
        tech = builtwith.builtwith(url)
        if tech:
            for k, v in tech.items():
                print(f"  {k}: {', '.join(v)}")
            return tech
        else:
            print("  [-] No technologies detected")
            return {"No technologies detected": ["Unknown"]}
    except requests.RequestException as e:
        print(f"  [!] Error accessing URL: {str(e)}")
        return {"Error": [str(e)]}
    except Exception as e:
        print(f"  [!] Error during technology detection: {str(e)}")
        return {"Error": [str(e)]}
