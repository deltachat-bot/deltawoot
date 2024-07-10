# deltawoot
A deltachat client for chatwoot so users can talk to chatwoot encrypted.

## Get Started

For now, the only working thing is:

```
python3 -m venv venv
. venv/bin/activate
pip install -e .[dev]
export WOOT_PROFILE_ACCESS_TOKEN=s3cr3t
export DELTAWOOT_ADDR=deltawoot@nine.testrun.org
export DELTAWOOT_PASSWORD=p4$$w0rD
deltawoot
```

You can get the `WOOT_PROFILE_ACCESS_TOKEN`
at the bottom of <https://chatwoot.testrun.org/app/accounts/1/profile/settings>.
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
WOOT_PROFILE_ACCESS_TOKEN=s3cr3t
DELTAWOOT_ADDR=deltawoot@nine.testrun.org
DELTAWOOT_PASSWORD=p4$$w0rD
```

Then you can start the docker container:

```
docker run -v deltawoot:/home/deltawoot/files --env-file .env -p 5000:5000 -ti deltawoot
```

