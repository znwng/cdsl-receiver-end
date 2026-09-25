# CDSL Arduino Receiver

Reads `~/.config/cdsl/config.toml` and generates `component_config.hpp` for `receiver.ino`.

```text
config.toml → generate_config.py → component_config.hpp → receiver.ino
```

```bash
make                              # Debug, keeps generated header, compiles and flashes the code
make BUILD_TYPE=Release           # Release, removes generated header and the rest same as above
make generate                     # Generate header only
make clean                        # Remove generated header
```
