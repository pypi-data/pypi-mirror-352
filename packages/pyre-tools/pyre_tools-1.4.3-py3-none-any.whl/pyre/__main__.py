#!/usr/bin/env python
import ast
import os
import sys
import argparse
import pkg_resources
import platform
import sysconfig
import importlib.util
import logging
#from importlib.metadata import packages_distributions, version as get_version
from collections import defaultdict

def get_version(module_name):
    """回退到 pkg_resources 获取版本"""
    try:
        dist = pkg_resources.get_distribution(module_name)
        return dist.version
    except pkg_resources.DistributionNotFound:
        raise

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

IGNORED_DIRS = {'venv', '.venv', '__pycache__', '.git', 'env', '.idea', '.vscode', 'node_modules', 'dist', 'build'}
IGNORED_FILES = {'__init__.py', 'setup.py'}

# 扩展支持的文件类型
SUPPORTED_EXTENSIONS = {'.py', '.pyw', '.ipynb'}

# 常见模块别名映射（包含更多常见映射）
MODULE_ALIASES = {
    "cv2": "opencv-python",
    "PIL": "Pillow",
    "Image": "Pillow",
    "yaml": "PyYAML",
    "Crypto": "pycryptodome",
    "skimage": "scikit-image",
    "lxml": "lxml",
    "bs4": "beautifulsoup4",
    "sklearn": "scikit-learn",
    "dateutil": "python-dateutil",
    "pandas": "pandas",
    "np": "numpy",
    "pd": "pandas",
    "plt": "matplotlib",
    "sns": "seaborn",
    "tf": "tensorflow",
    "torch": "torch",
    "mxnet": "mxnet",
    "keras": "keras",
    "tqdm": "tqdm",
    "django": "django",
    "flask": "flask",
    "requests": "requests",
    "sqlalchemy": "SQLAlchemy",
    "bson": "pymongo",
    "pymongo": "pymongo",
    "redis": "redis",
    "psycopg2": "psycopg2-binary",
    "MySQLdb": "mysqlclient",
    "jinja2": "Jinja2",
    "werkzeug": "Werkzeug",
    "celery": "celery",
}

# 已知标准库模块列表（补充更多常见标准库）
STDLIB_MODULES = {
    "os", "sys", "re", "math", "json", "datetime", "time", "collections", 
    "itertools", "functools", "argparse", "logging", "subprocess", "threading",
    "multiprocessing", "socket", "ssl", "hashlib", "base64", "urllib", "html",
    "xml", "csv", "sqlite3", "tempfile", "shutil", "glob", "io", "pickle",
    "struct", "zlib", "gzip", "bz2", "lzma", "zipfile", "tarfile", "fnmatch",
    "getopt", "optparse", "configparser", "pathlib", "stat", "fileinput",
    "shelve", "dbm", "weakref", "copy", "pprint", "reprlib", "enum", "types",
    "inspect", "ast", "traceback", "linecache", "pickletools", "dis", "code",
    "codeop", "pdb", "profile", "cProfile", "timeit", "doctest", "unittest",
    "pkgutil", "modulefinder", "runpy", "importlib", "sysconfig", "contextlib",
    "abc", "atexit", "sched", "queue", "_thread", "_dummy_thread", "select",
    "selectors", "asyncore", "asynchat", "signal", "mmap", "errno", "ctypes",
    "threading", "multiprocessing", "concurrent", "subprocess", "os", "io",
    "time", "random", "bisect", "array", "weakref", "copy", "pprint", "reprlib",
    "enum", "graphlib", "typing", "dataclasses"
}

def extract_imports(file_path):
    """从文件中提取导入的模块，支持更多AST节点类型"""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            # 尝试检测文件编码
            if not content.strip():
                return set()
            tree = ast.parse(content, filename=file_path)
    except Exception as e:
        logger.warning(f"⚠️ 解析文件失败 {file_path}: {str(e)}")
        return set()

    imported_modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                # 处理子模块导入 (import a.b.c as abc)
                module_name = alias.name.split('.')[0]
                imported_modules.add(module_name)
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.level == 0:  # 只处理绝对导入
                # 处理从包中导入 (from a.b import c)
                module_name = node.module.split('.')[0]
                imported_modules.add(module_name)
            # 处理相对导入 (from . import module)
            elif node.level > 0:
                # 尝试从文件路径推断包名
                dir_path = os.path.dirname(file_path)
                package_name = os.path.basename(dir_path)
                if package_name and package_name not in IGNORED_DIRS:
                    imported_modules.add(package_name)
    
    return imported_modules

