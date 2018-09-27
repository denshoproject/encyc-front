PROJECT=encyc
APP=encycfront
USER=encyc
SHELL = /bin/bash

APP_VERSION := $(shell cat VERSION)
GIT_SOURCE_URL=https://github.com/densho/encyc-front

# Release name e.g. jessie
DEBIAN_CODENAME := $(shell lsb_release -sc)
# Release numbers e.g. 8.10
DEBIAN_RELEASE := $(shell lsb_release -sr)
# Sortable major version tag e.g. deb8
DEBIAN_RELEASE_TAG = deb$(shell lsb_release -sr | cut -c1)

PACKAGE_SERVER=ddr.densho.org/static/encycfront

INSTALL_BASE=/opt
INSTALLDIR=$(INSTALL_BASE)/encyc-front
DOWNLOADS_DIR=/tmp/$(APP)-install
REQUIREMENTS=$(INSTALLDIR)/requirements.txt
PIP_CACHE_DIR=$(INSTALL_BASE)/pip-cache

VIRTUALENV=$(INSTALLDIR)/venv/front
SETTINGS=$(INSTALLDIR)/front/front/settings.py

CONF_BASE=/etc/encyc
CONF_PRODUCTION=$(CONF_BASE)/front.cfg
CONF_LOCAL=$(CONF_BASE)/front-local.cfg
CONF_DJANGO=$(INSTALLDIR)/front/front/settings.py

MEDIA_BASE=/var/www/html/front
MEDIA_ROOT=$(MEDIA_BASE)/media
STATIC_ROOT=$(MEDIA_BASE)/static

OPENJDK_PKG=
ifeq ($(DEBIAN_RELEASE), jessie)
	OPENJDK_PKG=openjdk-7-jre
endif
ifeq ($(DEBIAN_CODENAME), stretch)
	OPENJDK_PKG=openjdk-8-jre
endif

ELASTICSEARCH=elasticsearch-2.4.4.deb
# wget https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-1.0.1.deb

SUPERVISOR_GUNICORN_CONF=/etc/supervisor/conf.d/$(APP).conf
SUPERVISOR_CONF=/etc/supervisor/supervisord.conf
NGINX_CONF=/etc/nginx/sites-available/$(APP).conf
NGINX_CONF_LINK=/etc/nginx/sites-enabled/$(APP).conf

MODERNIZR=modernizr-2.5.3
BOOTSTRAP=bootstrap-2.3.1
JQUERY=jquery-1.7.2.min.js
JWPLAYER=jwplayer-5.9
LIGHTVIEW=lightview-3.2.2
SWFOBJECT=swfobject-2.2
OPENLAYERS=OpenLayers-2.12
# wget https://github.com/twbs/bootstrap/archive/v2.0.4.zip
# wget http://code.jquery.com/jquery-1.7.2.min.js
# wget http://modernizr.com/downloads/modernizr-2.5.3.js
# jwplayer-5.9
# lightview-3.2.2
# wget https://swfobject.googlecode.com/files/swfobject_2_2.zip
ASSETS=encyc-front-assets.tgz

DEB_BRANCH := $(shell git rev-parse --abbrev-ref HEAD | tr -d _ | tr -d -)
DEB_ARCH=amd64
DEB_NAME_JESSIE=$(APP)-$(DEB_BRANCH)
DEB_NAME_STRETCH=$(APP)-$(DEB_BRANCH)
# Application version, separator (~), Debian release tag e.g. deb8
# Release tag used because sortable and follows Debian project usage.
DEB_VERSION_JESSIE=$(APP_VERSION)~deb8
DEB_VERSION_STRETCH=$(APP_VERSION)~deb9
DEB_FILE_JESSIE=$(DEB_NAME_JESSIE)_$(DEB_VERSION_JESSIE)_$(DEB_ARCH).deb
DEB_FILE_STRETCH=$(DEB_NAME_STRETCH)_$(DEB_VERSION_STRETCH)_$(DEB_ARCH).deb
DEB_VENDOR=Densho.org
DEB_MAINTAINER=<geoffrey.jost@densho.org>
DEB_DESCRIPTION=Densho Encyclopedia site
DEB_BASE=opt/encyc-front


.PHONY: help


help:
	@echo "encyc-front Install Helper"
	@echo "See: make howto-install"

help-all:
	@echo "install - Do a fresh install"

