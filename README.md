# CDSL Arduino Receiver

Reads `~/.config/cdsl/config.xml` and generates `component_config.hpp` for `receiver.ino`.

```text
config.xml → generate_config.py → component_config.hpp → receiver.ino
```

```bash
make          # Generate header, compile, and flash
make generate # Generate component_config.hpp only
make compile  # Compile the receiver
make flash    # Flash the receiver
make clean    # Remove generated component_config.hpp
```
