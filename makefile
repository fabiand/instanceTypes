
instanceTypes.yaml: instanceTypes $(shell find instanceTypes/ -print)
	kubectl kustomize instanceTypes > $@

preferences.yaml:
	kubectl kustomize preferences > $@
