def convert_memory_to_byte(memory):
    memory = memory.lower()  
    if memory is None or memory == '':
        memory = 0
    if "tb" in memory:
        number = float(memory.replace("tb", "")) * 1024**4  # 1TB = 1024^4 bytes
    elif "gb" in memory:
        number = float(memory.replace("gb", "")) * 1024**3  # 1GB = 1024^3 bytes
    elif "mb" in memory:
        number = float(memory.replace("mb", "")) * 1024**2  # 1MB = 1024^2 bytes
    elif "kb" in memory:
        number = float(memory.replace("kb", "")) * 1024  # 1KB = 1024 bytes
    else:
        try:
            number = float(memory)
        except ValueError:
            raise ValueError("Cannot convert memory to number")

    return int(number)


def convert_byte_to_memory(bytes):
    bytes = int(bytes)
    if bytes >= 1024**4:  # 1TB = 1024^4 bytes
        memory = f"{bytes / 1024**4:.2f}TB"
    elif bytes >= 1024**3:  # 1GB = 1024^3 bytes
        memory = f"{bytes / 1024**3:.2f}GB"
    elif bytes >= 1024**2:  # 1MB = 1024^2 bytes
        memory = f"{bytes / 1024**2:.2f}MB"
    elif bytes >= 1024:  # 1KB = 1024 bytes
        memory = f"{bytes / 1024:.2f}KB"
    else:
        memory = f"{bytes} bytes"

    return memory


def convert_byte_to_gb(bytes):
    if bytes is None:
        return 0
    gb_value = float(bytes) / (1024**3)
    return f"{gb_value:.1f}"


def convert_byte_to_mb(bytes):
    if bytes is None:
        return 0
    mb_value = float(bytes) / (1024**2)
    return f"{mb_value:.1f}"


def convert_mb_to_byte(mb):
    if mb is None:
        return 0
    byte_value = int(mb) * (1024**2)
    return byte_value


def convert_mb_to_gb(mb: float) -> float:
    """
    Convert megabytes (MB) to gigabytes (GB).

    :param mb: The value in megabytes.
    :return: The value converted to gigabytes.
    """
    gb = mb / 1024.0
    return round(gb, 1)


def convert_to_bytes(size_str):
    size_str = str(size_str).strip().lower()

    if size_str.endswith("tb") or size_str.endswith("t"):
        size = (
            float(size_str[: -1 if size_str.endswith("t") else -2]) * 1024**4
        )  # Chuyển từ TB sang byte (1 TB = 1024^4 byte)
    elif size_str.endswith("gb") or size_str.endswith("g"):
        size = (
            float(size_str[: -1 if size_str.endswith("g") else -2]) * 1024**3
        )  # Chuyển từ GB sang byte (1 GB = 1024^3 byte)
    elif size_str.endswith("mb") or size_str.endswith("m"):
        size = (
            float(size_str[: -1 if size_str.endswith("m") else -2]) * 1024**2
        )  # Chuyển từ MB sang byte (1 MB = 1024^2 byte)
    elif size_str.endswith("kb") or size_str.endswith("k"):
        size = (
            float(size_str[: -1 if size_str.endswith("k") else -2]) * 1024
        )  # Chuyển từ KB sang byte (1 KB = 1024 byte)
    else:
        return float(size_str)
    return size


def convert_gb_to_byte(gb):
    byte = gb * (1024**3)
    return byte
