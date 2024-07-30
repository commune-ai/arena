



CONTAINER=arena
SCRIPTS_PATH=./scripts
COMMUNE_REPO=https://github.com/commune-ai/commune.git
git clone ${COMMUNE_REPO} ./src/commune
# include the arguments following this
build:
	${SCRIPTS_PATH}/build.sh 
start:
	${SCRIPTS_PATH}/start.sh 
up: 
	make start
	
restart: 
	docker restart ${CONTAINER}
down:
	docker kill ${CONTAINER} ; docker rm ${CONTAINER}
kill:
	docker kill ${CONTAINER} ; docker rm ${CONTAINER}
enter:
	docker exec -it ${CONTAINER} bash
tests: 
	docker exec ${CONTAINER} bash -c "pytest commune/tests"
chmod_scripts:
	chmod +x ${SCRIPTS_PATH}/*.sh

install:
	./scripts/install.sh
	