#!/bin/bash

# Make Debian package for front
#
# IMPORTANT: run this with bash, or the virtualenv stuff will not work:
# $ bash make-debian-package.sh

time (

SRCDIR=$PWD
TODAY=`date +%Y%m%d`
PKGDIR="${SRCDIR}-${TODAY}"
PKG=`basename "$PKGDIR"`
TMPDIR="/home/gjost/tmp/${PKG}"

APP_NAME=front
VENV="${APP_NAME}env"

if [ -d "$TMPDIR" ]; then
  echo "Removing old tmp packages: ${TMPDIR}"
  rm -Rf $TMPDIR
fi

echo "Copying ${SRCDIR} to ${TMPDIR}"
cp -R $SRCDIR $TMPDIR

echo "Building virtualenv"
cd $TMPDIR
virtualenv --no-site-packages $TMPDIR/front/frontenv
source $TMPDIR/front/frontenv/bin/activate
pip install -r $TMPDIR/front/requirements.txt

echo "Fix shebang paths"
cd $TMPDIR
find front/frontenv/bin/ -type f | xargs -n1 -i sed -i 's/#!\/home\/gjost\/tmp\/front\-$TODAY\/front\/frontenv\/bin\/python/#!\/usr\/share\/front\/frontenv\/bin\/python/' {}

echo "Building package"
cd $TMPDIR
debuild -rfakeroot -us -uc 

cd $SRCDIR

) # time
exit;