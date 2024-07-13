# Git
GIT_REVISION ?= $(shell git rev-parse --short HEAD)
GIT_TAG ?= $(shell git describe --tags --abbrev=0 --always | sed -e s/v//g)

# Azure CLI
SUBSCRIPTION_ID ?= $(shell az account show --query id --output tsv)
SUBSCRIPTION_NAME ?= $(shell az account show --query name --output tsv)
TENANT_ID ?= $(shell az account show --query tenantId --output tsv)

# Paramters
SCENARIO ?= event-grid-mqtt-messaging
RESOURCE_GROUP_NAME ?= rg-$(SCENARIO)
LOCATION ?= japaneast
EVENT_GRID_NAMESPACE_NAME ?= eg-$(SCENARIO)
RESOURCE_ID ?= /subscriptions/$(SUBSCRIPTION_ID)/resourceGroups/$(RESOURCE_GROUP_NAME)/providers/Microsoft.EventGrid/namespaces/$(EVENT_GRID_NAMESPACE_NAME)
CLIENT_NAME ?= sample_client
TOPIC_SPACE_NAME ?= samples
EVENT_GRID_HOST_NAME ?= $(shell az resource show --ids $(RESOURCE_ID) --query "properties.topicSpacesConfiguration.hostname" -o tsv)

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
.DEFAULT_GOAL := help

.PHONY: info
info: ## show information
	@echo "SUBSCRIPTION_ID: $(SUBSCRIPTION_ID)"
	@echo "SUBSCRIPTION_NAME: $(SUBSCRIPTION_NAME)"
	@echo "TENANT_ID: $(TENANT_ID)"
	@echo "GIT_REVISION: $(GIT_REVISION)"
	@echo "GIT_TAG: $(GIT_TAG)"
	@echo "RESOURCE_ID: $(RESOURCE_ID)"
	@echo "MQTT_HOST_NAME: $(shell az resource show --ids $(RESOURCE_ID) --query "properties.topicSpacesConfiguration.hostname" -o tsv)"

.PHONY: install-deps-dev
install-deps-dev: ## install dependencies for development
	@which az || echo "Please install Azure CLI: https://github.com/Azure/azure-cli#installation"
	@which step || echo "Please install step: https://smallstep.com/docs/step-cli/installation/index.html"
	@which mosquitto || echo "Please install mosquitto: https://mosquitto.org/download/"

.PHONY: create-certificate
create-certificate: ## create CA
	step ca init \
		--deployment-type standalone \
		--name MqttAppSamplesCA \
		--dns localhost \
		--address 127.0.0.1:443 \
		--provisioner MqttAppSamplesCAProvisioner

.PHONY: create-client-certificate
create-client-certificate: ## create client certificate
	mkdir -p $(CLIENT_NAME)
	step certificate create sample_client $(CLIENT_NAME)/sample_client.pem $(CLIENT_NAME)/sample_client.key \
		--ca ~/.step/certs/intermediate_ca.crt \
		--ca-key ~/.step/secrets/intermediate_ca_key \
		--no-password --insecure \
		--not-after 2400h \
		&& cat ~/.step/certs/root_ca.crt ~/.step/certs/intermediate_ca.crt > $(CLIENT_NAME)/chain.pem \
		&& cp .env.sample $(CLIENT_NAME)/local.env \
		&& cp .env.eg.sample $(CLIENT_NAME)/event-grid.env

# ---
# MOSQUITTO
# ---

.PHONY: mosquitto
mosquitto: ## setup mosquitto
	cd _mosquitto \
		&& cat ~/.step/certs/root_ca.crt ~/.step/certs/intermediate_ca.crt > chain.pem \
		&& step certificate create localhost localhost.crt localhost.key \
			--ca ~/.step/certs/intermediate_ca.crt \
			--ca-key ~/.step/secrets/intermediate_ca_key \
			--no-password \
			--insecure \
			--not-after 2400h

.PHONY: mosquitto-start
mosquitto-start: ## start mosquitto
	cd _mosquitto \
		&& mosquitto -c tls.conf

# ---
# Go
# ---

.PHONY: build
build: ## build an app
	cd go && go build -o ./bin/egcli .
