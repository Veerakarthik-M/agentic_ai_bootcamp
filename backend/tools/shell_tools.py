"""
Shell, Process, and File System Management Tools for Windows OS.
Enables agents to safely execute PowerShell/CMD commands, inspect & manage processes,
manipulate files, and query hardware/system stats.
"""

import os
import subprocess
import shutil
import psutil
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("shell_tools")
logger.setLevel(logging.INFO)


def execute_powershell(command: str, timeout_seconds: int = 30, cwd: Optional[str] = None) -> Dict[str, Any]:
    """
    Safely executes a PowerShell command and returns output, return code, and error state.
    """
    try:
        process = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", command],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            cwd=cwd
        )
        return {
            "status": "success" if process.returncode == 0 else "failed",
            "returncode": process.returncode,
            "stdout": process.stdout.strip(),
            "stderr": process.stderr.strip()
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "returncode": -1,
            "stdout": "",
            "stderr": f"Command timed out after {timeout_seconds} seconds"
        }
    except Exception as e:
        return {
            "status": "error",
            "returncode": -1,
            "stdout": "",
            "stderr": str(e)
        }


def list_processes(filter_name: Optional[str] = None, limit: int = 25) -> List[Dict[str, Any]]:
    """
    List running processes on the system, optionally filtered by executable name.
    """
    procs = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
        try:
            info = proc.info
            name = info.get('name') or ''
            if filter_name and filter_name.lower() not in name.lower():
                continue
            procs.append({
                "pid": info['pid'],
                "name": name,
                "cpu_percent": info.get('cpu_percent') or 0.0,
                "memory_percent": round(info.get('memory_percent') or 0.0, 2),
                "status": info.get('status')
            })
            if len(procs) >= limit:
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return procs


def start_process(executable: str, args: Optional[List[str]] = None, cwd: Optional[str] = None) -> Dict[str, Any]:
    """
    Launches a local application or background process (e.g. notepad.exe, calc.exe).
    """
    cmd = [executable]
    if args:
        cmd.extend(args)

    try:
        proc = subprocess.Popen(cmd, cwd=cwd)
        return {
            "status": "success",
            "pid": proc.pid,
            "executable": executable,
            "args": args or []
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


def kill_process(pid: int) -> Dict[str, Any]:
    """
    Terminates a process by its PID.
    """
    try:
        proc = psutil.Process(pid)
        proc_name = proc.name()
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except psutil.TimeoutExpired:
            proc.kill()
        return {"status": "success", "pid": pid, "name": proc_name}
    except psutil.NoSuchProcess:
        return {"status": "not_found", "pid": pid}
    except psutil.AccessDenied:
        return {"status": "access_denied", "pid": pid}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def search_files(directory: str, pattern: str = "*", recursive: bool = True, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Search for files matching pattern in a directory.
    """
    import fnmatch
    results = []
    if not os.path.exists(directory):
        return []

    if recursive:
        for root, _, files in os.walk(directory):
            for filename in files:
                if fnmatch.fnmatch(filename.lower(), pattern.lower()):
                    full_path = os.path.join(root, filename)
                    try:
                        stat = os.stat(full_path)
                        results.append({
                            "name": filename,
                            "path": full_path,
                            "size_bytes": stat.st_size,
                            "modified": stat.st_mtime
                        })
                    except Exception:
                        pass
                    if len(results) >= limit:
                        return results
    else:
        for filename in os.listdir(directory):
            if fnmatch.fnmatch(filename.lower(), pattern.lower()):
                full_path = os.path.join(directory, filename)
                if os.path.isfile(full_path):
                    try:
                        stat = os.stat(full_path)
                        results.append({
                            "name": filename,
                            "path": full_path,
                            "size_bytes": stat.st_size,
                            "modified": stat.st_mtime
                        })
                    except Exception:
                        pass
                    if len(results) >= limit:
                        return results
    return results


def organize_directory_by_extension(target_directory: str) -> Dict[str, Any]:
    """
    Organizes unorganized files into category subdirectories (e.g. Documents, Images, Archives, Spreadsheets).
    """
    if not os.path.exists(target_directory):
        return {"status": "error", "message": "Directory does not exist"}

    category_map = {
        "Documents": [".pdf", ".docx", ".doc", ".txt", ".md", ".rtf"],
        "Spreadsheets": [".xlsx", ".xls", ".csv"],
        "Images": [".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg"],
        "Archives": [".zip", ".tar", ".gz", ".7z", ".rar"],
        "Code": [".py", ".js", ".ts", ".html", ".css", ".json", ".yaml", ".yml"],
        "Installers": [".exe", ".msi"]
    }

    moved_count = 0
    categories_used = set()

    for item in os.listdir(target_directory):
        item_path = os.path.join(target_directory, item)
        if os.path.isfile(item_path):
            _, ext = os.path.splitext(item)
            ext = ext.lower()

            target_folder = "Others"
            for cat, extensions in category_map.items():
                if ext in extensions:
                    target_folder = cat
                    break

            cat_dir = os.path.join(target_directory, target_folder)
            os.makedirs(cat_dir, exist_ok=True)
            try:
                shutil.move(item_path, os.path.join(cat_dir, item))
                moved_count += 1
                categories_used.add(target_folder)
            except Exception as e:
                logger.error(f"Failed to move {item}: {e}")

    return {
        "status": "success",
        "moved_files": moved_count,
        "categories_created": list(categories_used)
    }


def get_system_resources() -> Dict[str, Any]:
    """
    Returns live CPU, Memory, Disk, and Battery diagnostics of the laptop.
    """
    cpu_percent = psutil.cpu_percent(interval=0.1)
    virtual_mem = psutil.virtual_memory()
    disk = psutil.disk_usage('C:\\' if os.name == 'nt' else '/')

    battery_info = {}
    if hasattr(psutil, "sensors_battery"):
        bat = psutil.sensors_battery()
        if bat:
            battery_info = {
                "percent": bat.percent,
                "power_plugged": bat.power_plugged,
                "seconds_left": bat.secsleft
            }

    return {
        "cpu_percent": cpu_percent,
        "memory": {
            "total_gb": round(virtual_mem.total / (1024**3), 2),
            "used_gb": round(virtual_mem.used / (1024**3), 2),
            "percent": virtual_mem.percent
        },
        "disk_c": {
            "total_gb": round(disk.total / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "percent_used": disk.percent
        },
        "battery": battery_info
    }
