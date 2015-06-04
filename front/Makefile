SHELL = /bin/bash

PACKAGE_SERVER=tank.densho.org

PIP_CACHE_DIR=/usr/local/src/pip-cache
VIRTUALENV=/usr/local/src/env/front
INSTALLDIR=/usr/local/src/encyc-front

ELASTICSEARCH=elasticsearch-1.0.1.deb
# wget https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-1.0.1.deb
BOOTSTRAP=bootstrap-3.1.1-dist
JQUERY=jquery-1.11.0.min.js
JWPLAYER=jwplayer-5.9
LIGHTVIEW=lightview-3.2.2
MODERNIZR=modernizr-2.6.2
SWFOBJECT=swfobject-2.2
# wget https://github.com/twbs/bootstrap/archive/v2.0.4.zip
# wget http://code.jquery.com/jquery-1.7.2.min.js
# wget http://modernizr.com/downloads/modernizr-2.5.3.js
# jwplayer-5.9
# lightview-3.2.2
# wget https://swfobject.googlecode.com/files/swfobject_2_2.zip
ASSETS=encyc-front-assets.tar.gz

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
	@echo "Switch to branch if not running master::"
	@echo ""
	@echo "    # git checkout -b develop origin/develop"
	@echo ""
	@echo "Install encyc-front::"
	@echo ""
	@echo "    # make install"
	@echo "    # make syncdb"
	@echo ""
	@echo "Turn on DEBUG mode if not running in production::"
	@echo ""
	@echo "    # vi /usr/local/src/encyc-front/front/front/settings.py"
	@echo "    DEBUG = True"
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
	cp /usr/local/src/encyc-front/debian/conf/elasticsearch.yml /etc/elasticsearch/
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
	source $(VIRTUALENV)/bin/activate
	pip install -U --download-cache=$(PIP_CACHE_DIR) bpython setuptools
	pip install -U --download-cache=$(PIP_CACHE_DIR) -r /usr/local/src/encyc-front/front/requirements/production.txt
	-mkdir /var/log/encyc
	chown -R encyc.root /var/log/encyc
	chmod -R 755 /var/log/encyc
# sqlite db dir
	-mkdir /var/lib/encyc
	chown -R encyc.root /var/lib/encyc
	chmod -R 755 /var/lib/encyc
	-mkdir -p /var/www/front/media
	chown -R encyc.root /var/www/front
	chmod -R 755 /var/www/front

syncdb:
	source $(VIRTUALENV)/bin/activate
	cd /usr/local/src/encyc-front/front && python manage.py syncdb --noinput
	chown -R encyc.root /var/lib/encyc
	chmod -R 750 /var/lib/encyc
	chown -R encyc.root /var/log/encyc
	chmod -R 755 /var/log/encyc

update-encyc-front:
	@echo ""
	@echo "encyc-front --------------------------------------------------------------"
	git fetch && git pull
	source $(VIRTUALENV)/bin/activate; \
	pip install -U --download-cache=$(PIP_CACHE_DIR) -r /usr/local/src/encyc-front/front/requirements/production.txt

uninstall-encyc-front:
	cd /usr/local/src/encyc-front/front
	source $(VIRTUALENV)/bin/activate; \
	-pip uninstall -r /usr/local/src/encyc-front/front/requirements/production.txt
	-rm /usr/local/lib/python2.7/dist-packages/front-*
	-rm -Rf /usr/local/lib/python2.7/dist-packages/front

restart-front:
	/etc/init.d/supervisor restart front

clean-encyc-front:
	-rm -Rf /usr/local/src/encyc-front/front/env/
	-rm -Rf /usr/local/src/encyc-front/front/src

