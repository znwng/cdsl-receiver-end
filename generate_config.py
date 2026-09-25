#!/usr/bin/env python3

import sys
import tomllib
from pathlib import Path


def to_pascal_case(name: str) -> str:
    return "".join(part.capitalize() for part in name.split("_"))


def main() -> None:
    if len(sys.argv) != 3:
        print(
            f"usage: {sys.argv[0]} <config.toml> <output.hpp>",
            file=sys.stderr,
        )
        sys.exit(1)

    config_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with config_path.open("rb") as file:
        config = tomllib.load(file)

    components = config.get("component")

    if not components:
        raise ValueError("No [component.*] sections found in config.toml")

    component_data = []

    for name, data in components.items():
        if "id" not in data:
            raise ValueError(f"Component '{name}' is missing an 'id'")

        component_id = data["id"]

        if not isinstance(component_id, int):
            raise ValueError(f"Component '{name}' has a non-integer id")

        if not 0 <= component_id <= 255:
            raise ValueError(f"Component '{name}' id must be between 0 and 255")

        component_data.append((name, component_id))

    ids = [component_id for _, component_id in component_data]

    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate component IDs found")

    component_data.sort(key=lambda item: item[1])

    output = """\
#pragma once

#include <stdint.h>

enum class ComponentId : uint8_t {
"""

    for name, component_id in component_data:
        enum_name = to_pascal_case(name)
        output += f"    {enum_name} = {component_id},\n"

    output += """\
};

inline const char* component_name(ComponentId component) {
    switch (component) {
"""

    for name, _ in component_data:
        enum_name = to_pascal_case(name)

        output += f"""\
        case ComponentId::{enum_name}:
            return "{name}";

"""

    output += """\
    }

    return "unknown";
}

inline bool is_valid_component_id(uint8_t id) {
    switch (static_cast<ComponentId>(id)) {
"""

    for name, _ in component_data:
        enum_name = to_pascal_case(name)
        output += f"        case ComponentId::{enum_name}:\n"

    output += """\
            return true;
    }

    return false;
}
"""

    output_path.write_text(output)

    print(f"Generated {output_path}")


if __name__ == "__main__":
    main()
