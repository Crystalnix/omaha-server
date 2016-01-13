FROM ubuntu-debootstrap:14.04

ENV omaha /srv/omaha

RUN \
  apt-get update && \
  apt-get install -y --no-install-recommends python-pip python-lxml python-psycopg2 uwsgi supervisor uwsgi-plugin-python nginx libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev python-pil build-essential libfuse-dev libcurl4-openssl-dev libxml2-dev mime-support automake libtool pkg-config libssl-dev wget tar && \
  apt-get clean && \
  apt-get autoremove -y && \
  rm -rf /var/lib/{apt,dpkg,cache,log}/

RUN \
  wget https://github.com/s3fs-fuse/s3fs-fuse/archive/v1.78.tar.gz -O /usr/src/v1.78.tar.gz && \
  tar xvz -C /usr/src -f /usr/src/v1.78.tar.gz && \
  cd /usr/src/s3fs-fuse-1.78 && \
  ./autogen.sh && \
  ./configure --prefix=/usr && \
  make && \
  make install && \
  mkdir /srv/omaha_s3 && \
  rm /usr/src/v1.78.tar.gz


RUN mkdir -p $omaha/requirements
WORKDIR ${omaha}

ADD ./requirements/base.txt $omaha/requirements/base.txt

RUN \
  pip install --upgrade six
    
RUN \
  pip install paver  && \
  pip install -r requirements/base.txt 

ADD . $omaha

# setup all the configfiles
RUN \
  rm /etc/nginx/sites-enabled/default && \
  rm /etc/nginx/nginx.conf && \
  ln -s /srv/omaha/conf/nginx.conf /etc/nginx/ && \
  ln -s /srv/omaha/conf/nginx-app.conf /etc/nginx/sites-enabled/ && \
  ln -s /srv/omaha/conf/supervisord.conf /etc/supervisor/conf.d/

RUN \
  wget -O /tmp/splunkforwarder-6.3.1-f3e41e4b37b2-linux-2.6-amd64.deb 'http://www.splunk.com/bin/splunk/DownloadActivityServlet?architecture=x86_64&platform=linux&version=6.3.1&product=universalforwarder&filename=splunkforwarder-6.3.1-f3e41e4b37b2-linux-2.6-amd64.deb&wget=true' && \
  dpkg -i /tmp/splunkforwarder-6.3.1-f3e41e4b37b2-linux-2.6-amd64.deb && \
  rm /tmp/splunkforwarder-6.3.1-f3e41e4b37b2-linux-2.6-amd64.deb

EXPOSE 80
CMD ["paver", "docker_run"]
