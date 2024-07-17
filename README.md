# deltawoot

A deltachat bot which acts as a chatwoot client,
so users can talk to chatwoot encrypted.

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
export WOOT_INBOX_ID=1
export WOOT_ACCOUNT_ID=1
export DELTAWOOT_ADDR=deltawoot@nine.testrun.org
export DELTAWOOT_PASSWORD=p4$$w0rD
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
The default is 1.
You might need it if you get a 404 error in the logs
when deltawoot tries to connect to the chatwoot API.

For the `WOOT_ACCOUNT_ID`,
go to the Chatwoot conversations list
where you want Delta Chat messages to pop up,
e.g. the one which appears directly after logging in.
It should look like `https://example.org/app/accounts/1/dashboard`.
The `WOOT_ACCOUNT_ID` should be the only number in the URL,
in this example `1`, as it is the default.
You might need it if you get a 404 error in the logs
when deltawoot tries to connect to the chatwoot API.

### Extended Configuration

You can set other environment variables for configuring deltawoot,
for example:

```
export DELTAWOOT_NAME=Your friendly Chatwoot Bridge
export DELTAWOOT_AVATAR=files/avatar.jpg
export DELTAWOOT_HELP_MSG="Hi, ask me for cooking recipes!"
export DELTAWOOT_LEAVE_MSG="Please don't add me to groups, write me 1:1 instead."
```

`DELTAWOOT_NAME` will be the bot's display name in Delta Chat.

`DELTAWOOT_AVATAR` will be the bot's avatar in Delta Chat;
if you run deltawoot in docker,
you need to put it into the docker volume,
and prepend the path with `files/`.

`DELTAWOOT_HELP_MSG` is what the bot replies
if you send `/help` to it.
You can customize it in your language.

If you try to add the bot to a group,
the bot will leave the group at once,
but send the person who added it an explanation.
`DELTAWOOT_LEAVE_MSG` is what the bot says
in such a situation.

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
DELTAWOOT_NAME=Your friendly Chatwoot Bridge
DELTAWOOT_AVATAR=files/avatar.jpg
WOOT_INBOX_ID=1
WOOT_ACCOUNT_ID=1
DELTAWOOT_HELP_MSG="Hi, ask me for cooking recipes!"
DELTAWOOT_LEAVE_MSG="Please don't add me to groups, write me 1:1 instead."
```

Then you can start the docker container:

```
docker run -v deltawoot:/home/deltawoot/files --env-file .env -p 5000:5000 -ti deltawoot
```

Now you can look into the logs
with `docker logs -ft deltawoot`,
to find out the join code of the bot:

```
2024-07-10T14:20:22.427084078Z INFO:root:Running deltachat core v1.141.2
2024-07-10T14:20:22.431288436Z You can publish this invite code to your users: OPENPGP4FPR:AA5FDEF02BFC355FDEA09FF4CA4AFCD2F065E613#a=deltawoot%40nine.testrun.org&n=deltawoot%40nine.testrun.org&i=q4DhTVr1T2A&s=mT3Bo9JDdVx
2024-07-10T14:20:22.437551296Z  * Serving Flask app 'deltawoot-webhook'
2024-07-10T14:20:22.438395066Z  * Debug mode: on
2024-07-10T14:20:22.451052630Z INFO:root:src/securejoin.rs:126: Generated QR code.
2024-07-10T14:20:22.451080018Z INFO:root:src/scheduler.rs:66: starting IO
```

Copy-paste the `OPENPGP4FPR:` and everything behind it
into the form at <https://i.delta.chat>
to generate an invite link which you can advertise on your contact page.

