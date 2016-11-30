include .env
VERSION ?= latest

REPO = mattberther/s3-backup
NAME = s3-backup
INSTANCE = default

.PHONY: build push shell run start stop rm release

build:
	docker build -t $(REPO):$(VERSION) .

push: build
	docker push $(REPO):$(VERSION)

shell:
	docker run --rm --name $(NAME)-$(INSTANCE) -i -t $(PORTS) $(VOLUMES) $(ENV) $(EXTRA_OPTS) $(REPO):$(VERSION) /bin/sh

run:
	docker run --rm --name $(NAME)-$(INSTANCE) $(PORTS) $(VOLUMES) $(ENV) $(EXTRA_OPTS) $(REPO):$(VERSION)

rm:
	docker rm $(NAME)-$(INSTANCE)

release: build
	make push -e VERSION=$(VERSION)

default: build
