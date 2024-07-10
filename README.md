# deltawoot

A deltachat client for chatwoot so users can talk to chatwoot encrypted.

You need to connect this bot to a working <https://www.chatwoot.com/> instance,
from now on called `example.org`.

## Get Started

For now, the only working thing is:

```
python3 -m venv venv
. venv/bin/activate
pip install -e .[dev]
export WOOT_DOMAIN=example.org
export WOOT_PROFILE_ACCESS_TOKEN=s3cr3t
export DELTAWOOT_ADDR=deltawoot@nine.testrun.org
export DELTAWOOT_PASSWORD=p4$$w0rD
deltawoot
```

You can get the `WOOT_PROFILE_ACCESS_TOKEN`
at the bottom of `https://example.org/app/accounts/1/profile/settings`.
For `DELTAWOOT_ADDR`
and `DELTAWOOT_PASSWORD`
you can use any email account.

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
DELTAWOOT_ADDR=deltawoot@nine.testrun.org
DELTAWOOT_PASSWORD=p4$$w0rD
```

Then you can start the docker container:

```
docker run -v deltawoot:/home/deltawoot/files --env-file .env -p 5000:5000 -ti deltawoot
```

### Connect the Bot to Your Chatwoot Instance

The bot needs to be reachable via HTTP from the chatwoot instance,
and you need to enter a callback URL into the chatwoot web interface.
For this, go to `https://example.org/app/accounts/1/settings/integrations`
and configure a new webhook.

For example,
If the bot is running on the same docker host as the chatwoot instance,
enter `http://host.docker.internal:5000`.
In your chatwoot instance's docker-compose file,
you will also need to add this to the sidekiq container:

```
  sidekiq:
    extra_hosts:
    - "host.docker.internal:host-gateway"
```