howto-install:
	@echo "Installation"
	@echo "============"
	@echo ""
	@echo "Basic Debian server netinstall; see ddr-manual."
	@echo "Install SSH keys for root."
	@echo "(see https://help.github.com/articles/generating-ssh-keys/)::"
	@echo ""
	@echo "    # ssh-keygen -t rsa -b 4096 -C \"your_email@example.com\""
	@echo "    # cat ~/.ssh/id_rsa.pub"
	@echo "    Cut and paste public key into GitHub."
	@echo "    # ssh -T git@github.com"
	@echo ""
	@echo "Prepare for install::"
	@echo ""
	@echo "    # apt-get install make"
	@echo "    # adduser encyc"
	@echo "    # git clone git@github.com:densho/encyc-front.git $(INSTALLDIR)"
	@echo "    # cd $(INSTALLDIR)/front"
	@echo ""
	@echo "If not running the master branch, switch to it now::"
	@echo ""
	@echo "    # git checkout -b develop origin/develop"
	@echo ""
	@echo "Install encyc-front software, dependencies, and configs::"
	@echo ""
	@echo "    # make install"
	@echo ""
	@echo "Run Django shell once to initialize environment variables."
	@echo ""
	@echo "    # source $(VIRTUALENV)/bin/activate"
	@echo "    # cd $(INSTALLDIR)/front && python manage.py shell"
	@echo ""
	@echo "Initial database setup."
	@echo ""
	@echo "    # make syncdb"
	@echo "    # su encyc"
	@echo "    $ python manage.py dbshell"
	@echo "    sqlite> update django_site set domain='encyclopedia.densho.org', name='encyclopedia.densho.org' where id=1;"
	@echo "    sqlite> .quit"
	@echo ""
	@echo "Adjust configs to fit the local environment. Values in /etc/encyc/front-local.cfg"
	@echo "override those in front.cfg::"
	@echo ""
	@echo "    # vi /etc/encyc/front-local.cfg"
	@echo ""
	@echo "Restart::"
	@echo ""
	@echo "    # make restart"
	@echo "    # make status"
	@echo ""
	@echo "If you need automatic updates, add the following to /etc/crontab.::"
	@echo ""
	@echo "    # encyc-front: get topics,authors,articles updates from dango"
	@echo "    SHELL=/bin/bash"
	@echo "    */30 *  * * *   encyc   $(VIRTUALENV)/bin/python $(INSTALLDIR)/front/manage.py encyc --topics --authors --articles"
	@echo ""
	@echo "    # encyc-front: get primary-source images from dango"
	@echo "    SHELL=/bin/bash"
	@echo "    */60 *  * * *   encyc   $(VIRTUALENV)/bin/python $(INSTALLDIR)/front/bin/sync-psms.py"
	@echo ""



install: install-prep install-app install-static install-configs

update: update-front

uninstall: uninstall-front

clean: clean-front


install-prep: apt-update install-core git-config install-misc-tools


apt-update:
	@echo ""
	@echo "Package update ---------------------------------------------------------"
	apt-get --assume-yes update

apt-upgrade:
	@echo ""
	@echo "Package upgrade --------------------------------------------------------"
	apt-get --assume-yes upgrade

install-core:
	apt-get --assume-yes install bzip2 curl gdebi-core git-core logrotate ntp p7zip-full wget

git-config:
	git config --global alias.st status
	git config --global alias.co checkout
	git config --global alias.br branch
	git config --global alias.ci commit

install-misc-tools:
	@echo ""
	@echo "Installing miscellaneous tools -----------------------------------------"
	apt-get --assume-yes install ack-grep byobu elinks htop httpie iftop iotop mg multitail sshuttle


install-daemons: install-nginx install-redis install-elasticsearch

install-nginx:
	@echo ""
	@echo "Nginx ------------------------------------------------------------------"
	apt-get --assume-yes install nginx

install-redis:
	@echo ""
	@echo "Redis ------------------------------------------------------------------"
	apt-get --assume-yes install redis-server

get-elasticsearch:
	-wget -nc -P $(DOWNLOADS_DIR) http://$(PACKAGE_SERVER)/$(ELASTICSEARCH)

install-elasticsearch: install-core
	@echo ""
	@echo "Elasticsearch ----------------------------------------------------------"
# Elasticsearch is configured/restarted here so it's online by the time script is done.
	apt-get --assume-yes install $(OPENJDK_PKG)
	-gdebi --non-interactive /tmp/downloads/$(ELASTICSEARCH)
