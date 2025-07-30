import datetime as dt
import re


def expect_boolean(data: object) -> bool:
    if not isinstance(data, bool):
        raise TypeError(f"Expected bool, got {type(data).__name__}")

    return data


def expect_integer(data: object) -> int:
    if not isinstance(data, int):
        raise TypeError(f"Expected int, got {type(data).__name__}")

    return data


def expect_string(data: object) -> str:
    if not isinstance(data, str):
        raise TypeError(f"Expected str, got {type(data).__name__}")

    return data


def expect_date(data: object) -> dt.date:
    if not isinstance(data, str):
        raise TypeError(f"Expected str, got {type(data).__name__}")

    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", data)
    if not m:
        raise ValueError(f'Invalid date: "{data}"')

    return dt.date(int(m[1]), int(m[2]), int(m[3]))


def expect_time(data: object) -> dt.datetime:
    if not isinstance(data, str):
        raise TypeError(f"Expected str, got {type(data).__name__}")

    return dt.datetime.strptime(data, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=dt.timezone.utc)


def expect_record(data: object) -> dict[str, object]:
    if not isinstance(data, dict):
        raise TypeError(f"Expected dict, got {type(data).__name__}")

    return data  # pyright: ignore [reportUnknownVariableType]


def expect_list(data: object) -> list[object]:
    if not isinstance(data, list):
        raise TypeError(f"Expected list, got {type(data).__name__}")

    return data  # pyright: ignore [reportUnknownVariableType]


def expect_record_list(data: object) -> list[dict[str, object]]:
    return [expect_record(it) for it in expect_list(data)]
