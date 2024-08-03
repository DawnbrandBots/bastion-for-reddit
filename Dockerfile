FROM python:3.12-alpine
ARG REVISION
LABEL org.opencontainers.image.title="Bastion Reddit bot"
LABEL org.opencontainers.image.authors="bastionbotdev@gmail.com"
LABEL org.opencontainers.image.licenses="AGPL-3.0-or-later"
LABEL org.opencontainers.image.revision="${REVISION}"
ENV REVISION=${REVISION}
WORKDIR /usr/src/bastion-for-reddit
COPY COPYING src/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY src .
USER 10000
ENTRYPOINT ["python", "bastion.py"]