#cp $(INSTALL_BASE)/ddr-public/conf/elasticsearch.yml /etc/elasticsearch/
#chown root.root /etc/elasticsearch/elasticsearch.yml
#chmod 644 /etc/elasticsearch/elasticsearch.yml
# 	@echo "${bldgrn}search engine (re)start${txtrst}"
	-service elasticsearch stop
	-systemctl disable elasticsearch.service

enable-elasticsearch:
	systemctl enable elasticsearch.service

disable-elasticsearch:
	systemctl disable elasticsearch.service

remove-elasticsearch:
	apt-get --assume-yes remove $(OPENJDK_PKG) elasticsearch


install-virtualenv:
	@echo ""
	@echo "install-virtualenv -----------------------------------------------------"
	apt-get --assume-yes install python-pip python-virtualenv
	test -d $(VIRTUALENV) || virtualenv --distribute --setuptools $(VIRTUALENV)

install-setuptools: install-virtualenv
	@echo ""
	@echo "install-setuptools -----------------------------------------------------"
	apt-get --assume-yes install python-dev
	source $(VIRTUALENV)/bin/activate; \
	pip install -U setuptools


install-app: install-virtualenv install-setuptools install-encyc-front

update-app: update-encyc-front install-configs

uninstall-app: uninstall-encyc-front

clean-app: clean-encyc-front


install-encyc-front:
	@echo ""
	@echo "encyc-front --------------------------------------------------------------"
	apt-get --assume-yes install imagemagick libxml2 libxslt1.1 libxslt1-dev python-dev sqlite3 supervisor zlib1g-dev

ifeq ($(DEBIAN_CODENAME), wheezy)
	apt-get --assume-yes install libjpeg8-dev
endif
ifeq ($(DEBIAN_CODENAME), jessie)
	apt-get --assume-yes install libjpeg62-turbo-dev
endif

# virtualenv
	source $(VIRTUALENV)/bin/activate; \
	pip install -U -r $(INSTALLDIR)/requirements.txt
# log dir
	-mkdir /var/log/encyc
	chown -R encyc.root /var/log/encyc
	chmod -R 755 /var/log/encyc
# sqlite db dir
	-mkdir /var/lib/encyc
	chown -R encyc.root /var/lib/encyc
	chmod -R 755 /var/lib/encyc
