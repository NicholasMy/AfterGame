FROM ubuntu:20.04

ENV APP=/aftergame
ENV BUILD=/build_aftergame

WORKDIR $BUILD

RUN apt update
RUN apt install python3.8 python3-pip -y

# Copy the files into the build directory for temporary setup
COPY requirements.txt .

RUN pip install -r requirements.txt

# Switch to live bind location so the config file is synced with the host
WORKDIR $APP

CMD python3 -u app.py