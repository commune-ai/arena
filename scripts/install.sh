ORG_NAME=commune-ai
REPO_NAME=commune
GIT_URL=https://github.com/$ORG_NAME/$REPO_NAME.git
REPO_PATH= $HOME/$REPO_NAME
# if the repo path does not exist, clone it
if [! -d $REPO_PATH ]; then
    echo "COULD NOT FIND COMMUNE in ${REPO_PATH}, CLONING REPO $REPO_NAME"
    git clone $GIT_URL $REPO_PATH
    pip install -r $REPO_PATH
fi
echo "COMMUNE IS INSTALLED"
# cd $REPO_PATH
# pip install -r requirements.txt
python3 -m pip install -e ./ --break-system-packages

# pip install -e ./
