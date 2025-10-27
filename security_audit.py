#!/usr/bin/env python3
"""
Security audit script for dependency scanning and vulnerability checking
Run this regularly to check for security issues
"""
import subprocess
import sys
import json
from datetime import datetime

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def run_pip_audit():
    """Run pip-audit to check for known vulnerabilities"""
    print_header("Running pip-audit for Python dependencies")
    
    try:
        # Check if pip-audit is installed
        subprocess.run(['pip', 'show', 'pip-audit'], 
                      capture_output=True, check=True)
    except subprocess.CalledProcessError:
        print("⚠️  pip-audit not installed. Installing...")
        subprocess.run(['pip', 'install', 'pip-audit'], check=True)
    
    # Run pip-audit
    result = subprocess.run(['pip-audit', '--format', 'json'], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ No known vulnerabilities found in Python dependencies")
        return True
    else:
        print("⚠️  Vulnerabilities found:")
        try:
            data = json.loads(result.stdout)
            for vuln in data.get('dependencies', []):
                print(f"\n  Package: {vuln.get('name')}")
                print(f"  Version: {vuln.get('version')}")
                print(f"  Vulnerability: {vuln.get('vulns', [{}])[0].get('id')}")
                print(f"  Fix: Upgrade to {vuln.get('vulns', [{}])[0].get('fix_versions', ['N/A'])[0]}")
        except:
            print(result.stdout)
        return False

def check_outdated_packages():
    """Check for outdated packages"""
    print_header("Checking for outdated packages")
    
    result = subprocess.run(['pip', 'list', '--outdated', '--format', 'json'], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        outdated = json.loads(result.stdout)
        if not outdated:
            print("✅ All packages are up to date")
            return True
        else:
            print(f"⚠️  {len(outdated)} packages have updates available:\n")
            for pkg in outdated[:10]:  # Show first 10
                print(f"  {pkg['name']}: {pkg['version']} → {pkg['latest_version']}")
            if len(outdated) > 10:
                print(f"\n  ... and {len(outdated) - 10} more")
            return False
    return False

def check_requirements_pinning():
    """Check if requirements.txt has pinned versions"""
    print_header("Checking requirements.txt version pinning")
    
    try:
        with open('requirements.txt', 'r') as f:
            lines = f.readlines()
        
        unpinned = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                if '==' not in line:
                    unpinned.append(line)
        
        if not unpinned:
            print("✅ All dependencies are pinned to specific versions")
            return True
        else:
            print(f"⚠️  {len(unpinned)} dependencies are not pinned:")
            for pkg in unpinned:
                print(f"  {pkg}")
            return False
    except FileNotFoundError:
        print("❌ requirements.txt not found")
        return False

def check_python_version():
    """Check Python version"""
    print_header("Checking Python version")
    
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 9:
        print("✅ Python version is supported and secure")
        return True
    else:
        print("⚠️  Consider upgrading to Python 3.9 or higher")
        return False

def generate_report(results):
    """Generate security audit report"""
    print_header("Security Audit Report")
    
    total_checks = len(results)
    passed_checks = sum(results.values())
    
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total Checks: {total_checks}")
    print(f"Passed: {passed_checks}")
    print(f"Failed: {total_checks - passed_checks}")
    print(f"Score: {(passed_checks/total_checks)*100:.1f}%")
    
    if passed_checks == total_checks:
        print("\n✅ All security checks passed!")
        return 0
    else:
        print("\n⚠️  Some security checks failed. Review the issues above.")
        return 1

def main():
    """Main audit function"""
    print_header("Backend Security Audit")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        'pip_audit': run_pip_audit(),
        'outdated_packages': check_outdated_packages(),
        'pinned_versions': check_requirements_pinning(),
        'python_version': check_python_version()
    }
    
    exit_code = generate_report(results)
    
    print("\n💡 Tip: Run this script regularly (weekly) to stay secure")
    print("💡 Tip: Add to CI/CD pipeline for automated checking\n")
    
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
