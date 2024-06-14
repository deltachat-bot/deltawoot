# deltawoot
A deltachat client for chatwoot so users can talk to chatwoot encrypted.

## Get Started

For now, the only working thing is:

```
python3 -m venv venv
. venv/bin/activate
pip install -e .
PROFILE_ACCESS_TOKEN=asdf python3 src/deltawoot/quickndirty.py
```

You can get the `PROFILE_ACCESS_TOKEN`
at the bottom of <https://chatwoot.testrun.org/app/accounts/1/profile/settings>
(or by running `pass -c delta/chatwoot.testrun.org/profile_access_token`
if you have set up our secrets).
