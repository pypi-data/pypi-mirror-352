from json import dumps
from tabulate import tabulate
from ._identities import generate_identity


class Static(object):
    identity = {"User-Agent": generate_identity()}

    def __init__(self, custom_json) -> None:
        super().__init__()
        self.custom_json = custom_json

    def visualize(self, indentation: int = 2, alphabetical: bool = False) -> str | None:
        return (
            dumps(
                self.custom_json,
                indent=indentation,
                sort_keys=alphabetical,
                ensure_ascii=False,
            )
            if self.custom_json
            else None
        )

    def table(self, table_format: str = "psql") -> str | None:
        try:
            return (
                tabulate(
                    self.custom_json["data"], headers="keys", tablefmt=table_format
                )
                if self.custom_json
                else None
            )
        except TypeError:
            return None