clean-pip:
	-rm -Rf $(PIP_CACHE_DIR)/*



install-static: install-bootstrap install-jquery install-jwplayer install-lightview install-modernizr install-swfobject

get-assets:
	@echo ""
	@echo "get assets --------------------------------------------------------------"
	-mkdir -p /var/www/front
	chown -R root.root /var/www/front
	chmod -R 755 /var/www/front
	wget -nc -P /tmp http://$(PACKAGE_SERVER)/$(ASSETS)
	tar xzvf /tmp/encyc-front-assets.tar.gz -C /var/www/

install-bootstrap:
	@echo ""
	@echo "Bootstrap --------------------------------------------------------------"
	wget -nc -P /tmp/ http://$(PACKAGE_SERVER)/$(BOOTSTRAP).zip
	7z x -y -o/var/www/front/static/ /tmp/$(BOOTSTRAP).zip

install-jquery:
	@echo ""
	@echo "jQuery -----------------------------------------------------------------"
	wget -nc -P /var/www/front/static/ http://$(PACKAGE_SERVER)/$(JQUERY)

install-jwplayer:
	@echo ""
	@echo "jwplayer ---------------------------------------------------------------"
	-wget -nc -P /tmp/ http://$(PACKAGE_SERVER)/$(JWPLAYER).tgz
	-tar xzf /tmp/$(JWPLAYER).tgz -C /tmp/
	-mv /tmp/$(JWPLAYER) /var/www/front/static/

install-lightview:
	@echo ""
	@echo "lightview --------------------------------------------------------------"
	-wget -nc -P /tmp/ http://$(PACKAGE_SERVER)/$(LIGHTVIEW).tgz
	-tar xzf /tmp/$(LIGHTVIEW).tgz -C /tmp/
	-mv /tmp/$(LIGHTVIEW) /var/www/front/static/

install-modernizr:
	@echo ""
	@echo "Modernizr --------------------------------------------------------------"
	-rm /var/www/front/static/js/$(MODERNIZR)*
	-wget -nc -P /var/www/front/static/ http://$(PACKAGE_SERVER)/$(MODERNIZR).js

install-swfobject:
	@echo ""
	@echo "swfobject --------------------------------------------------------------"
	-wget -nc -P /tmp/ http://$(PACKAGE_SERVER)/$(SWFOBJECT).zip
	-7z x -y -o/tmp/ /tmp/$(SWFOBJECT).zip
	-mv /tmp/swfobject/ /var/www/front/static/$(SWFOBJECT)

set-perms:
#	recursively chmod directories 755, files 644
#	from CWD
	for i in `find /var/www/front/ -type d`; do chmod 755 $i; done
	for i in `find /var/www/front/ -type f`; do chmod 644 $i; done


clean-static: clean-bootstrap clean-jquery clean-jwplayer clean-lightview clean-modernizr clean-swfobject

clean-bootstrap:
	-rm -Rf /var/www/front/static/$(BOOTSTRAP)

clean-jquery:
	-rm -Rf /var/www/front/static/$(JQUERY)

clean-jwplayer:
	-rm -Rf /var/www/front/static/$(JWPLAYER)

clean-lightview:
	-rm -Rf /var/www/front/static/$(LIGHTVIEW)

clean-modernizr:
	-rm /var/www/front/static/$(MODERNIZR).js

clean-swfobject:
	-rm -Rf /var/www/front/static/$(SWFOBJECT)


install-configs:
	@echo ""
	@echo "installing configs ----------------------------------------------------"
# web app settings
	cp /usr/local/src/encyc-front/debian/conf/settings.py /usr/local/src/encyc-front/front/front/
	chown root.root /usr/local/src/encyc-front/front/front/settings.py
	chmod 644 /usr/local/src/encyc-front/front/front/settings.py
# nginx settings
	cp /usr/local/src/encyc-front/debian/conf/front.conf /etc/nginx/sites-available
	chown root.root /etc/nginx/sites-available/front.conf
	chmod 644 /etc/nginx/sites-available/front.conf
	-ln -s /etc/nginx/sites-available/front.conf /etc/nginx/sites-enabled/front.conf
	-rm /etc/nginx/sites-enabled/default
# supervisord
	cp /usr/local/src/encyc-front/debian/conf/gunicorn_front.conf /etc/supervisor/conf.d/
	chown root.root /etc/supervisor/conf.d/gunicorn_front.conf
	chmod 644 /etc/supervisor/conf.d/gunicorn_front.conf

uninstall-configs:
	-rm /etc/nginx/sites-available/front.conf
	-rm /etc/nginx/sites-enabled/front.conf
	-rm /etc/supervisor/conf.d/gunicorn_front.conf
	-rm /usr/local/src/encyc-front/front/settings.py


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
	/etc/init.d/redis-server status
	/etc/init.d/elasticsearch status
	/etc/init.d/nginx status
	supervisorctl status

git-status:
	@echo "------------------------------------------------------------------------"
	cd /usr/local/src/encyc-front && git status
