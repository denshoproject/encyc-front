PROJECT=encyc
APP=encycfront
USER=encyc
SHELL = /bin/bash

APP_VERSION := $(shell cat VERSION)
GIT_SOURCE_URL=https://github.com/densho/encyc-front

PACKAGE_SERVER=ddr.densho.org/static/encycfront

SRC_REPO_ASSETS=https://github.com/denshoproject/encyc-front-assets.git

INSTALL_BASE=/opt
INSTALLDIR=$(INSTALL_BASE)/encyc-front
DOWNLOADS_DIR=/tmp/$(APP)-install
INSTALL_FRONT=/opt/encyc-front
INSTALL_ASSETS=/opt/encyc-front-assets
REQUIREMENTS=$(INSTALLDIR)/requirements.txt
PIP_CACHE_DIR=$(INSTALL_BASE)/pip-cache

VIRTUALENV=$(INSTALLDIR)/venv/front
SETTINGS=$(INSTALLDIR)/front/front/settings.py

CONF_BASE=/etc/encyc
CONF_PRODUCTION=$(CONF_BASE)/front.cfg
CONF_LOCAL=$(CONF_BASE)/front-local.cfg
CONF_DJANGO=$(INSTALLDIR)/front/front/settings.py

SQLITE_BASE=/var/lib/encyc
LOG_BASE=/var/log/encyc

MEDIA_BASE=/var/www/encycfront
MEDIA_ROOT=$(MEDIA_BASE)/media
STATIC_ROOT=$(MEDIA_BASE)/static

# Release name e.g. jessie
DEBIAN_CODENAME := $(shell lsb_release -sc)
# Release numbers e.g. 8.10
DEBIAN_RELEASE := $(shell lsb_release -sr)
# Sortable major version tag e.g. deb8
DEBIAN_RELEASE_TAG = deb$(shell lsb_release -sr | cut -c1)

OPENJDK_PKG=
ifeq ($(DEBIAN_CODENAME), bullseye)
	OPENJDK_PKG=openjdk-17-jre-headless
endif
ifeq ($(DEBIAN_CODENAME), bookworm)
	OPENJDK_PKG=openjdk-17-jre-headless
endif
ifeq ($(DEBIAN_CODENAME), trixie)
	OPENJDK_PKG=openjdk-17-jre-headless
endif

ELASTICSEARCH=elasticsearch-2.4.6.deb

SUPERVISOR_GUNICORN_CONF=/etc/supervisor/conf.d/$(APP).conf
SUPERVISOR_CONF=/etc/supervisor/supervisord.conf
NGINX_CONF=/etc/nginx/sites-available/$(APP).conf
NGINX_CONF_LINK=/etc/nginx/sites-enabled/$(APP).conf

TGZ_BRANCH := $(shell git rev-parse --abbrev-ref HEAD | tr -d _ | tr -d -)
TGZ_FILE=$(APP)_$(APP_VERSION)
TGZ_DIR=$(INSTALL_FRONT)/$(TGZ_FILE)
TGZ_FRONT=$(TGZ_DIR)/encyc-front
TGZ_ASSETS=$(TGZ_DIR)/encyc-front/encyc-front-assets

DEB_BRANCH := $(shell git rev-parse --abbrev-ref HEAD | tr -d _ | tr -d -)
DEB_ARCH=amd64
DEB_NAME_BULLSEYE=$(APP)-$(DEB_BRANCH)
DEB_NAME_BOOKWORM=$(APP)-$(DEB_BRANCH)
DEB_NAME_TRIXIE=$(APP)-$(DEB_BRANCH)
# Application version, separator (~), Debian release tag e.g. deb8
# Release tag used because sortable and follows Debian project usage.
DEB_VERSION_BULLSEYE=$(APP_VERSION)~deb11
DEB_VERSION_BOOKWORM=$(APP_VERSION)~deb12
DEB_VERSION_TRIXIE=$(APP_VERSION)~deb13
DEB_FILE_BULLSEYE=$(DEB_NAME_BULLSEYE)_$(DEB_VERSION_BULLSEYE)_$(DEB_ARCH).deb
DEB_FILE_BOOKWORM=$(DEB_NAME_BOOKWORM)_$(DEB_VERSION_BOOKWORM)_$(DEB_ARCH).deb
DEB_FILE_TRIXIE=$(DEB_NAME_TRIXIE)_$(DEB_VERSION_TRIXIE)_$(DEB_ARCH).deb
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



install: install-prep install-app install-configs

test: test-app

update: update-front

uninstall: uninstall-front

clean: clean-front


install-prep: apt-update install-core git-config


apt-update:
	@echo ""
	@echo "Package update ---------------------------------------------------------"
	apt-get --assume-yes update

apt-upgrade:
	@echo ""
	@echo "Package upgrade --------------------------------------------------------"
	apt-get --assume-yes upgrade

