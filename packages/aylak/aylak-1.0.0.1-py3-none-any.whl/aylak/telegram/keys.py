import random

KEYS = [
    {"b63d319588b3950a6ad531bbb162b38d": 26016190},
    {"b6060c4b9aa4725b1c65f85e4da214bb": 26552289},
    {"45a7b70fa0c9984f0bba82e77d77c183": 28853360},
    {"d97f522d1badff170babf25dc48073e2": 29928232},
    {"dd4784e8a9722f1780ad3d910c0b1736": 20055942},
    {"e9344dd447b9a930206260c9ea0f101f": 25749871},
    {"db5cd23c23a7d21a20c0ad15c196645a": 28590864},
    {"ff0ed77e7d14172f91da353c469110c8": 23312051},
    {"e045afc1ef7410e7cb2b0e5cf8064611": 13753812},
    {"d5e5f3b8e415f3c99eb6cad2c1fb666c": 23622341},
    {"78ab84d76e1ae0bf1e11d45672fbb6ec": 27166094},
    # {"fe492468db1a862b02b75a3477342658": 3477342658},
    # {"53ea88aba8b6f1a2fcd4f17252aaad78": 8365793},
]


def get_key() -> tuple:
    """
    Returns a random key from the KEYS list and its corresponding value.
    """
    key = random.choice(KEYS)
    return list(key.keys())[0], list(key.values())[0]


def get_keys_list(data_type: str = "dict") -> list:
    """
    Returns a list of keys from the KEYS list.

    Args:
        data_type (str): The type of data to return. Options are:
            `dict`: Returns a list of dictionaries.
            `list`: Returns a list of keys.
            `api_id`: Returns a list of API IDs.
            `api_hash`: Returns a list of API hashes.
            `human`: Returns a human-readable string of API IDs and hashes.

    Returns:
        list: A list of keys in the specified format.

    Raises:
        ValueError: If an invalid data_type is provided.
    """
    if data_type == "dict":
        return KEYS
    elif data_type == "list":
        return [list(key.keys())[0] for key in KEYS]
    elif data_type == "api_id":
        return [list(key.values())[0] for key in KEYS]
    elif data_type == "api_hash":
        return [list(key.keys())[0] for key in KEYS]
    elif data_type == "human":
        return "\n".join(
            [
                f"API_ID: {list(key.values())[0]}, API_HASH: {list(key.keys())[0]}"
                for key in KEYS
            ]
        )

    else:
        raise ValueError(
            "Invalid data_type. Use 'dict', 'list', 'values', 'keys', or 'human'."
        )


print(get_keys_list("human"))
