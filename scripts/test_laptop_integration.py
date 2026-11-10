"""Test and verify multi-repository optimization on all laptop applications."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.integration.multi_repo_optimizer import multi_repo_optimizer

def main():
    print("=" * 70)
    print("MULTI-REPOSITORY OPTIMIZER: HOST LAPTOP INTEGRATION")
    print("=" * 70)

    # 1. Discover all repositories on laptop
    repos = multi_repo_optimizer.discover_laptop_repositories()
    print("\n[+] Discovered Laptop Repositories:")
    for r in repos:
        status = "EXISTS" if r["exists"] else "NOT FOUND"
        print(f"    • {r['name']:<30} | {status:<9} | {r['python_files']} Py files | {r['test_files']} Tests")

    # 2. Analyze and optimize each existing application
    results = []
    for r in repos:
        if not r["exists"]:
            continue
        print(f"\n[*] Analyzing & Optimizing: {r['name']} ({r['path']})")
        res = multi_repo_optimizer.optimize_external_repo_change(r["path"])
        print(f"    Strategy           : {res['execution_strategy']}")
        print(f"    Failure Risk       : {res['failure_probability']:.2%}")
        print(f"    Model Confidence   : {res['model_confidence']:.2%}")
        print(f"    Available Tests    : {res['total_tests_available']}")
        print(f"    Selected Tests     : {res['selected_tests_count']}")
        print(f"    Test Reduction %   : {res['test_reduction_percentage']}%")
        results.append(res)

        # 3. Install AI CI/CD Pipeline into target repo
        install_res = multi_repo_optimizer.install_ai_cicd_to_repo(r["path"])
        print(f"    [+] Installed Workflow : {install_res['installed_workflow']}")
        print(f"    [+] Installed Runner   : {install_res['installed_runner']}")

    print("\n" + "=" * 70)
    print("[SUCCESS] All laptop applications analyzed, optimized, and integrated!")
    print("=" * 70)

if __name__ == "__main__":
    main()
