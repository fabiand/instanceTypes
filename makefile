
RESOURCES := $(shell find instanceTypes -print)

.PHONY: $(RESOURCES)

all: instanceTypes.yaml instanceTypes.txt

instanceTypes.yaml: $(RESOURCES)
	kubectl kustomize instanceTypes > $@

instanceTypes.txt: instanceTypes.yaml
	python3 hacks/docs.py > $@
