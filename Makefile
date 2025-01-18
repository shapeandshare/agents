## Management #################################################################
setup:
	resources/setup.sh

prepare:
	resources/prepare.sh

clean:
	rm -rf ./build ./dist ./src/shapeandshare.agents.egg-info docs/build *.tgz

nuke:
	make nuke-dev
	make clean
	rm -rf ./venv

# In CI:
#	TWINE_USERNAME=joshburt
#	TWINE_PASSWORD=token
#	TWINE_NON_INTERACTIVE
# locally: ~/.pypirc

publish-package:
	resources/publish-package.sh

lint:
	resources/lint.sh

lint-fix:
	resources/lint-fix.sh

## Dev Setup ##################################################################

install-k3d:
	curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash

setup-dev:
	k3d registry create dev-registry --port 5001
	k3d cluster create dev-cluster --registry-use k3d-dev-registry:5001 --port "8080:8080@loadbalancer" --port "8081:8081@loadbalancer" --port "8000:8000@loadbalancer" --port "27017:27017@loadbalancer" --port "5672:5672@loadbalancer" --port "15672:15672@loadbalancer"
	kubectl create namespace agents

nuke-dev:
	k3d cluster delete dev-cluster
	k3d registry delete dev-registry

## Build ######################################################################

build-package:
	resources/build-package.sh

build-image:
	resources/build-image.sh

build-git-agent-installer:
	helm package src/shapeandshare/agents/git/charts/git-agent

build-chromadb-installer:
	helm package src/shapeandshare/agents/core/charts/chromadb

build-mongodb-installer:
	helm package src/shapeandshare/agents/core/charts/mongodb

build-rabbitmq-installer:
	helm package src/shapeandshare/agents/core/charts/rabbitmq

build-chathistory-service-installer:
	helm package src/shapeandshare/agents/core/services/chathistory/charts/chathistory-service

build:
	make build-package
	make build-image
	make build-git-agent-installer
	make build-chromadb-installer
	make build-mongodb-installer
	make build-rabbitmq-installer
	make build-chathistory-service-installer


## Install Local Dev ################################################################

push-image-dev:
	docker push k3d-dev-registry:5001/shapeandshare.agents:latest

mongodb-install-dev:
	helm install mongodb ./mongodb-0.1.0.tgz --namespace agents

chromadb-install-dev:
	helm install chromadb ./chromadb-0.1.0.tgz --namespace agents

git-agent-install-dev:
	helm install git-agent ./git-agent-0.1.0.tgz --namespace agents

rabbitmq-install-dev:
	helm install rabbitmq ./rabbitmq-0.1.0.tgz --namespace agents

chathistory-service-install-dev:
	helm install chathistory-service ./chathistory-service-0.1.0.tgz --namespace agents

install:
	make mongodb-install-dev
	make chromadb-install-dev
	make rabbitmq-install-dev

install-apps:
	make push-image-dev
	make chathistory-service-install-dev
	make git-agent-install-dev


## Uninstall Local Dev ################################################################

mongodb-uninstall-dev:
	helm uninstall mongodb --namespace agents

chromadb-uninstall-dev:
	helm uninstall chromadb --namespace agents

git-agent-uninstall-dev:
	helm uninstall git-agent --namespace agents

rabbitmq-uninstall-dev:
	helm uninstall rabbitmq --namespace agents

chathistory-service-uninstall-dev:
	helm uninstall chathistory-service  --namespace agents

uninstall:
	make chromadb-uninstall-dev
	make mongodb-uninstall-dev
	make rabbitmq-uninstall-dev

uninstall-apps:
	make chathistory-service-uninstall-dev
	make git-agent-uninstall-dev

## Documentation ##############################################################

docs-quickstart:
	sphinx-quickstart docs --sep --project agents

docs-api:
	sphinx-apidoc -f -o docs/source/api src/shapeandshare/agents

docs-build:
	rm -rf docs/build && cd docs && make clean && make html

## Demo #######################################################################

demo:
	make setup
	make prepare
	make setup-dev
	make build
	make install
	make install-apps