def get_installed_packages():
    """获取已安装的包及其版本，使用更可靠的元数据"""
    installed = {}
    for dist in pkg_resources.working_set:
        # 使用小写名称作为键以确保一致性
        key = dist.key.lower()
        installed[key] = dist.version
        
        # 添加项目名称作为备用键
        project_name = dist.project_name.lower()
        if project_name != key:
            installed[project_name] = dist.version
    
    return installed

def is_stdlib(module_name):
    """更可靠的标准库检测方法"""
    # 首先检查已知标准库列表
    if module_name in STDLIB_MODULES:
        return True
    
    # 检查内置模块
    if module_name in sys.builtin_module_names:
        return True
    
    try:
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            return False
        
        # 检查模块来源
        if spec.origin in ("built-in", None):
            return True
        if "frozen" in str(spec.origin):
            return True
        
        # 检查标准库路径
        stdlib_paths = [
            sysconfig.get_path("stdlib"),
            sysconfig.get_path("platstdlib"),
            sysconfig.get_path("purelib"),
        ]
        
        # 过滤掉空路径
        stdlib_paths = [p for p in stdlib_paths if p]
        
        if not stdlib_paths:
            return False
        
        # 检查模块路径是否在标准库目录下
        origin_path = spec.origin
        for stdlib_path in stdlib_paths:
            if origin_path.startswith(stdlib_path):
                return True
                
    except (ImportError, AttributeError, TypeError, ValueError):
        pass
    
    return False

def resolve_module_to_package(module_name):
    """将模块名解析为包名，使用更全面的策略"""
    # 首先检查别名映射
    if module_name in MODULE_ALIASES:
        return MODULE_ALIASES[module_name]
    
    # 尝试使用小写版本
    module_lower = module_name.lower()
    if module_lower in MODULE_ALIASES:
        return MODULE_ALIASES[module_lower]
    
    # 尝试从已安装包中查找
    try:
        # 创建模块名到包名的映射
        module_to_pkg = {}
        for dist in pkg_resources.working_set:
            try:
                # 获取包提供的所有模块
                pkg_modules = set()
                if dist.has_metadata('top_level.txt'):
                    top_level = dist.get_metadata('top_level.txt').splitlines()
                    pkg_modules.update(t.strip() for t in top_level if t.strip())
                
                # 添加包名本身
                pkg_modules.add(dist.key)
                
                # 添加到映射
                for mod in pkg_modules:
                    mod_key = mod.lower()
                    if mod_key not in module_to_pkg:
                        module_to_pkg[mod_key] = dist.key
            
            except Exception:
                continue
        
        # 尝试查找匹配
        if module_lower in module_to_pkg:
            return module_to_pkg[module_lower]
        
        # 尝试直接获取版本信息
        try:
            get_version(module_name)
            return module_name
        except pkg_resources.DistributionNotFound:
            pass
    
    except Exception as e:
        logger.debug(f"解析模块包名时出错: {module_name}, {e}")
    
    # 作为最后手段，返回原始模块名
    return module_name

def match_imports_to_packages(imports):
    """将导入的模块匹配到包和版本，使用更智能的匹配策略"""
    installed = get_installed_packages()
    result = []
    unresolved = set()
    
    # 先处理所有导入
    for mod in imports:
        mod_lower = mod.lower()
        
        # 跳过标准库
        if is_stdlib(mod_lower):
            continue
        
        # 解析为包名
        pip_name = resolve_module_to_package(mod_lower)
        if not pip_name:
            unresolved.add(mod)
            continue
        
        # 尝试查找已安装的版本
        found = False
        for key in [pip_name, pip_name.lower(), pip_name.replace("-", "_"), pip_name.replace("_", "-")]:
            if key in installed:
                result.append((pip_name, installed[key]))
                found = True
                break
        
        if not found:
            unresolved.add(mod)
    
    # 报告未解析的模块
    if unresolved:
        logger.warning(f"⚠️ 无法解析的模块: {', '.join(sorted(unresolved))}")
    
    return result

def collect_all_files(path):
    """收集所有支持的文件，包括子目录"""
    all_files = []
    for root, dirs, files in os.walk(path):
        # 过滤忽略的目录
        dirs[:] = [d for d in dirs if d.lower() not in [d.lower() for d in IGNORED_DIRS]]
        
        for file in files:
            # 检查文件扩展名
            ext = os.path.splitext(file)[1].lower()
            if ext in SUPPORTED_EXTENSIONS:
                # 跳过忽略的文件
                if file.lower() not in [f.lower() for f in IGNORED_FILES]:
                    all_files.append(os.path.join(root, file))
    
    return all_files

