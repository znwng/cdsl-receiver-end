CONFIG := $(HOME)/.config/cdsl/config.toml
GENERATED := component_config.hpp
GENERATOR := generate_config.py

FQBN ?= arduino:avr:uno
PORT ?= /dev/ttyUSB0

BUILD_TYPE ?= Debug

ifeq ($(BUILD_TYPE),Release)
KEEP_GENERATED := false
else ifeq ($(BUILD_TYPE),Debug)
KEEP_GENERATED := true
else
$(error Invalid BUILD_TYPE='$(BUILD_TYPE)'. Use BUILD_TYPE=Release or BUILD_TYPE=Debug)
endif

.PHONY: all generate compile upload clean

all: upload

generate:
	python3 $(GENERATOR) $(CONFIG) $(GENERATED)

compile: generate
	arduino-cli compile \
		--fqbn $(FQBN) \
		.

	$(if $(filter false,$(KEEP_GENERATED)),rm -f $(GENERATED))

upload: compile
	arduino-cli upload \
		-p $(PORT) \
		--fqbn $(FQBN) \
		.

	$(if $(filter false,$(KEEP_GENERATED)),rm -f $(GENERATED))

clean:
	rm -f $(GENERATED)
