def get_single_lightning_gpu_device_from_torch_gpu_string(torch_gpu_string: str) -> str:
    """
    从torch字符串中获取单个GPU设备
    """
    if torch_gpu_string.startswith("cuda"):
        return {"accelerator": "gpu", "devices": [torch_gpu_string.split(":")[1]]}
    else:
        raise ValueError(f"不支持的设备: {torch_gpu_string}")
