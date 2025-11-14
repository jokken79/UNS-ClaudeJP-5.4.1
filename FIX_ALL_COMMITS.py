#!/usr/bin/env python3
"""
Intelligent fix for all db.commit() calls

Wraps db operations (add/commit/refresh or just commit) in try-except blocks
"""

import re
from pathlib import Path
from typing import List, Tuple

def find_commit_blocks(lines: List[str]) -> List[Tuple[int, int, int]]:
    """
    Find db.commit() and determine the block to wrap
    Returns: List of (start_line, commit_line, indent_level)
    """
    blocks = []

    for i, line in enumerate(lines):
        if 'db.commit()' not in line:
            continue

        # Skip if already in try-except
        prev_10 = '\n'.join(lines[max(0, i-10):i])
        if 'try:' in prev_10:
            # Check if there's a matching except before this commit
            if 'except' not in prev_10.split('try:')[-1]:
                continue  # Already in try block

        # Get indent level
        indent = len(line) - len(line.lstrip())

        # Find start of block (look for db.add or previous statement at same indent)
        start = i
        for j in range(i-1, max(0, i-10), -1):
            prev_line = lines[j].strip()
            prev_indent = len(lines[j]) - len(lines[j].lstrip())

            if prev_indent < indent:
                # Found block start
                start = j + 1
                break

            if 'db.add(' in prev_line or 'db_' in prev_line:
                start = j
                continue

        blocks.append((start, i, indent))

    return blocks

def wrap_in_try_except(lines: List[str], start: int, commit_line: int, indent: int) -> List[str]:
    """Wrap lines from start to commit_line in try-except"""
    indent_str = ' ' * indent

    # Find end of block (db.refresh if exists)
    end = commit_line
    if commit_line + 1 < len(lines) and 'db.refresh' in lines[commit_line + 1]:
        end = commit_line + 1

    new_lines = []

    # Add try:
    new_lines.append(f"{indent_str}try:\n")

    # Add indented block
    for i in range(start, end + 1):
        new_lines.append(f"    {lines[i]}")

    # Add except:
    new_lines.append(f"{indent_str}except Exception as e:\n")
    new_lines.append(f"{indent_str}    db.rollback()\n")
    new_lines.append(f"{indent_str}    raise HTTPException(\n")
    new_lines.append(f"{indent_str}        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,\n")
    new_lines.append(f"{indent_str}        detail=f\"Database error: {{str(e)}}\"\n")
    new_lines.append(f"{indent_str}    )\n")

    return new_lines, end

def fix_file(file_path: Path) -> int:
    """Fix all db.commit() in a file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    blocks = find_commit_blocks(lines)

    if not blocks:
        return 0

    # Process blocks in reverse order to maintain line numbers
    blocks.reverse()

    for start, commit_line, indent in blocks:
        new_block, end = wrap_in_try_except(lines, start, commit_line, indent)

        # Replace lines
        lines[start:end+1] = new_block

    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    return len(blocks)

def main():
    backend_path = Path("/home/user/UNS-ClaudeJP-5.4.1/LolaAppJpnew/backend/app/api")

    print("🔧 Fixing db.commit() calls with error handling...")
    print()

    total_fixed = 0
    files_fixed = 0

    for api_file in sorted(backend_path.glob("*.py")):
        if api_file.name == "__init__.py":
            continue

        count = fix_file(api_file)
        if count > 0:
            print(f"✓ {api_file.name}: Fixed {count} db.commit() calls")
            total_fixed += count
            files_fixed += 1

    print()
    print(f"✅ Fixed {total_fixed} db.commit() calls in {files_fixed} files")

    return total_fixed

if __name__ == "__main__":
    fixed = main()
    exit(0 if fixed > 0 else 1)