install-core:
	apt-get --assume-yes install bzip2 curl gdebi-core git-core logrotate ntp p7zip-full python3 wget

git-config:
	git config --global alias.st status
	git config --global alias.co checkout
	git config --global alias.br branch
	git config --global alias.ci commit


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
	apt-get --assume-yes install python3-pip python3-venv
	python3 -m venv $(VIRTUALENV)
	source $(VIRTUALENV)/bin/activate; \
	pip3 install -U --cache-dir=$(PIP_CACHE_DIR) pip

install-setuptools: install-virtualenv
	@echo ""
	@echo "install-setuptools -----------------------------------------------------"
	apt-get --assume-yes install python3-dev
	source $(VIRTUALENV)/bin/activate; \
	pip3 install -U --cache-dir=$(PIP_CACHE_DIR) setuptools


install-app: install-virtualenv install-setuptools install-encyc-front

test-app: test-encyc-front test-encyc-events

update-app: update-encyc-front install-configs

uninstall-app: uninstall-encyc-front

clean-app: clean-encyc-front


install-encyc-front:
	@echo ""
	@echo "encyc-front --------------------------------------------------------------"
	apt-get --assume-yes install imagemagick libxml2 libxslt1.1 libxslt1-dev python3-dev sqlite3 supervisor zlib1g-dev

ifeq ($(DEBIAN_CODENAME), wheezy)
	apt-get --assume-yes install libjpeg8-dev
endif
ifeq ($(DEBIAN_CODENAME), jessie)
	apt-get --assume-yes install libjpeg62-turbo-dev
endif

# virtualenv
	source $(VIRTUALENV)/bin/activate; \
	pip3 install -U --cache-dir=$(PIP_CACHE_DIR) -r $(INSTALLDIR)/requirements.txt
	sudo -u encyc git config --global --add safe.directory $(INSTALLDIR)
# log dir
	-mkdir $(LOG_BASE)
	chown -R encyc.root $(LOG_BASE)
	chmod -R 755 $(LOG_BASE)
# sqlite db dir
	-mkdir $(SQLITE_BASE)
	chown -R encyc.root $(SQLITE_BASE)
	chmod -R 755 $(SQLITE_BASE)
# media dir
	-mkdir $(MEDIA_BASE)
	-mkdir $(MEDIA_ROOT)
	chown -R ddr.root $(MEDIA_ROOT)
	chmod -R 755 $(MEDIA_ROOT)

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
	pip3 install -U --cache-dir=$(PIP_CACHE_DIR) -r $(INSTALLDIR)/requirements.txt

uninstall-encyc-front:
	cd $(INSTALLDIR)/front
	source $(VIRTUALENV)/bin/activate; \
	-pip3 uninstall -r $(INSTALLDIR)/requirements.txt
	-rm /usr/local/lib/python$(PYTHON_VERSION)/dist-packages/front-*
	-rm -Rf /usr/local/lib/python$(PYTHON_VERSION)/dist-packages/front

restart-front:
	/etc/init.d/supervisor restart front

test-encyc-events:
	@echo ""
	@echo "test-encyc-events ``----------------------------------------------------"
	source $(VIRTUALENV)/bin/activate; \
	cd $(INSTALLDIR)/; pytest --disable-warnings --reuse-db front/events/tests.py

test-encyc-front:
	@echo ""
	@echo "test-encyc-front -------------------------------------------------------"
	source $(VIRTUALENV)/bin/activate; \
	cd $(INSTALLDIR)/; pytest --disable-warnings --reuse-db front/wikiprox/tests.py

shell:
	source $(VIRTUALENV)/bin/activate; \
	python front/manage.py shell

runserver:
	source $(VIRTUALENV)/bin/activate; \
	python front/manage.py runserver 0.0.0.0:8080

clean-encyc-front:
	-rm -Rf $(VIRTUALENV)
	-rm -Rf $(INSTALLDIR)/front/src

