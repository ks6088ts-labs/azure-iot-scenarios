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

.PHONY: resource-group
resource-group: ## create Resource Group
	az group create --name $(RESOURCE_GROUP_NAME) --location $(LOCATION)

.PHONY: event-grid
event-grid: ## create Event Grid
		az account set -s $(SUBSCRIPTION_ID)
		az resource create --id $(RESOURCE_ID) --is-full-object --properties "{\
			\"properties\": {\
				\"isZoneRedundant\": true,\
				\"topicsConfiguration\": {\
					\"inputSchema\": \"CloudEventSchemaV1_0\"\
				},\
				\"topicSpacesConfiguration\": {\
					\"state\": \"Enabled\"\
				}\
			},\
			\"location\": \"$(LOCATION)\"\
		}"

.PHONY: create-certificate
create-certificate: ## create CA
	step ca init \
		--deployment-type standalone \
		--name MqttAppSamplesCA \
		--dns localhost \
		--address 127.0.0.1:443 \
		--provisioner MqttAppSamplesCAProvisioner

.PHONY: create-event-grid-certificate
create-event-grid-certificate: ## create certificate for Event Grid
	$(eval capem := $(shell cat ~/.step/certs/intermediate_ca.crt | tr -d "\n"))
	az resource create \
		--id "$(RESOURCE_ID)/caCertificates/Intermediate01" \
		--properties "{\"encodedCertificate\" : \"$(capem)\"}"

.PHONY: delete-event-grid-certificate
delete-event-grid-certificate: ## create certificate for Event Grid
	az resource delete \
		--id "$(RESOURCE_ID)/caCertificates/Intermediate01"

.PHONY: create-client-certificate
create-client-certificate: ## create client certificate
	rm -rf $(CLIENT_NAME)
	mkdir -p $(CLIENT_NAME)
	cd $(CLIENT_NAME) \
		&& step certificate create sample_client sample_client.pem sample_client.key \
			--ca ~/.step/certs/intermediate_ca.crt \
			--ca-key ~/.step/secrets/intermediate_ca_key \
			--no-password --insecure \
			--not-after 2400h \
		&& cat ~/.step/certs/root_ca.crt ~/.step/certs/intermediate_ca.crt > chain.pem \
		&& cp ../.env.sample .env

.PHONY: create-event-grid-client
create-event-grid-client: ## create client for Event Grid
	az resource create --id "$(RESOURCE_ID)/clients/$(CLIENT_NAME)" --properties "{\
		\"authenticationName\": \"$(CLIENT_NAME)\",\
		\"state\": \"Enabled\",\
		\"clientCertificateAuthentication\": {\
			\"validationScheme\": \"SubjectMatchesAuthenticationName\"\
		},\
		\"attributes\": {\
			\"type\": \"$(CLIENT_NAME)\"\
		},\
		\"description\": \"This is a test publisher client\"\
	}"

.PHONY: create-event-grid-topic-space
create-event-grid-topic-space: ## create topic space for Event Grid
	az resource create --id "$(RESOURCE_ID)/topicSpaces/$(TOPIC_SPACE_NAME)" --properties "{\
		\"topicTemplates\": [\"sample/#\"]\
	}"

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
