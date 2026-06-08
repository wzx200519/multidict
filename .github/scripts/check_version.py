import os
import sys
import json
import urllib.request
import urllib.error

def main():
    package_name = "multidict"
    github_ref = os.environ.get("GITHUB_REF", "")
    
    if not github_ref.startswith("refs/tags/v"):
        print(f"Ref {github_ref} is not a valid version tag (should start with refs/tags/v).")
        sys.exit(1)
        
    version = github_ref.split("/")[-1].lstrip("v")
    print(f"Checking if {package_name} version {version} exists on PyPI...")
    
    url = f"https://pypi.org/pypi/{package_name}/json"
    
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            releases = data.get("releases", {})
            
            if version in releases:
                print(f"Version {version} already exists on PyPI. Skipping release.")
                with open(os.environ["GITHUB_OUTPUT"], "a") as f:
                    f.write("exists=true\n")
            else:
                print(f"Version {version} does not exist on PyPI. Proceeding with release.")
                with open(os.environ["GITHUB_OUTPUT"], "a") as f:
                    f.write("exists=false\n")
                    
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"Package {package_name} not found on PyPI. Proceeding with initial release.")
            with open(os.environ["GITHUB_OUTPUT"], "a") as f:
                f.write("exists=false\n")
        else:
            print(f"Failed to fetch PyPI data: HTTP {e.code}")
            sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
