FROM python:3.9.2-slim

# Configure python
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8 PYTHONUNBUFFERED=1


RUN apt-get -qq update && apt-get install -y build-essential wget

# Install entr from the source. It should be patched to watch files in docker container.
# https://bitbucket.org/eradman/entr/issues/42/changes-to-files-in-docker-volumes-arent#comment-46788220
RUN wget http://eradman.com/entrproject/code/entr-3.9.tar.gz \
    && tar zvxf entr-3.9.tar.gz \
    && cd eradman-entr-332fd96a324a \
    && wget http://entrproject.org/patches/entr-3.9-wsl \
    && patch -p1 < entr-3.9-wsl \
    && ./configure \
    && make install


COPY /src  /src/
COPY tests/ /tests/
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
WORKDIR /src



# CMD ["python", "app.py"]