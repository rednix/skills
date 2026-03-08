# -*- coding: utf-8 -*-

import json
import os
import platform
import shutil
import subprocess
import sys


def print_json(payload, exit_code=0):
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if exit_code:
        sys.exit(exit_code)


def has_command(name):
    return shutil.which(name) is not None


def as_command_text(command):
    return " ".join(command)


def linux_privilege_prefix():
    if os.name == "nt":
        return []
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        return []
    if has_command("sudo"):
        return ["sudo"]
    return None


def build_install_plan():
    ffmpeg_path = shutil.which("ffmpeg")
    ffprobe_path = shutil.which("ffprobe")
    if ffmpeg_path and ffprobe_path:
        return {
            "status": "already_available",
            "platform": platform.system(),
            "ffmpeg_path": ffmpeg_path,
            "ffprobe_path": ffprobe_path,
            "source_policy": "package_manager_only",
        }

    system = platform.system()

    if system == "Darwin":
        if has_command("brew"):
            return {
                "status": "installable",
                "platform": system,
                "package_manager": "brew",
                "source_policy": "package_manager_only",
                "avoid": ["github-direct", "npm", "manual-zip-download"],
                "commands": [["brew", "install", "ffmpeg"]],
            }
        return {
            "status": "blocked",
            "platform": system,
            "reason": "homebrew_not_found",
            "message": "No supported local package manager was found. Do not bootstrap Homebrew via a GitHub install script inside this skill.",
            "source_policy": "package_manager_only",
        }

    if system == "Windows":
        if has_command("winget"):
            return {
                "status": "installable",
                "platform": system,
                "package_manager": "winget",
                "source_policy": "package_manager_only",
                "avoid": ["github-direct", "npm", "manual-zip-download"],
                "commands": [[
                    "winget",
                    "install",
                    "--id",
                    "Gyan.FFmpeg",
                    "-e",
                    "--accept-source-agreements",
                    "--accept-package-agreements",
                ]],
            }
        if has_command("choco"):
            return {
                "status": "installable",
                "platform": system,
                "package_manager": "choco",
                "source_policy": "package_manager_only",
                "avoid": ["github-direct", "npm", "manual-zip-download"],
                "commands": [["choco", "install", "ffmpeg", "-y"]],
            }
        return {
            "status": "blocked",
            "platform": system,
            "reason": "package_manager_not_found",
            "message": "No supported Windows package manager was found. Do not fall back to npm or manual GitHub downloads.",
            "source_policy": "package_manager_only",
        }

    prefix = linux_privilege_prefix()
    if has_command("apt-get") and prefix is not None:
        return {
            "status": "installable",
            "platform": system,
            "package_manager": "apt-get",
            "source_policy": "package_manager_only",
            "avoid": ["github-direct", "npm", "manual-zip-download"],
            "commands": [
                prefix + ["apt-get", "update"],
                prefix + ["apt-get", "install", "-y", "ffmpeg"],
            ],
        }
    if has_command("dnf") and prefix is not None:
        return {
            "status": "installable",
            "platform": system,
            "package_manager": "dnf",
            "source_policy": "package_manager_only",
            "avoid": ["github-direct", "npm", "manual-zip-download"],
            "commands": [prefix + ["dnf", "install", "-y", "ffmpeg"]],
        }
    if has_command("yum") and prefix is not None:
        return {
            "status": "installable",
            "platform": system,
            "package_manager": "yum",
            "source_policy": "package_manager_only",
            "avoid": ["github-direct", "npm", "manual-zip-download"],
            "commands": [prefix + ["yum", "install", "-y", "ffmpeg"]],
        }
    if has_command("zypper") and prefix is not None:
        return {
            "status": "installable",
            "platform": system,
            "package_manager": "zypper",
            "source_policy": "package_manager_only",
            "avoid": ["github-direct", "npm", "manual-zip-download"],
            "commands": [prefix + ["zypper", "--non-interactive", "install", "ffmpeg"]],
        }

    return {
        "status": "blocked",
        "platform": system,
        "reason": "package_manager_not_found_or_no_privilege_path",
        "message": "No supported package manager path is available for autonomous installation.",
        "source_policy": "package_manager_only",
    }


def execute_plan(plan):
    steps = plan.get("commands", [])
    outputs = []
    for command in steps:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        outputs.append(
            {
                "command": as_command_text(command),
                "returncode": result.returncode,
                "stdout": result.stdout[-4000:],
                "stderr": result.stderr[-4000:],
            }
        )
        if result.returncode != 0:
            return {
                "status": "failed",
                "platform": plan.get("platform"),
                "package_manager": plan.get("package_manager"),
                "source_policy": plan.get("source_policy"),
                "steps": outputs,
            }

    ffmpeg_path = shutil.which("ffmpeg")
    ffprobe_path = shutil.which("ffprobe")
    if ffmpeg_path and ffprobe_path:
        return {
            "status": "installed",
            "platform": plan.get("platform"),
            "package_manager": plan.get("package_manager"),
            "source_policy": plan.get("source_policy"),
            "ffmpeg_path": ffmpeg_path,
            "ffprobe_path": ffprobe_path,
            "steps": outputs,
        }

    return {
        "status": "failed",
        "platform": plan.get("platform"),
        "package_manager": plan.get("package_manager"),
        "source_policy": plan.get("source_policy"),
        "message": "Installation commands finished but ffmpeg/ffprobe are still unavailable.",
        "steps": outputs,
    }


def main():
    execute = "--execute" in sys.argv[1:]

    plan = build_install_plan()
    if not execute:
        if plan.get("status") == "installable":
            plan["commands_text"] = [as_command_text(command) for command in plan["commands"]]
        print_json(plan, exit_code=0 if plan.get("status") != "blocked" else 1)

    if plan.get("status") == "already_available":
        print_json(plan)
    if plan.get("status") != "installable":
        print_json(plan, exit_code=1)

    result = execute_plan(plan)
    print_json(result, exit_code=0 if result.get("status") == "installed" else 1)


if __name__ == "__main__":
    main()
