# coding: utf8

"""
This software is licensed under the Apache 2 license, quoted below.

Copyright 2014 Crystalnix Limited

Licensed under the Apache License, Version 2.0 (the "License"); you may not
use this file except in compliance with the License. You may obtain a copy of
the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations under
the License.
"""

import os

from raven import Client
from paver.easy import task, needs
from paver.easy import sh


client = Client(os.environ.get('RAVEN_DNS'))


@task
def test():
    sh('./manage.py test --settings=omaha_server.settings_test', cwd='omaha_server')


@task
def test_tox():
    path_to_test = os.getenv("PATH_TO_TEST", '')
    settings = os.getenv("DJANGO_SETTINGS_MODULE", 'omaha_server.settings_test')
    sh('./manage.py test %s --settings=%s' % (path_to_test, settings), cwd='omaha_server')


@task
def test_postgres():
    sh('./manage.py test --settings=omaha_server.settings_test_postgres', cwd='omaha_server')


@task
@needs('test', 'test_postgres')
def test_all():
    pass


@task
def up_local_dev_server():
    """
    Requirements:

    - [docker](docker.com) or [boot2docker](https://github.com/boot2docker/boot2docker) for OS X or Windows
    - [docker-compose](https://docs.docker.com/compose/install/)

    """
    sh('docker-compose -f docker-compose.dev.yml -p dev up -d db')
    sh('docker-compose -f docker-compose.dev.yml -p dev up -d web')
    print("""Open http://{DOCKER_HOST}:9090/admin/\n username: admin\n password: admin""")


@task
def deploy_dev():
    sh('ebs-deploy deploy -e omaha-server-dev', cwd='omaha_server')


@task
def collectstatic():
    sh('./manage.py collectstatic --noinput', cwd='omaha_server')


@task
def loaddata():
    sh('./manage.py loaddata fixtures/initial_data.json', cwd='omaha_server')


@task
def migrate():
    sh('./manage.py migrate sites --noinput', cwd='omaha_server')
    sh('./manage.py migrate auth --noinput', cwd='omaha_server')
    sh('./manage.py migrate --noinput', cwd='omaha_server')


@task
def create_admin():
    sh('./createadmin.py', cwd='omaha_server')


@task
def configure_nginx():
    splunk_host = os.environ.get('SPLUNK_HOST')
    splunk_port = os.environ.get('SPLUNK_PORT', '')
    if splunk_host and splunk_port.isdigit():
        sh("sed -i 's/access_log.*;/access_log syslog:server=%s:%s main;/g' /etc/nginx/nginx.conf" % (splunk_host, splunk_port))
        sh("sed -i 's/error_log.*;/error_log syslog:server=%s:%s;/g' /etc/nginx/nginx.conf" % (splunk_host, splunk_port))
    else:
        sh("sed -i 's#access_log.*;#access_log /var/log/nginx/access.log main;#g' /etc/nginx/nginx.conf")
        sh("sed -i 's#error_log.*;#error_log /var/log/nginx/error.log;#g' /etc/nginx/nginx.conf")
    server_name = os.environ.get('HOST_NAME', '_')
    server_name = server_name if server_name != '*' else '_'
    sh("sed -i 's/server_name.*;/server_name %s;/g' /etc/nginx/sites-enabled/nginx-app.conf" % (server_name))


@task
def install_syslog():
    sh("apt-get install rsyslog curl cron unzip libwww-perl libdatetime-perl -y")
    sh("service rsyslog start")


@task
def enable_memory_monitoring():
    sh("curl http://aws-cloudwatch.s3.amazonaws.com/downloads/CloudWatchMonitoringScripts-1.2.1.zip -O")
    sh("unzip CloudWatchMonitoringScripts-1.2.1.zip")
    sh("rm CloudWatchMonitoringScripts-1.2.1.zip")
    path_to_omaha = os.getenv('omaha')
    sh("echo '*/5 * * * * %s/aws-scripts-mon/mon-put-instance-data.pl --mem-util --mem-used --mem-avail --from-cron' "\
       "> cron_config" % (path_to_omaha,))
    sh("crontab cron_config")
    sh("cron")


@task
def docker_run():
    try:
        is_memory_monitoring_enabled = True if os.environ.get('MEMORY_MONITORING_ENABLED', '').title() == 'True' else False
        if is_memory_monitoring_enabled:
            install_syslog()
            enable_memory_monitoring()
        is_private = True if os.environ.get('OMAHA_SERVER_PRIVATE', '').title() == 'True' else False

        if is_private:
            migrate()
            loaddata()
            create_admin()
            collectstatic()

        configure_nginx()
        sh('/usr/bin/supervisord')
    except:
        client.captureException()
        raise


@task
def docker_run_test():
    sh('apt-get install -y python-dev libxslt-dev libpq-dev')
    sh('pip install -r requirements/test.txt --use-mirrors')
    test()
    test_postgres()


@task
def run_test_in_docker():
    try:
        sh('docker-compose -f docker-compose.test.yml -p omaha_testing run --rm sut paver docker_run_test')
    except:
        pass
    sh('docker-compose -f docker-compose.test.yml -p omaha_testing stop')
    sh('docker-compose -f docker-compose.test.yml -p omaha_testing rm --force')
