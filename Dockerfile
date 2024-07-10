FROM python:3.11-slim

RUN adduser deltawoot
WORKDIR /home/deltawoot
COPY . .
RUN chown deltawoot:deltawoot -R src
USER deltawoot:deltawoot

ENV PATH /home/deltawoot/.local/bin:/usr/bin:/usr/sbin:/bin:/sbin:${PATH}
ENV DC_ACCOUNTS_PATH /home/deltawoot/files/accounts

RUN pip install --user .

EXPOSE 5000

USER root
ENTRYPOINT ["/bin/sh", "entrypoint.sh"]
CMD ["deltawoot"]

