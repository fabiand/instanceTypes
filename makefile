
RESOURCES := $(shell find series/ -print)

.PHONY: $(RESOURCES)

all: instanceTypes.yaml README.md

instanceTypes.yaml: $(RESOURCES)
	kubectl kustomize series > $@

README.md: instanceTypes.yaml
	python3 hacks/docs.py > $@
