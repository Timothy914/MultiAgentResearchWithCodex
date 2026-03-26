from __future__ import annotations

from dataclasses import asdict, dataclass
import subprocess


@dataclass(frozen=True)
class GpuInfo:
    index: int
    memory_used_mib: int
    memory_total_mib: int
    utilization_gpu: int

    @property
    def memory_free_mib(self) -> int:
        return self.memory_total_mib - self.memory_used_mib

    def to_dict(self) -> dict[str, int]:
        return asdict(self)


def parse_gpu_query_output(raw: str) -> list[GpuInfo]:
    gpus: list[GpuInfo] = []
    for line in raw.strip().splitlines():
        if not line.strip():
            continue
        parts = [part.strip() for part in line.split(",")]
        if len(parts) != 4:
            continue
        gpus.append(
            GpuInfo(
                index=int(parts[0]),
                memory_used_mib=int(parts[1]),
                memory_total_mib=int(parts[2]),
                utilization_gpu=int(parts[3]),
            )
        )
    return gpus


def query_gpus() -> list[GpuInfo]:
    result = subprocess.run(
        [
            "nvidia-smi",
            "--query-gpu=index,memory.used,memory.total,utilization.gpu",
            "--format=csv,noheader,nounits",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return parse_gpu_query_output(result.stdout)


def select_best_gpu(
    gpus: list[GpuInfo],
    max_memory_used_mib: int | None = None,
    max_utilization: int | None = None,
) -> GpuInfo | None:
    candidates = list(gpus)
    if max_memory_used_mib is not None:
        candidates = [gpu for gpu in candidates if gpu.memory_used_mib <= max_memory_used_mib]
    if max_utilization is not None:
        candidates = [gpu for gpu in candidates if gpu.utilization_gpu <= max_utilization]
    if not candidates:
        candidates = list(gpus)
    if not candidates:
        return None
    return sorted(candidates, key=lambda gpu: (gpu.memory_used_mib, gpu.utilization_gpu, -gpu.memory_free_mib, gpu.index))[0]

