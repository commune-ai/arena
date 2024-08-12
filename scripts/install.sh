ORG_NAME=commune-ai
REPO_NAME=commune
GIT_URL=https://github.com/$ORG_NAME/$REPO_NAME.git
REPO_PATH="/root/$REPO_NAME"
REPO_EXIST=$(ls -l $REPO_PATH/.git | wc -l)

# if the repo path does not exist, clone it
if [ $REPO_EXIST -eq 0 ]; then
    echo "COULD NOT FIND COMMUNE in ${REPO_PATH}, CLONING REPO $REPO_NAME"
    # only clone the main branch and avoid the entire history
    git clone $GIT_URL $REPO_PATH --depth 1
    python3 -m pip install -e $REPO_PATH --break-system-packages
fi
# does REPO EXIST
echo "COMMUNE IS $REPO_PATH $REPO_EXIST"
# # cd $REPO_PATH
python3 -m pip install -e ./ --break-system-packages

