FROM ubuntu:20.10

WORKDIR /opt/mailer_daemon

ENV webdav_path "/python_mailer"
ENV DEBIAN_FRONTEND=noninteractive

COPY ./requirements.txt ./requirements.txt
COPY ./webdav.conf /etc/nginx/conf.d/webdav.conf
COPY ./pythonmailer.sh /etc/init.d/pythonmailer

## I send output to /dev/null because output it's mess ##
## and since install work is not important, when this  ##
## layer crash just remove sending output to /dev/null ##
RUN apt -y update >> /dev/null 2>&1 && \
    apt -y upgrade >> /dev/null 2>&1 && \
    apt -y install --no-install-recommends\
    python3.8 \
    nginx-full \
    systemctl \
    tzdata \
    pip >> /dev/null 2>&1 && \
    ## Configre warsaw timezone ##
    rm -rf /var/lib/apt/lists/* && \
    ln -fs /usr/share/zoneinfo/Europe/Warsaw /etc/localtime && \
    dpkg-reconfigure --frontend noninteractive tzdata && \
    ## Link Python3.8 to Python path ##
    ln -s /usr/bin/python3.8 /usr/local/bin/python && \
    ## Install Python packages ##
    pip install -r ./requirements.txt >> /dev/null 2>&1

## Copy all files after whole process, to use cached layer in further dev ##
COPY . .
RUN mkdir $webdav_path && \
    chown 33:33 $webdav_path

CMD systemctl start pythonmailer.service && \
    nginx -g "daemon off;"
