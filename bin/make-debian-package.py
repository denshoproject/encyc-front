#!/usr/bin/python

from datetime import datetime, date
import os
import shutil

start = datetime.now()

src_dir = os.getcwd()
pkg = '%s_%s' % (os.path.basename(src_dir), date.today().strftime('%Y%m%d'))
tmp_pkg = '/home/gjost/tmp/%s' % pkg

print 'Packaging %s (started %s)' % (pkg, start)

if os.path.exists(tmp_pkg):
    rm = '%s*' % tmp_pkg
    print 'Removing old tmp packages: %s' % rm
    os.system('sudo rm -Rf %s' % rm)

print 'Copying %s to %s' % (src_dir, tmp_pkg)
shutil.copytree(src_dir, tmp_pkg)

print 'Building...'
os.chdir(tmp_pkg)
os.system('sudo debuild -us -uc')
#os.system('debuild -rfakeroot -us -uc')
#os.system('debuild -rfakeroot')

end = datetime.now()
elapsed = end - start
print 'DONE (elapsed: %s)' % elapsed
