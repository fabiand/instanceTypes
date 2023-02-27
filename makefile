
RESOURCES := $(shell find instanceTypes -print)

.PHONY: $(RESOURCES)

all: instanceTypes.yaml instanceTypes.md

instanceTypes.yaml: $(RESOURCES)
	kubectl kustomize instanceTypes > $@

README.md: instanceTypes.yaml
	python3 hacks/docs.py > $@
