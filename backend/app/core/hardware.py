from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import os
import platform
import shutil
import subprocess
from functools import lru_cache
from typing import Any


class Accelerator(str, Enum):
    CPU = "cpu"
    CUDA = "cuda"
    ROCM = "rocm"
    METAL = "metal"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class HardwareProfile:
    accelerator: Accelerator
    platform: str
    arch: str
    details: dict[str, Any]


def _run_command(cmd: list[str]) -> tuple[bool, str]:
    if not shutil.which(cmd[0]):
        return False, ""
    try:
        completed = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
        )
        return completed.returncode == 0, completed.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False, ""


def _detect_cuda() -> tuple[bool, int]:
    ok, output = _run_command(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"])
    if not ok or not output:
        return False, 0
    devices = [line for line in output.splitlines() if line.strip()]
    return True, len(devices)


def _detect_rocm() -> tuple[bool, int]:
    ok, output = _run_command(["rocm-smi", "--showproductname"])
    if not ok or not output:
        return False, 0
    devices = [line for line in output.splitlines() if "card" in line.lower()]
    return True, len(devices)


def _is_apple_silicon(system: str, machine: str) -> bool:
    return system == "Darwin" and machine.lower() in {"arm64", "arm64e"}


@lru_cache(maxsize=1)
def detect_hardware() -> HardwareProfile:
    override = os.getenv("ACCELERATOR_OVERRIDE")
    if override:
        try:
            accel = Accelerator(override.lower())
        except ValueError:
            accel = Accelerator.UNKNOWN
        return HardwareProfile(
            accelerator=accel,
            platform=platform.system(),
            arch=platform.machine(),
            details={"source": "override"},
        )

    system = platform.system()
    arch = platform.machine()
    details: dict[str, Any] = {"system": system, "arch": arch}

    has_cuda, cuda_devices = _detect_cuda()
    if has_cuda:
        details["cuda_devices"] = cuda_devices
        return HardwareProfile(Accelerator.CUDA, system, arch, details)

    has_rocm, rocm_devices = _detect_rocm()
    if has_rocm:
        details["rocm_devices"] = rocm_devices
        return HardwareProfile(Accelerator.ROCM, system, arch, details)

    if _is_apple_silicon(system, arch):
        details["apple_silicon"] = True
        return HardwareProfile(Accelerator.METAL, system, arch, details)

    return HardwareProfile(Accelerator.CPU, system, arch, details)
