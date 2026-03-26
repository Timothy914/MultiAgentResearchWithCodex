from dyco_repair.runtime import GpuInfo, parse_gpu_query_output, select_best_gpu


def test_parse_gpu_query_output() -> None:
    raw = "0, 1200, 46068, 20\n7, 293, 46068, 0\n"
    gpus = parse_gpu_query_output(raw)
    assert [gpu.index for gpu in gpus] == [0, 7]
    assert gpus[1].memory_used_mib == 293


def test_select_best_gpu_prefers_lower_memory_and_utilization() -> None:
    gpus = [
        GpuInfo(index=0, memory_used_mib=1000, memory_total_mib=46068, utilization_gpu=20),
        GpuInfo(index=6, memory_used_mib=4, memory_total_mib=46068, utilization_gpu=0),
        GpuInfo(index=7, memory_used_mib=293, memory_total_mib=46068, utilization_gpu=0),
    ]
    selected = select_best_gpu(gpus, max_memory_used_mib=2048, max_utilization=10)
    assert selected is not None
    assert selected.index == 6
