#!/bin/bash
VERSION="1"

DST="./dist"
echo "Build boros config binary...."

mkdir -p $DST/macos
mkdir -p $DST/linux64

rm -Rf build
os=$(uname)
echo "OS detected >$os<"

OUT_NAME="borosconfigV${VERSION}"
PYINST_OPT="--onefile --clean -y -n ${OUT_NAME}"

if [ "$os" = "Darwin" ] ; then
    python --version
    pyinstaller $PYINST_OPT -w --noconsole --distpath $DST/macos -i logo.icns main.py
    if [ $? -eq 0 ] ; then
        rm $DST/macos/$OUT_NAME
        hdiutil create -volname "$OUT_NAME" -srcfolder $DST/macos -ov -format UDZO $DST/tmp.dmg
        mv $DST/tmp.dmg $DST/macos/$OUT_NAME.dmg
        rm -Rf $DST/macos/${OUT_NAME}.app
    fi
    rm -Rf build

else 
    # linux 64
    python --version
    pyinstaller $PYINST_OPT --distpath $DST/linux64 main.py
    if [ $? -eq 0 ] ; then
        gzip -9 $DST/linux64/$OUT_NAME
    fi
    rm -Rf build
fi




