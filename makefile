
RESOURCES := $(shell find series/ -print)

.PHONY: $(RESOURCES)

all: instanceTypes.yaml README.md

instanceTypes.yaml: $(RESOURCES)
	kubectl kustomize series > $@

clusterInstanceTypes.yaml: instanceTypes.yaml
	kubectl kustomize --load-restrictor=LoadRestrictionsNone cluster > $@

README.md: instanceTypes.yaml
	python3 hacks/docs.py > $@
