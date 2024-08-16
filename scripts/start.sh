# START THE CONTAINER
IMAGE_NAME=arena
IMAGE_PATH=./
CONTAINER_NAME=$IMAGE_NAME
SHM_SIZE=4g
NETWORK=host
START_PORT=50050
END_PORT=50100
DOCKER_SOCKET_PATH=/var/run/docker.sock

DOES_IMAGE_EXIST=$(docker images -q $IMAGE_NAME)
if [ ! $DOES_IMAGE_EXIST ]; then
  echo "BUILDING IMAGE $IMAGE_NAME"
  docker build -t $IMAGE_NAME $IMAGE_PATH
fi

CONTAINER_EXISTS=$(docker ps -q -f name=$CONTAINER_NAME)  
if [ $CONTAINER_EXISTS ]; then
  echo "STOPPING CONTAINER $CONTAINER_NAME"
  docker stop $CONTAINER_NAME
fi

CONTAINER_ID=$(docker ps -aqf "name=$CONTAINER_NAME")
if [ $CONTAINER_ID ]; then
  echo "REMOVING CONTIANER NAME=$CONTAINER_NAME ID=$CONTAINER_ID"
  docker rm $CONTAINER_ID
fi

CMD_STR="docker run -d \
  --name $CONTAINER_NAME \
  --shm-size $SHM_SIZE \
  -v ~/.commune:/root/.commune \
  -v ~/commune:/root/commune \
  -v $PWD:/app \
  --network $NETWORK \
  $IMAGE_NAME"
echo $CMD_STR
  # voume of docker socket
docker exec -it $CONTAINER_NAME c ls
eval $CMD_STR


# RESOLVE PORT RANGE
