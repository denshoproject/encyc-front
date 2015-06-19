SHELL = /bin/bash

PACKAGE_SERVER=tank.densho.org

PIP_CACHE_DIR=/usr/local/src/pip-cache
VIRTUALENV=/usr/local/src/env/front
INSTALLDIR=/usr/local/src/encyc-front
MEDIA_BASE=/var/www/html/front
MEDIA_ROOT=$(MEDIA_BASE)/media
STATIC_ROOT=$(MEDIA_BASE)/static

ELASTICSEARCH=elasticsearch-1.0.1.deb
# wget https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-1.0.1.deb

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
	@echo "    # git clone git@github.com:densho/encyc-front.git /usr/local/src/encyc-front"
	@echo "    # cd /usr/local/src/encyc-front/front"
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
	@echo "    # source /usr/local/src/env/front/bin/activate"
	@echo "    # cd /usr/local/src/encyc-front/front && python manage.py shell"
	@echo ""
	@echo "Initial database setup."
	@echo ""
	@echo "    # make syncdb"
	@echo ""
	@echo "Adjust configs to fit the local environment. Values in /etc/encyc/local.cfg"
	@echo "override those in production.cfg::"
	@echo ""
	@echo "    # vi /etc/encyc/local.cfg"
	@echo ""
	@echo "Restart::"
	@echo ""
	@echo "    # make restart"
	@echo "    # make status"



install: install-prep install-daemons install-front install-static install-configs

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

install-elasticsearch:
	@echo ""
	@echo "Elasticsearch ----------------------------------------------------------"
# Elasticsearch is configured/restarted here so it's online by the time script is done.
	apt-get --assume-yes install openjdk-7-jre
	wget -nc -P /tmp/downloads http://$(PACKAGE_SERVER)/$(ELASTICSEARCH)
	gdebi --non-interactive /tmp/downloads/$(ELASTICSEARCH)
	cp $(INSTALLDIR)/debian/conf/elasticsearch.yml /etc/elasticsearch/
	chown root.root /etc/elasticsearch/elasticsearch.yml
	chmod 644 /etc/elasticsearch/elasticsearch.yml
	@echo "${bldgrn}search engine (re)start${txtrst}"
	/etc/init.d/elasticsearch restart


install-front: install-encyc-front

update-front: update-encyc-front install-configs

uninstall-front: uninstall-encyc-front

clean-front: clean-encyc-front


install-encyc-front:
	@echo ""
	@echo "encyc-front --------------------------------------------------------------"
	apt-get --assume-yes install imagemagick libjpeg62-turbo-dev libxml2 libxslt1.1 libxslt1-dev python-dev python-pip python-virtualenv supervisor zlib1g-dev
	test -d $(VIRTUALENV) || virtualenv $(VIRTUALENV)
	source $(VIRTUALENV)/bin/activate; \
	pip install -U --download-cache=$(PIP_CACHE_DIR) bpython setuptools
	source $(VIRTUALENV)/bin/activate; \
	pip install -U --download-cache=$(PIP_CACHE_DIR) -r $(INSTALLDIR)/front/requirements/production.txt
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
	pip install -U --download-cache=$(PIP_CACHE_DIR) -r $(INSTALLDIR)/front/requirements/production.txt

uninstall-encyc-front:
	cd $(INSTALLDIR)/front
	source $(VIRTUALENV)/bin/activate; \
	-pip uninstall -r $(INSTALLDIR)/front/requirements/production.txt
	-rm /usr/local/lib/python2.7/dist-packages/front-*
	-rm -Rf /usr/local/lib/python2.7/dist-packages/front

restart-front:
	/etc/init.d/supervisor restart front

clean-encyc-front:
	-rm -Rf $(INSTALLDIR)/front/env/
	-rm -Rf $(INSTALLDIR)/front/src

clean-pip:
	-rm -Rf $(PIP_CACHE_DIR)/*



install-static: install-bootstrap install-jquery install-jwplayer install-lightview install-modernizr install-swfobject install-openlayers

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
	cp $(INSTALLDIR)/debian/conf/settings.py $(INSTALLDIR)/front/front/
	chown root.root $(INSTALLDIR)/front/front/settings.py
	chmod 644 $(INSTALLDIR)/front/front/settings.py
	-mkdir /etc/encyc
	cp $(INSTALLDIR)/debian/conf/production.cfg /etc/encyc/
	chown root.encyc /etc/encyc/production.cfg
	chmod 640 /etc/encyc/production.cfg
	touch /etc/encyc/local.cfg
	chown root.encyc /etc/encyc/local.cfg
	chmod 640 /etc/encyc/local.cfg
# nginx settings
	cp $(INSTALLDIR)/debian/conf/front.conf /etc/nginx/sites-available
	chown root.root /etc/nginx/sites-available/front.conf
	chmod 644 /etc/nginx/sites-available/front.conf
	-ln -s /etc/nginx/sites-available/front.conf /etc/nginx/sites-enabled/front.conf
	-rm /etc/nginx/sites-enabled/default
# supervisord
	cp $(INSTALLDIR)/debian/conf/gunicorn_front.conf /etc/supervisor/conf.d/
	chown root.root /etc/supervisor/conf.d/gunicorn_front.conf
	chmod 644 /etc/supervisor/conf.d/gunicorn_front.conf

uninstall-configs:
	-rm /etc/nginx/sites-available/front.conf
	-rm /etc/nginx/sites-enabled/front.conf
	-rm /etc/supervisor/conf.d/gunicorn_front.conf
	-rm $(INSTALLDIR)/front/settings.py


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
