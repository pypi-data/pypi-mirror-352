#!/usr/bin/env python
import ast
import os
import sys
import argparse
import pkg_resources
import platform

IGNORED_DIRS = {'venv', '.venv', '__pycache__', '.git', 'env', '.idea', '.vscode'}

def extract_imports(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=file_path)
    except Exception as e:
        print(f"[!] Failed to parse {file_path}: {e}")
        return set()

    imported_modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_modules.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported_modules.add(node.module.split('.')[0])
    return imported_modules

def get_installed_packages():
    return {pkg.key: pkg.version for pkg in pkg_resources.working_set}

def match_imports_to_packages(imports):
    installed = get_installed_packages()
    result = []
    for mod in imports:
        mod_lower = mod.lower()
        if mod_lower in installed:
            result.append((mod_lower, installed[mod_lower]))
        else:
            print(f"[!] Warning: '{mod}' not found in current environment")
    return result

def collect_all_py_files(path):
    py_files = []
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d.lower() not in IGNORED_DIRS]
        for file in files:
            if file.endswith(".py"):
                py_files.append(os.path.join(root, file))
    return py_files

def export_requirements(requirements, output_path):
    if requirements:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(sorted(f"{name}=={version}" for name, version in requirements)))
        print(f"✅ requirements.txt written to: {output_path}")
    else:
        print("⚠️ No valid dependencies found.")

def export_pyproject_toml(requirements, output_path, name):
    py_ver = f">={platform.python_version_tuple()[0]}.{platform.python_version_tuple()[1]}"
    content = [
        "[project]",
        f'name = "{name}"',
        'version = "0.1.0"',
        'description = "Add your description here"',
        'readme = "README.md"',
        f'requires-python = "{py_ver}"',
        "",
        "dependencies = ["
    ]
    for name, version in sorted(requirements):
        content.append(f'    "{name}=={version}",')
    content.append("]")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(content))
    print(f"✅ pyproject.toml written to: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="该工具实现从目标代码导出依赖文件 requirements.txt 和 pyproject.toml")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-s", "--script", help="目标python脚本地址 eg. /path/to/script.py")
    group.add_argument("-p", "--project", help="目标python项目地址 eg. /path/to/project")
    args = parser.parse_args()

    if args.script:
        if not os.path.isfile(args.script):
            print(f"❌ File not found: {args.script}")
            return
        print(f"🔍 Analyzing script: {args.script}")
        imports = extract_imports(args.script)
        matched = match_imports_to_packages(imports)

        base_dir = os.path.dirname(args.script)
        name = os.path.splitext(os.path.basename(args.script))[0]

        export_requirements(matched, os.path.join(base_dir, "requirements.txt"))
        export_pyproject_toml(matched, os.path.join(base_dir, "pyproject.toml"), name)

    elif args.project:
        if not os.path.isdir(args.project):
            print(f"❌ Directory not found: {args.project}")
            return
        print(f"🔍 Scanning project directory: {args.project}")
        py_files = collect_all_py_files(args.project)
        all_imports = set()
        for py_file in py_files:
            all_imports |= extract_imports(py_file)

        matched = match_imports_to_packages(all_imports)

        name = os.path.basename(os.path.abspath(args.project))
        export_requirements(matched, os.path.join(args.project, "requirements.txt"))
        export_pyproject_toml(matched, os.path.join(args.project, "pyproject.toml"), name)

if __name__ == "__main__":
    main()
