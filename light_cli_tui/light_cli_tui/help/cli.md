**Unofficial CLI for the Light Phone.**

Manage music, podcasts, notes, contacts, tools, and more on your Light device from the terminal.

**Login:** Provide your email and password to get started.

1. Prompt for the password interactively:
    - `light --email <EMAIL> --ask <command>`
2. From file:
    - `light --email-file <FILE> --password-file <FILE>`
3. Using environment variables:
    - `LIGHT_EMAIL` and `LIGHT_PASSWORD`

**Multiple devices?** To target a specific device, specify one of either a phone number or a device ID.

Specifying phone number and device ID is not required if you have only one device registered to your account.

1. From file:
    - `--phone-number-file` or `--device-id-file`
2. Using environment variables:
    - `LIGHT_PHONE_NUMBER` or `LIGHT_DEVICE_ID`
3. From CLI options:
    - `--phone-number` or `--device-id`
