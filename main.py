import sys
from unidiff import PatchSet

def main():
    diff_file = 'sample.diff'
    
    try:
        # Parse the git diff using unidiff
        patch_set = PatchSet.from_filename(diff_file)
    except FileNotFoundError:
        print(f"Error: Could not find '{diff_file}'.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading diff file: {e}")
        sys.exit(1)

    # Extract metrics
    files_changed = len(patch_set)
    added_lines = patch_set.added
    deleted_lines = patch_set.removed

    # Display extracted metrics
    print("--- PR Metrics ---")
    print(f"Files changed: {files_changed}")
    print(f"Added lines:   {added_lines}")
    print(f"Deleted lines: {deleted_lines}")
    print("------------------\n")

    # Implement basic rule checks
    violations = []
    
    if files_changed > 1:
        violations.append(f"Too many changed files (Expected <= 1, found {files_changed}).")
        
    if added_lines > 0:
        violations.append(f"Cannot add lines (Expected 0, found {added_lines}).")

    # Output validation result
    if violations:
        print("INVALID PR")
        for reason in violations:
            print(f"- {reason}")
    else:
        print("VALID PR")

if __name__ == '__main__':
    main()
