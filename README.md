# NbSAPI Verification Tool

`nbsapi_verify` is a standalone tool designed to verify that your API implementation conforms to the <https://nbsapi.org> OpenAPI specification.

## Installation
`pipx install nbsapi_verify` or `uv tool install nbsapi_verify`

## Configuration and Usage
Verifying your API is a two-step process:

1. Generate a verification config. This requires you to specify:
    - the host the API is running on
    - a valid username
    - the password for that username
    - the ID of that user
    - a directory for the verification config to be stored (optional: defaults to the current working directory)
    - the test type to be run: `all`, `auth`, `user`: the `auth` tests will exercise the write API functions, while the `user` tests will exercise the read API functions (defaults to `all`).

That command might look like:

```shell
nbsinfra_verify --generate \
    --host http://localhost:8000 \
    --test-type all
    --username testuser \
    --password testpass \
    --testid 1 \
    --config-dir ~
```

If the command completes sucessfully, you may run the verification tool:

```shell
nbsinfra_verify --config-dir ~
```

When all tests pass, your API implementation is conformant to the `NbsAPI` specification.

## Help
`nbsinfra_verify --help`
