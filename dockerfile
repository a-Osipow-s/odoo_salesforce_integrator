FROM odoo:12

USER root

RUN apt-get update && apt-get install -y \python3-pip

RUN pip3 install -U pip
RUN pip3 install simple-salesforce

RUN echo "Build complete"

USER odoo
