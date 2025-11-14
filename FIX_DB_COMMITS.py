#!/usr/bin/env python3
"""
Fix all db.commit() calls to include proper error handling

Adds try-except blocks with rollback around all db.commit() calls
"""

import re
from pathlib import Path

def fix_file(file_path: Path) -> int:
    """Fix db.commit() calls in a file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    fixed_count = 0
    new_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check if this line has db.commit()
        if 'db.commit()' in line and 'try:' not in lines[max(0, i-5):i]:
            # Get indentation
            indent = len(line) - len(line.lstrip())
            indent_str = ' ' * indent

            # Check if already in try-except
            prev_lines = ''.join(lines[max(0, i-10):i])
            if 'try:' in prev_lines and 'except' not in prev_lines:
                # Already in a try block
                new_lines.append(line)
                i += 1
                continue

            # Add try block before commit
            new_lines.append(f"{indent_str}try:\n")
            new_lines.append(line)

            # Add except block after commit
            new_lines.append(f"{indent_str}except Exception as e:\n")
            new_lines.append(f"{indent_str}    db.rollback()\n")
            new_lines.append(f"{indent_str}    raise HTTPException(\n")
            new_lines.append(f"{indent_str}        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,\n")
            new_lines.append(f"{indent_str}        detail=str(e)\n")
            new_lines.append(f"{indent_str}    )\n")

            fixed_count += 1
            i += 1
        else:
            new_lines.append(line)
            i += 1

    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    return fixed_count

def main():
    backend_path = Path("/home/user/UNS-ClaudeJP-5.4.1/LolaAppJpnew/backend/app/api")

    total_fixed = 0

    for api_file in backend_path.glob("*.py"):
        if api_file.name == "__init__.py":
            continue

        count = fix_file(api_file)
        if count > 0:
            print(f"✓ Fixed {count} db.commit() calls in {api_file.name}")
            total_fixed += count

    print(f"\n✅ Total fixed: {total_fixed} db.commit() calls")

    return total_fixed

if __name__ == "__main__":
    main()