def export_requirements(requirements, output_path):
    """导出requirements.txt文件，处理重复项"""
    if not requirements:
        logger.warning("⚠️ 未找到有效依赖")
        return
    
    # 合并重复的包（保留最高版本？但这里我们保留第一个找到的版本）
    pkg_versions = {}
    for name, version in requirements:
        name_lower = name.lower()
        if name_lower not in pkg_versions:
            pkg_versions[name_lower] = (name, version)
    
    # 按包名排序
    sorted_reqs = sorted(pkg_versions.values(), key=lambda x: x[0].lower())
    
    # 写入文件
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("# 自动生成的依赖列表\n")
            f.write("\n".join(f"{name}=={version}" for name, version in sorted_reqs))
        logger.info(f"✅ requirements.txt 已写入: {output_path}")
    except Exception as e:
        logger.error(f"❌ 写入requirements.txt失败: {str(e)}")

def export_pyproject_toml(requirements, output_path, name):
    """导出pyproject.toml文件，包含更多元数据"""
    if not requirements:
        logger.warning("⚠️ 未找到有效依赖，跳过pyproject.toml生成")
        return
    
    # 获取Python版本
    py_ver = f">={sys.version_info.major}.{sys.version_info.minor}"
    
    # 合并重复的包
    pkg_versions = {}
    for name, version in requirements:
        name_lower = name.lower()
        if name_lower not in pkg_versions:
            pkg_versions[name_lower] = (name, version)
    
    # 准备内容
    content = [
        "[project]",
        f'name = "{name}"',
        'version = "0.1.0"',
        'description = "自动生成的项目"',
        'readme = "README.md"',
        f'requires-python = "{py_ver}"',
        "",
        "dependencies = ["
    ]
    
    # 添加依赖
    for name, version in sorted(pkg_versions.values(), key=lambda x: x[0].lower()):
        content.append(f'    "{name}=={version}",')
    
    content.append("]")
    
    # 添加构建系统信息
    content.extend([
        "",
        "[build-system]",
        'requires = ["setuptools>=61.0.0", "wheel"]',
        'build-backend = "setuptools.build_meta"',
    ])
    
    # 写入文件
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(content))
        logger.info(f"✅ pyproject.toml 已写入: {output_path}")
    except Exception as e:
        logger.error(f"❌ 写入pyproject.toml失败: {str(e)}")

def analyze_project(path):
    """分析项目目录或单个文件"""
    if os.path.isfile(path):
        # 单个文件分析
        logger.info(f"🔍 分析单个文件: {path}")
        imports = extract_imports(path)
        return match_imports_to_packages(imports)
    
    elif os.path.isdir(path):
        # 项目目录分析
        logger.info(f"🔍 扫描项目目录: {path}")
        all_files = collect_all_files(path)
        logger.info(f"找到 {len(all_files)} 个代码文件")
        
        all_imports = set()
        for file_path in all_files:
            file_imports = extract_imports(file_path)
            all_imports.update(file_imports)
        
        return match_imports_to_packages(all_imports)
    
    else:
        logger.error(f"❌ 无效路径: {path}")
        return []

def main():
    parser = argparse.ArgumentParser(
        description="智能Python依赖分析工具 - 从代码生成requirements.txt和pyproject.toml",
        epilog="示例: python depfinder.py my_project/"
    )
    parser.add_argument("target", help="Python脚本或项目目录路径")
    parser.add_argument("-v", "--verbose", action="store_true", help="显示详细输出")
    parser.add_argument("-o", "--output", help="指定输出目录（默认为输入目录）")
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    path = os.path.abspath(args.target)
    if not os.path.exists(path):
        logger.error(f"❌ 路径不存在: {path}")
        sys.exit(1)
    
    # 确定输出目录
    output_dir = args.output or os.path.dirname(path) if os.path.isfile(path) else path
    os.makedirs(output_dir, exist_ok=True)
    
    # 分析项目
    requirements = analyze_project(path)
    
    # 确定项目名称
    if os.path.isfile(path):
        name = os.path.splitext(os.path.basename(path))[0]
    else:
        name = os.path.basename(os.path.abspath(path)) or "project"
    
    # 导出结果
    export_requirements(requirements, os.path.join(output_dir, "requirements.txt"))
    export_pyproject_toml(requirements, os.path.join(output_dir, "pyproject.toml"), name)
    
    logger.info("✅ 依赖分析完成")

if __name__ == "__main__":
    main()