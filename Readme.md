# HaveIBeenpwned Check

This is a python script to batch check emails addresses against the HIBP database and generate notification emails.

This was designed to be used for use in a small business to monitor users emails without having to individually sign them up to the HIBP notification service.

```
usage: hibp_check.py [-h] [-v] [-q] [-c CONFIG_FILE] [-n]

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         Print Version Number
  -q, --quiet           Disable console output
  -c CONFIG_FILE, --configuration CONFIG_FILE
                        Specify a different config file
  -n, --no-email        Disable email output
  -d, --delete-data     Delete saved breach data
```

Not affiliated with haveibeenpwned.com

## Installation

Note: Ensure you modify config.yml to suite your setup prior to running. It is recommended for the first run to use the `-n` option to test, then use the `-d` option to clear saved breach information in order to issue notifications.

```
$: git clone https://github.com/dugite-code/hibp_check.git
[...]
$: virtualenv ./env --python=python3
[...]
$: . ./env/bin/activate
(env) $: cd hibp_check
(env) $: pip install -r requirements.txt
[...]
(env) $: cp config.yml.dist config.yml
```

## Customizing the emails

The emails are generated using the [mako templating engine](https://www.makotemplates.org/)

### Variables used in the Templates

Main email wrapper section
```
${email}
${admin}
${body}
```

Breaches section
```
${title}
${date}
${domain}
${description}
${categories}
```

# Buy me a Beer

| Bitcoin  | Litecoin |
| ------------- | ------------- |
| <p align="center"><img alt="image" align="middle" style="max-width: 250px;" src="https://raw.githubusercontent.com/dugite-code/Icons/master/Donation%20Icons/bitcoin.svg?sanitize=true"></p> | <p align="center"><img alt="image" style="max-width: 250px;" src="https://raw.githubusercontent.com/dugite-code/Icons/master/Donation%20Icons/litecoin.svg?sanitize=true"></p> |
| **Bitcoin Address:** 155xGQ2sPt2BAbmLUp5myyfjLmAm3c8pPP | **Litecoin Address:** LNiBt4ksgDgTqGq4BYcLS8vtNkdn1Lrmmh |

**Website:** [PeekRead.Info](https://peekread.info)
