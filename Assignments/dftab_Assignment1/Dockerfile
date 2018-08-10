FROM debian
RUN echo deb http://httpredir.debian.org/debian jessie main >> /etc/apt/sources.list
RUN echo deb http://security.debian.org jessie/updates main >> /etc/apt/sources.list
RUN useradd -m -p P3f73hKS4bInY -s /bin/false saturn
RUN apt clean && apt update
RUN apt clean && apt update && apt upgrade -V
RUN apt clean && apt update && apt install -y npm python3-setuptools python3-pip libpython3.5-dev python3-matplotlib python3-nltk python3-numpy python3-pandas python3-protobuf python3-pygments python3-sklearn python3-scipy python3-theano libzmq3-dev python3-xlrd nodejs-legacy gcc g++ git ffmpeg apache2
RUN a2enmod headers proxy_http proxy_wstunnel rewrite
RUN npm install -g configurable-http-proxy
RUN pip3 install jupyterhub
RUN pip3 install numpy
RUN pip3 install keras
RUN pip3 install tensorflow
RUN pip3 install notebook
RUN pip3 install -U ipykernel
COPY 000-default.conf /etc/apache2/sites-available/000-default.conf
COPY jupyterhub_config.py /etc/jupyterhub_config.py
ENTRYPOINT service apache2 start && jupyterhub -f /etc/jupyterhub_config.py
