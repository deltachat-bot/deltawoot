# deltawoot

A deltachat client for chatwoot so users can talk to chatwoot encrypted.

## Configure Chatwoot

You need to connect this bot to a working <https://www.chatwoot.com/> instance,
from now on called `example.org`.
Let's configure it first.

### Create an API channel

You need to [create an API channel](https://www.chatwoot.com/hc/user-guide/articles/1677839703-how-to-create-an-api-channel-inbox#setup-the-api-channel).
Make sure to leave the webhook URL empty.

### Configure a callback URL

The bot needs to be reachable via HTTP from the chatwoot instance,
and you need to enter a callback URL into the chatwoot web interface.
For this, go to `https://example.org/app/accounts/1/settings/integrations`
and configure a new webhook.

For example,
If the bot is running on the same docker host as the chatwoot instance,
enter `http://host.docker.internal:5000`,
and enable the `message_created` option.
In your chatwoot instance's docker-compose file,
you will also need to add this to the sidekiq container:

```
  sidekiq:
    extra_hosts:
    - "host.docker.internal:host-gateway"
```

## Get Started

In principle, deltawoot can be configured and started like this:

```
python3 -m venv venv
. venv/bin/activate
pip install -e .[dev]
export WOOT_DOMAIN=example.org
export WOOT_PROFILE_ACCESS_TOKEN=s3cr3t
export DELTAWOOT_ADDR=deltawoot@nine.testrun.org
export DELTAWOOT_PASSWORD=p4$$w0rD
export WOOT_INBOX_ID=1
deltawoot
```

You can get the `WOOT_PROFILE_ACCESS_TOKEN`
at the bottom of `https://example.org/app/accounts/1/profile/settings`.
For `DELTAWOOT_ADDR`
and `DELTAWOOT_PASSWORD`
you can use any email account.

For the `WOOT_INBOX_ID`,
go to the settings of the API channel you created above
at `example.org/app/accounts/1/settings/inboxes/list`,
and look at the number at the end of the URL.

### Run it with Docker

First, cd into this repository and build the docker container:

```
docker build -t deltawoot .
docker volume create deltawoot
```

Then you need to add your environment variables to an `.env` file.
It should look like this for example:

```
WOOT_DOMAIN=example.org
WOOT_PROFILE_ACCESS_TOKEN=s3cr3t
WOOT_INBOX_ID=1
DELTAWOOT_ADDR=deltawoot@nine.testrun.org
DELTAWOOT_PASSWORD=p4$$w0rD
```

Then you can start the docker container:

```
docker run -v deltawoot:/home/deltawoot/files --env-file .env -p 5000:5000 -ti deltawoot
```
