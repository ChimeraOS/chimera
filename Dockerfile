FROM python:alpine

COPY . /srv/chimera/
RUN pip install --no-cache-dir -r /srv/chimera/requirements-container.txt

WORKDIR /srv/chimera
ENV CONTENT_SHARE_ONLY=true XDG_DATA_HOME=/data XDG_CONFIG_HOME=/data XDG_CACHE_HOME=/data
USER 1000:1000
CMD [ "python", "-m", "chimera_app" ]
