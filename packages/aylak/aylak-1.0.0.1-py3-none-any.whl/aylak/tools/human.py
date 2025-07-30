from typing import List, Union
import asyncio


class HumanTools:
    def __init__(self):
        pass

    async def TimeFormatter(self, milliseconds: int) -> str:
        seconds, milliseconds = divmod(int(milliseconds), 1000)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        tmp = (
            ((str(days) + "g, ") if days else "")
            + ((str(hours) + "s, ") if hours else "")
            + ((str(minutes) + "dk, ") if minutes else "")
            + ((str(seconds) + "sn, ") if seconds else "")
            + ((str(milliseconds) + "ms, ") if milliseconds else "")
        )
        return tmp[:-2]

    async def convertDataToBytes(
        self,
        kb: int | float = 0,
        mb: int | float = 0,
        gb: int | float = 0,
        tb: int | float = 0,
        pb: int | float = 0,
        eb: int | float = 0,
        zb: int | float = 0,
        yb: int | float = 0,
    ) -> int:
        return int(
            kb * 1024
            + mb * 1024**2
            + gb * 1024**3
            + tb * 1024**4
            + pb * 1024**5
            + eb * 1024**6
            + zb * 1024**7
            + yb * 1024**8
        )

    def humanbytes(bytes: int, metric: bool = False, precision: int = 1) -> str:
        return HumanBytes.format(bytes, metric, precision)


class HumanBytes:
    METRIC_LABELS: List[str] = ["B", "kB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
    BINARY_LABELS: List[str] = [
        "B",
        "KiB",
        "MiB",
        "GiB",
        "TiB",
        "PiB",
        "EiB",
        "ZiB",
        "YiB",
    ]
    PRECISION_OFFSETS: List[float] = [
        0.5,
        0.05,
        0.005,
        0.0005,
        0.00005,
        0.000005,
        0.0000005,
        0.00000005,
        0.000000005,
        0.0000000005,
        0.00000000005,
    ]
    PRECISION_FORMATS: List[str] = [
        "{}{:.0f} {}",
        "{}{:.1f} {}",
        "{}{:.2f} {}",
        "{}{:.3f} {}",
        "{}{:.4f} {}",
        "{}{:.5f} {}",
        "{}{:.6f} {}",
        "{}{:.7f} {}",
        "{}{:.8f} {}",
        "{}{:.9f} {}",
        "{}{:.10f} {}",
    ]

    @staticmethod
    def format(num: Union[int, float], metric: bool = False, precision: int = 1) -> str:

        assert isinstance(num, (int, float)), "num değeri int veya float olmalıdır"
        assert isinstance(metric, bool), "metric değeri bool olmalıdır"
        assert (
            isinstance(precision, int) and precision >= 0 and precision <= 10
        ), "precision değeri 0 ile 10 arasında bir tamsayı olmalıdır"

        unit_labels = HumanBytes.METRIC_LABELS if metric else HumanBytes.BINARY_LABELS
        last_label = unit_labels[-1]
        unit_step = 1000 if metric else 1024
        unit_step_thresh = unit_step - HumanBytes.PRECISION_OFFSETS[precision]

        is_negative = num < 0
        if is_negative:  # Faster than ternary assignment or always running abs().
            num = abs(num)

        for unit in unit_labels:
            if num < unit_step_thresh:
                break
            if unit != last_label:
                num /= unit_step

        return HumanBytes.PRECISION_FORMATS[precision].format(
            "-" if is_negative else "", num, unit
        )
