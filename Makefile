CONFIG := $(HOME)/.config/cdsl/config.toml
GENERATED := component_config.hpp
GENERATOR := generate_config.py

FQBN ?= arduino:avr:uno
PORT := $(shell python3 -c 'import tomllib; print(tomllib.load(open("$(CONFIG)", "rb"))["arduino"]["port"])')

.PHONY: all generate compile flash clean

all: generate compile flash

generate:
	python3 $(GENERATOR) $(CONFIG) $(GENERATED)

compile:
	arduino-cli compile \
		--fqbn $(FQBN) \
		.

flash:
	arduino-cli upload \
		-p $(PORT) \
		--fqbn $(FQBN) \
		.

clean:
	rm -f $(GENERATED)
