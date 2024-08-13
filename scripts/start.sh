#

# if commune does not exist build it

# if docker is not running, start it

IMAGE_NAME=arena
IMAGE_PATH=./
CONTAINER_NAME=$IMAGE_NAME
SHM_SIZE=4g
NETWORK=host

# RESOLVE PORT RANGE
START_PORT=50050
END_PORT=50100
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
  -v $PWD:/app \
  --network $NETWORK \
  --restart unless-stopped \
  $CONTAINER_NAME"

eval $CMD_STR