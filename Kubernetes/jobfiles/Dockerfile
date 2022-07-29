FROM tensorflow/tensorflow:2.6.1
COPY . ~/jobfiles
WORKDIR ~/jobfiles
RUN /bin/sh runfiles.sh
CMD /bin/sh processfiles.sh