#!/usr/bin/env python3

import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def to_pascal_case(name: str) -> str:
    return "".join(part.capitalize() for part in name.split("_"))


def main() -> None:
    if len(sys.argv) != 3:
        print(
            f"usage: {sys.argv[0]} <config.xml> <output.hpp>",
            file=sys.stderr,
        )
        sys.exit(1)

    config_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    tree = ET.parse(config_path)
    root = tree.getroot()

    component_section = root.find("component")

    if component_section is None:
        raise ValueError("No <component> section found in config.xml")

    component_data = []

    for component in component_section:
        name = component.tag

        id_element = component.find("id")

        if id_element is None:
            raise ValueError(f"Component '{name}' is missing an 'id'")

        try:
            component_id = int(id_element.text)
        except (TypeError, ValueError):
            raise ValueError(f"Component '{name}' has a non-integer id")

        if not 0 <= component_id <= 255:
            raise ValueError(f"Component '{name}' id must be between 0 and 255")

        component_data.append((name, component_id))

    if not component_data:
        raise ValueError("No components found in config.xml")

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