clean-pip:
	-rm -Rf $(PIP_CACHE_DIR)/*


install-configs:
	@echo ""
	@echo "installing configs ----------------------------------------------------"
# web app settings
	-mkdir /etc/encyc
	cp $(INSTALLDIR)/conf/front.cfg /etc/encyc/
	chown root.encyc /etc/encyc/front.cfg
	chmod 644 /etc/encyc/front.cfg
	touch /etc/encyc/front-local.cfg
	chown root.encyc /etc/encyc/front-local.cfg
	chmod 640 /etc/encyc/front-local.cfg

uninstall-configs:
	-rm $(INSTALLDIR)/front/settings.py

install-daemon-configs:
	@echo ""
	@echo "installing daemon configs ---------------------------------------------"
 # nginx settings
	cp $(INSTALLDIR)/conf/nginx.conf /etc/nginx/sites-available/encycfront.conf
	chown root.root /etc/nginx/sites-available/encycfront.conf
	chmod 644 /etc/nginx/sites-available/encycfront.conf
	-ln -s /etc/nginx/sites-available/encycfront.conf /etc/nginx/sites-enabled/encycfront.conf
	 -rm /etc/nginx/sites-enabled/default
 # supervisord
	cp $(INSTALLDIR)/conf/supervisor.conf /etc/supervisor/conf.d/encycfront.conf
	chown root.root /etc/supervisor/conf.d/encycfront.conf
	chmod 644 /etc/supervisor/conf.d/encycfront.conf

uninstall-daemon-configs:
	-rm /etc/nginx/sites-available/encycfront.conf
	-rm /etc/nginx/sites-enabled/encycfront.conf
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


tgz-local:
	rm -Rf $(TGZ_DIR)
	git clone $(INSTALL_FRONT) $(TGZ_FRONT)
	git clone $(INSTALL_ASSETS) $(TGZ_ASSETS)
	cd $(TGZ_FRONT); git checkout develop; git checkout master
	cd $(TGZ_ASSETS); git checkout develop; git checkout master
	tar czf $(TGZ_FILE).tgz $(TGZ_FILE)
	rm -Rf $(TGZ_DIR)

tgz:
	rm -Rf $(TGZ_DIR)
	git clone $(GIT_SOURCE_URL) $(TGZ_FRONT)
	git clone $(SRC_REPO_ASSETS) $(TGZ_ASSETS)
	cd $(TGZ_FRONT); git checkout develop; git checkout master
	cd $(TGZ_ASSETS); git checkout develop; git checkout master
	tar czf $(TGZ_FILE).tgz $(TGZ_FILE)
	rm -Rf $(TGZ_DIR)


# http://fpm.readthedocs.io/en/latest/
install-fpm:
	@echo "install-fpm ------------------------------------------------------------"
	apt-get install --assume-yes ruby ruby-dev rubygems build-essential
	gem install --no-document fpm

# https://stackoverflow.com/questions/32094205/set-a-custom-install-directory-when-making-a-deb-package-with-fpm
# https://brejoc.com/tag/fpm/
deb: deb-bullseye

deb-bullseye:
	@echo ""
	@echo "FPM packaging (bullseye) -----------------------------------------------"
	-rm -Rf $(DEB_FILE_BULLSEYE)
# Make package
	fpm   \
	--verbose   \
	--input-type dir   \
	--output-type deb   \
	--name $(DEB_NAME_BULLSEYE)   \
	--version $(DEB_VERSION_BULLSEYE)   \
	--package $(DEB_FILE_BULLSEYE)   \
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
	requirements.txt=$(DEB_BASE)   \
	venv=$(DEB_BASE)   \
	VERSION=$(DEB_BASE)

deb-bookworm:
	@echo ""
	@echo "FPM packaging (bookworm) -----------------------------------------------"
	-rm -Rf $(DEB_FILE_BOOKWORM)
# Make package
	fpm   \
	--verbose   \
	--input-type dir   \
	--output-type deb   \
	--name $(DEB_NAME_BOOKWORM)   \
	--version $(DEB_VERSION_BOOKWORM)   \
	--package $(DEB_FILE_BOOKWORM)   \
	--url "$(GIT_SOURCE_URL)"   \
	--vendor "$(DEB_VENDOR)"   \
	--maintainer "$(DEB_MAINTAINER)"   \
	--description "$(DEB_DESCRIPTION)"   \
	--depends "git-core"   \
	--depends "imagemagick"   \
	--depends "libxml2"   \
	--depends "libxslt1.1"   \
	--depends "libxslt1-dev"   \
	--depends "python3-dev"   \
	--depends "python3-pip"   \
	--depends "python3-venv"   \
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
	requirements.txt=$(DEB_BASE)   \
	venv=$(DEB_BASE)   \
	VERSION=$(DEB_BASE)

deb-trixie:
	@echo ""
	@echo "FPM packaging (trixie) -----------------------------------------------"
	-rm -Rf $(DEB_FILE_TRIXIE)
# Make package
	fpm   \
	--verbose   \
	--input-type dir   \
	--output-type deb   \
	--name $(DEB_NAME_TRIXIE)   \
	--version $(DEB_VERSION_TRIXIE)   \
	--package $(DEB_FILE_TRIXIE)   \
	--url "$(GIT_SOURCE_URL)"   \
	--vendor "$(DEB_VENDOR)"   \
	--maintainer "$(DEB_MAINTAINER)"   \
	--description "$(DEB_DESCRIPTION)"   \
	--depends "git-core"   \
	--depends "imagemagick"   \
	--depends "libxml2"   \
	--depends "libxslt1.1"   \
	--depends "libxslt1-dev"   \
	--depends "python3-dev"   \
	--depends "python3-pip"   \
	--depends "python3-venv"   \
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
	requirements.txt=$(DEB_BASE)   \
	venv=$(DEB_BASE)   \
	VERSION=$(DEB_BASE)
