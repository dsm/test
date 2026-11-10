# CAN DBC -> C generator: generation and verification entry points.

PYTHON ?= python3
DBC    ?= dbc/example_vehicle.dbc
NODES  ?= --node VCU --node BMS --node MCU --node DISPLAY:rx

.PHONY: generate test verify mutation clean

# Regenerate the committed example code.
generate:
	PYTHONPATH=generator $(PYTHON) -m dbcgen --dbc $(DBC) --out generated $(NODES)

# Complete suite with the reference build only (fast).
test:
	$(PYTHON) -m pytest tests/verification -q

# Complete campaign: all build variants, coverage gate, report.
verify:
	$(PYTHON) tools/run_verification.py

# Complete campaign including the mutation check (slow).
mutation:
	$(PYTHON) tools/run_verification.py --mutation

clean:
	rm -rf build .pytest_cache
