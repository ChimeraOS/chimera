FROM python:alpine

COPY . /srv/chimera/
RUN pip install --no-cache-dir -r /srv/chimera/requirements-container.txt

WORKDIR /srv/chimera
ENV CONTENT_SHARE_ONLY=true
CMD [ "python", "-m", "chimera_app" ]