# media dirs
	-mkdir -p $(MEDIA_ROOT)
	-mkdir -p $(STATIC_ROOT)
	chown -R encyc.root $(STATIC_ROOT)
	chmod -R 755 $(STATIC_ROOT)
	cp -R $(INSTALLDIR)/front/static/* $(STATIC_ROOT)/
	cp -R $(INSTALLDIR)/front/wikiprox/static/* $(STATIC_ROOT)/
	chown -R encyc.root $(MEDIA_BASE)
	chmod -R 755 $(MEDIA_BASE)

syncdb:
	source $(VIRTUALENV)/bin/activate
	cd $(INSTALLDIR)/front && python manage.py syncdb --noinput
	chown -R encyc.root /var/lib/encyc
	chmod -R 750 /var/lib/encyc
	chown -R encyc.root /var/log/encyc
	chmod -R 755 /var/log/encyc

update-encyc-front:
	@echo ""
	@echo "encyc-front --------------------------------------------------------------"
	git fetch && git pull
	source $(VIRTUALENV)/bin/activate; \
	pip install -U -r $(INSTALLDIR)/requirements.txt

uninstall-encyc-front:
	cd $(INSTALLDIR)/front
	source $(VIRTUALENV)/bin/activate; \
	-pip uninstall -r $(INSTALLDIR)/requirements.txt
	-rm /usr/local/lib/python2.7/dist-packages/front-*
	-rm -Rf /usr/local/lib/python2.7/dist-packages/front

restart-front:
	/etc/init.d/supervisor restart front

clean-encyc-front:
	-rm -Rf $(VIRTUALENV)
	-rm -Rf $(INSTALLDIR)/front/src

clean-pip:
	-rm -Rf $(PIP_CACHE_DIR)/*



install-static: get-assets install-bootstrap install-jquery install-jwplayer install-lightview install-modernizr install-swfobject install-openlayers

get-assets:
	@echo ""
	@echo "get assets --------------------------------------------------------------"
	-mkdir -p $(MEDIA_BASE)
	chown -R root.root $(MEDIA_BASE)
	chmod -R 755 $(MEDIA_BASE)
	wget -nc -P /tmp http://$(PACKAGE_SERVER)/$(ASSETS)
	tar xzvf /tmp/$(ASSETS) -C /tmp/
	cp -R /tmp/encyc-front-assets/* $(MEDIA_ROOT)

install-bootstrap:
	@echo ""
	@echo "Bootstrap --------------------------------------------------------------"
	wget -nc -P /tmp/ http://$(PACKAGE_SERVER)/$(BOOTSTRAP).zip
	7z x -y -o$(STATIC_ROOT)/ /tmp/$(BOOTSTRAP).zip

install-jquery:
	@echo ""
	@echo "jQuery -----------------------------------------------------------------"
	wget -nc -P $(STATIC_ROOT)/ http://$(PACKAGE_SERVER)/$(JQUERY)

install-jwplayer:
	@echo ""
	@echo "jwplayer ---------------------------------------------------------------"
	-wget -nc -P /tmp/ http://$(PACKAGE_SERVER)/$(JWPLAYER).tgz
	-tar xzf /tmp/$(JWPLAYER).tgz -C /tmp/
	-mv /tmp/$(JWPLAYER) $(STATIC_ROOT)/

install-lightview:
	@echo ""
	@echo "lightview --------------------------------------------------------------"
	-wget -nc -P /tmp/ http://$(PACKAGE_SERVER)/$(LIGHTVIEW).tgz
	-tar xzf /tmp/$(LIGHTVIEW).tgz -C /tmp/
	-mv /tmp/$(LIGHTVIEW) $(STATIC_ROOT)/

install-modernizr:
	@echo ""
	@echo "Modernizr --------------------------------------------------------------"
	-rm $(STATIC_ROOT)/js/$(MODERNIZR)*
	-wget -nc -P $(STATIC_ROOT)/ http://$(PACKAGE_SERVER)/$(MODERNIZR).js

install-swfobject:
	@echo ""
	@echo "swfobject --------------------------------------------------------------"
	-wget -nc -P /tmp/ http://$(PACKAGE_SERVER)/$(SWFOBJECT).zip
	-7z x -y -o/tmp/ /tmp/$(SWFOBJECT).zip
	-mv /tmp/swfobject/ $(STATIC_ROOT)/$(SWFOBJECT)

install-openlayers:
	@echo ""
	@echo "OpenLayers -------------------------------------------------------------"
	-wget -nc -P /tmp/ http://$(PACKAGE_SERVER)/$(OPENLAYERS).tar.gz
	-tar xzf /tmp/$(OPENLAYERS).tar.gz -C /tmp/
	-mv /tmp/$(OPENLAYERS) $(STATIC_ROOT)/

set-perms:
#	recursively chmod directories 755, files 644
#	from CWD
	chown -R encyc.root $(MEDIA_BASE)
	cd $(MEDIA_BASE)
	for i in `find . -type d`; do chmod 755 $i; done
	for i in `find . -type f`; do chmod 644 $i; done


clean-static: clean-bootstrap clean-jquery clean-jwplayer clean-lightview clean-modernizr clean-swfobject clean-openlayers

clean-bootstrap:
	-rm -Rf $(STATIC_ROOT)/$(BOOTSTRAP)

clean-jquery:
	-rm -Rf $(STATIC_ROOT)/$(JQUERY)

clean-jwplayer:
	-rm -Rf $(STATIC_ROOT)/$(JWPLAYER)

clean-lightview:
	-rm -Rf $(STATIC_ROOT)/$(LIGHTVIEW)

clean-modernizr:
	-rm $(STATIC_ROOT)/$(MODERNIZR).js

clean-swfobject:
	-rm -Rf $(STATIC_ROOT)/$(SWFOBJECT)

clean-openlayers:
	-rm -Rf $(STATIC_ROOT)/$(OPENLAYERS)


install-configs:
	@echo ""
	@echo "installing configs ----------------------------------------------------"
# web app settings
	cp $(INSTALLDIR)/conf/settings.py $(INSTALLDIR)/front/front/
	chown root.root $(INSTALLDIR)/front/front/settings.py
	chmod 644 $(INSTALLDIR)/front/front/settings.py
	-mkdir /etc/encyc
	cp $(INSTALLDIR)/conf/front.cfg /etc/encyc/
	chown root.encyc /etc/encyc/front.cfg
	chmod 640 /etc/encyc/front.cfg
	touch /etc/encyc/front-local.cfg
	chown root.encyc /etc/encyc/front-local.cfg
	chmod 640 /etc/encyc/front-local.cfg

uninstall-configs:
	-rm $(INSTALLDIR)/front/settings.py

install-daemon-configs:
	@echo ""
	@echo "installing daemon configs ---------------------------------------------"
# nginx settings
	cp $(INSTALLDIR)/conf/nginx.conf /etc/nginx/sites-available/front.conf
	chown root.root /etc/nginx/sites-available/front.conf
	chmod 644 /etc/nginx/sites-available/front.conf
	-ln -s /etc/nginx/sites-available/front.conf /etc/nginx/sites-enabled/front.conf
	-rm /etc/nginx/sites-enabled/default
# supervisord
	cp $(INSTALLDIR)/conf/supervisor.conf /etc/supervisor/conf.d/front.conf
	chown root.root /etc/supervisor/conf.d/front.conf
	chmod 644 /etc/supervisor/conf.d/front.conf

uninstall-daemon-configs:
	-rm /etc/nginx/sites-available/front.conf
	-rm /etc/nginx/sites-enabled/front.conf
	-rm /etc/supervisor/conf.d/gunicorn_front.conf


reload: reload-nginx reload-supervisor

reload-nginx:
	/etc/init.d/nginx reload

reload-supervisor:
	supervisorctl reload


restart: restart-elasticsearch restart-redis restart-nginx restart-supervisor

restart-elasticsearch:
	/etc/init.d/elasticsearch restart

restart-redis:
	/etc/init.d/redis-server restart

restart-nginx:
	/etc/init.d/nginx restart

restart-supervisor:
	/etc/init.d/supervisor restart


status:
	@echo [`systemctl is-active nginx`] nginx
	@echo [`systemctl is-active redis-server`] redis
	@echo [`systemctl is-active elasticsearch`] elasticsearch
	@echo [`systemctl is-active supervisor`] supervisor
	@supervisorctl status

git-status:
	@echo "------------------------------------------------------------------------"
	cd $(INSTALLDIR) && git status


# http://fpm.readthedocs.io/en/latest/
# https://stackoverflow.com/questions/32094205/set-a-custom-install-directory-when-making-a-deb-package-with-fpm
# https://brejoc.com/tag/fpm/
deb: deb-stretch

# deb-jessie and deb-stretch are identical EXCEPT:
# jessie: --depends openjdk-7-jre
# stretch: --depends openjdk-8-jre
deb-stretch:
	@echo ""
	@echo "DEB packaging (stretch) ------------------------------------------------"
	-rm -Rf $(DEB_FILE_STRETCH)
	virtualenv --relocatable $(VIRTUALENV)  # Make venv relocatable
	fpm   \
	--verbose   \
	--input-type dir   \
	--output-type deb   \
	--name $(DEB_NAME_STRETCH)   \
	--version $(DEB_VERSION_STRETCH)   \
	--package $(DEB_FILE_STRETCH)   \
	--url "$(GIT_SOURCE_URL)"   \
	--vendor "$(DEB_VENDOR)"   \
	--maintainer "$(DEB_MAINTAINER)"   \
	--description "$(DEB_DESCRIPTION)"   \
	--depends "imagemagick"   \
	--depends "libxml2"   \
	--depends "libxslt1.1"   \
	--depends "libxslt1-dev"   \
	--depends "python-dev"   \
	--depends "python-pip"   \
	--depends "python-virtualenv"   \
	--depends "sqlite3"   \
	--depends "zlib1g-dev"   \
	--depends "libjpeg62-turbo-dev"   \
	--depends "nginx"   \
	--depends "redis-server"   \
	--depends "supervisor"   \
	--chdir $(INSTALLDIR)   \
	conf/front.cfg=etc/encyc/front.cfg   \
	conf=$(DEB_BASE)   \
	COPYRIGHT=$(DEB_BASE)   \
	front=$(DEB_BASE)   \
	.git=$(DEB_BASE)   \
	.gitignore=$(DEB_BASE)   \
	INSTALL=$(DEB_BASE)   \
	LICENSE=$(DEB_BASE)   \
	Makefile=$(DEB_BASE)   \
	README.rst=$(DEB_BASE)   \
	venv=$(DEB_BASE)   \
	venv/front/lib/python2.7/site-packages/rest_framework/static/rest_framework=$(STATIC_ROOT)  \
	VERSION=$(DEB_BASE)
