import sys
import json
import argparse
from unidiff import PatchSet

def load_diff(diff_file: str) -> PatchSet:
    """
    Loads and parses the git diff file.
    Gracefully handles missing files and parsing errors.
    """
    try:
        return PatchSet.from_filename(diff_file)
    except FileNotFoundError:
        print(f"Error: The file '{diff_file}' was not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: Failed to parse diff file. Is it a valid Git diff format?\nDetails: {e}")
        sys.exit(1)

def extract_metrics(patch_set: PatchSet) -> dict:
    """
    Extracts core metrics from the parsed patch set.
    """
    return {
        "files_changed": len(patch_set),
        "added_lines": patch_set.added,
        "deleted_lines": patch_set.removed
    }

def validate_rules(metrics: dict) -> list:
    """
    Applies validation rules against extracted metrics.
    
    Future Extensibility:
    - Rule engine will be configurable via a YAML configuration file.
    - Designed to plug directly into GitHub Actions as a pre-merge check.
    """
    violations = []
    
    if metrics["files_changed"] > 1:
        violations.append(f"Too many changed files (Expected <= 1, found {metrics['files_changed']})")
        
    if metrics["added_lines"] > 0:
        violations.append(f"Added lines are not allowed (Expected 0, found {metrics['added_lines']})")
        
    return violations

def display_output(metrics: dict, violations: list, json_mode: bool = False):
    """
    Formats and displays the final validation result in either CLI text or JSON.
    """
    is_valid = len(violations) == 0

    if json_mode:
        result = {
            "valid": is_valid,
            "metrics": metrics,
            "violations": violations
        }
        print(json.dumps(result, indent=2))
        return

    print("=== PR ANALYSIS ===")
    print(f"Files Changed : {metrics['files_changed']}")
    print(f"Added Lines   : {metrics['added_lines']}")
    print(f"Deleted Lines : {metrics['deleted_lines']}")
    print("\n=== RESULT ===")

    if is_valid:
        print("✅ VALID PR")
    else:
        print("❌ INVALID PR")
        for message in violations:
            print(f"→ {message}")

def main():
    parser = argparse.ArgumentParser(
        description="BLT Preflight: A professional CLI tool to validate Git Pull Requests via diff analysis."
    )
    parser.add_argument("diff_file", help="Path to the .diff file to analyze")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    
    args = parser.parse_args()
    
    patch_set = load_diff(args.diff_file)
    metrics = extract_metrics(patch_set)
    violations = validate_rules(metrics)
    
    display_output(metrics, violations, json_mode=args.json)
    
    if violations:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
