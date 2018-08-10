FROM debian
RUN echo deb http://httpredir.debian.org/debian jessie main >> /etc/apt/sources.list
RUN echo deb http://security.debian.org jessie/updates main >> /etc/apt/sources.list
RUN useradd -m -p P3f73hKS4bInY -s /bin/false saturn
RUN apt clean && apt update
RUN apt upgrade -V
RUN apt install -y npm python3-setuptools python3-pip libpython3.5-dev python3-ipykernel python3-ipython python3-matplotlib python3-nltk python3-numpy python3-pandas python3-protobuf python3-pygments python3-sklearn python3-scipy python3-theano libzmq3-dev python3-xlrd nodejs-legacy gcc g++ git ffmpeg
RUN npm install -g configurable-http-proxy
RUN pip3 install jupyterhub
RUN pip3 install numpy
RUN pip3 install keras
RUN pip3 install tensorflow
RUN pip3 install notebook
ENTRYPOINT jupyterhub
