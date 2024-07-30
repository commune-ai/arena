ORG_NAME=commune-ai
REPO_NAME=commune
REPO_PATH= $PWD/src/$REPO_NAME
# if the repo path does not exist, clone it
if [ ! -d "$REPO_PATH" ]; then
    echo "CLONING REPO $REPO_NAME"
    git clone https://github.com/$ORG_NAME/$REPO_NAME.git $REPO_PATH
    SRC_PATH=$REPO_PATH/requirements.txt
    pip install -r ${SRC_PATH}
fi
