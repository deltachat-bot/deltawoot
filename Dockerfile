FROM python:3.11-slim
ARG CACHEBUST=1

RUN adduser deltawoot
WORKDIR /home/deltawoot
COPY . .
RUN chown deltawoot:deltawoot -R src
RUN rm -rf build/
USER deltawoot:deltawoot

ENV PATH /home/deltawoot/.local/bin:/usr/bin:/usr/sbin:/bin:/sbin:${PATH}
ENV DC_ACCOUNTS_PATH /home/deltawoot/files/accounts

RUN pip install --user .

EXPOSE 5000

USER root
ENTRYPOINT ["/bin/sh", "entrypoint.sh"]
CMD ["deltawoot"]

