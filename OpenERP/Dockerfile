FROM debian:wheezy
# Update the system
ENV DEBIAN_FRONTEND="noninteractive"
RUN DEBIAN_FRONTEND=noninteractive apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get dist-upgrade -V -y
# Install packages
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y postgresql python python-psycopg2 python-reportlab python-egenix-mxdatetime python-tz python-pychart python-mako python-pydot python-lxml python-vobject python-yaml python-dateutil python-pychart python-webdav python-cherrypy3 python-formencode python-pybabel python-simplejson python-pyparsing python-pybabel wget
# Create OpenERP user
RUN useradd -m --system --home=/opt/openerp openerp
# Copy files
COPY server /opt/openerp
COPY openerp-server.conf /etc
# Start postgresql
#ENTRYPOINT service postgresql start
#CMD service postgresql start
# Expose port 8069
EXPOSE 8069/tcp
# Run OpenERP server
USER openerp
ENTRYPOINT /opt/openerp/bin/openerp-server.py --config /etc/openerp-server.conf
