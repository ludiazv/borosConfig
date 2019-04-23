#! /bin/bash
# Script for recreating the virtual enviroment. This is usefule use the in linux & macos
PY_VER="3.7.2"

os=$(uname)

echo "Installing python via pyenv..."
if [ "$os" = "Darwin" ] ; then
    ENVDIR=".macosenv"
    env PYTHON_CONFIGURE_OPTS="--enable-framework" pyenv install $PY_VER
else
    ENVDIR=".linuxenv"
    env PYTHON_CONFIGURE_OPTS="--enable-shared" pyenv install $PY_VER
fi

echo "Setup python env...."
echo "Os detected $os $ENVDIR"
echo "Checking pyenv......"
pyenv local
python --version
echo "CTRL-C to cancel any key to continue"
read -n 1
echo "Upgrade pip..."
pip install pip --upgrade
echo "cleaning..."
rm -rf $ENVDIR
rm -rf __pycache__
echo "recreating ...."
python -m venv $ENVDIR
source $ENVDIR/bin/activate
pip install -r requirements.txt


echo "Done!"