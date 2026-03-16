
# Unofficial Light Phone III Music API

Unofficial API for uploading music to the Light Phone III, which uses browser automation (Playwright) to handle uploads.

## Usage

```
# If secrets are in env vars: LIGHT_EMAIL, LIGHT_PASSWORD, LIGHT_DEVICE_ID
python lp3_upload.py song1.mp3 song2.mp3 song3.mp3

# If secrets are in a file (i.e. with sops)
python lp3_upload.py --email=/run/secrets/email --password=/run/secrets/pw --device-id=/run/secrets/did song.mp3

# To see what Playwright is doing
python lp3_upload.py --no-headless song.mp3
```
