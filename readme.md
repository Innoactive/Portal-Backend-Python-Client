# Innoactive Portal Python Client

Command-line client for Innoactive Portal's APIs, written in Python.

## Installation

To install it via pip (currently not published via pypi), run:

```sh
pip install portal-client@git+https://github.com/Innoactive/Portal-Python-CLI.git@main
```

## Usage

```bash
$ innoactive-portal --help
usage: innoactive-portal [-h] {auth,applications,upload-app,upload-client,users,groups,branding,organizations,vms} ...

positional arguments:
  {auth,applications,upload-app,upload-client,users,groups,branding,organizations,vms}
                        Help on specific commands
    auth                Authenticate against Portal (interactive browser login)
    applications        Manage application versions on Portal
    upload-app          Upload of applications / application versions to Portal
    upload-client       Upload of client applications to Portal
    users               Manage user accounts on Portal
    groups              Manage user groups on Portal
    branding            Manage branding on Portal
    organizations       Manage organizations on Portal
    vms                 Manage Virtual Machines

options:
  -h, --help            show this help message and exit
```

## Authentication

The easiest way to authenticate is to log in interactively via the browser. Given the
credentials of an OAuth client registered on Portal, the CLI runs the OAuth2
authorization code flow: it opens your browser to sign in and stores the resulting
access token locally, so subsequent commands work without any further setup.

```sh
innoactive-portal auth login --client-id <your-oauth-client-id>
```

For a confidential client, also pass its secret:

```sh
innoactive-portal auth login --client-id <your-oauth-client-id> --client-secret <your-oauth-client-secret>
```

The redirect URI defaults to `http://localhost:8723/callback` and must be registered as
one of the client's redirect URIs on Portal. Override it with `--redirect-uri` if your
client uses a different one. You can also request specific scopes with `--scope` and
suppress opening the browser (printing the URL instead) with `--no-browser`.

Rather than passing them on the command line every time, you can configure the OAuth
client via environment variables or a config file. For each setting the precedence is:
CLI flag, then environment variable, then config file, then the built-in default.

Supported environment variables:

```sh
export PORTAL_BACKEND_CLIENT_ID=your-oauth-client-id
export PORTAL_BACKEND_CLIENT_SECRET=your-oauth-client-secret   # confidential clients only
export PORTAL_BACKEND_REDIRECT_URI=http://localhost:8723/callback
export PORTAL_BACKEND_OAUTH_SCOPE="read write"
```

Or a config file at `~/.config/innoactive-portal/config.json` (honoring
`XDG_CONFIG_HOME`):

```json
{
  "client_id": "your-oauth-client-id",
  "client_secret": "your-oauth-client-secret",
  "redirect_uri": "http://localhost:8723/callback",
  "scope": "read write"
}
```

With either configured, logging in is simply:

```sh
innoactive-portal auth login
```

The obtained token is stored in `~/.config/innoactive-portal/credentials.json` (honoring
`XDG_CONFIG_HOME`). To check your current status or log out again, use:

```sh
innoactive-portal auth status
innoactive-portal auth logout
```

Alternatively, you can provide credentials as environment variables. You can use either a Bearer token issued by Portal or a user's username (email address) and password combination. These always take precedence over a token stored via `auth login`.

To use a bearer token, set:

```sh
export PORTAL_BACKEND_ACCESS_TOKEN=my-supersecure-token
```

To use a user's credentials use:

```sh
export PORTAL_BACKEND_USERNAME=jane.doe@example.org
export PORTAL_BACKEND_PASSWORD=supersecure-password
```

## Configuration

Apart from the authentication credentials, you can also opt to run the client against another Portal instance than the default, which is `https://api.innoactive.io`.

To use another Portal instance, set the environment variable like:

```sh
export PORTAL_BACKEND_ENDPOINT=https://my-portal-instance.example.org
```

For VM management, you can also configure the session management endpoint. The default is `https://session-management.innoactive.io`.

To use a different session management endpoint, set:

```sh
export PORTAL_SESSION_MANAGEMENT_ENDPOINT=https://my-session-mgmt.example.org
```

## Examples

### Uploading a (new) application build

You will need the application's identity from Portal as well as the application archive (.zip or .apk) to be uploaded.

```sh
innoactive-portal applications v2 upload-build \
./my-new-app-version.zip \ # application archive to be uploaded
--application-id 8feaa9c8-5aaf-4d49-8eef-0c20e8c73d9c \ # the id of the application this version belongs to
--version 1.0.2 \ # version number of the new version
--xr-platform win-non-vr \ # the XR platform this version is for, can be specified multiple times for multiple platforms
--launch-args='--my-custom-arg' \ # custom launch arguments for the application
--changelog='This version contains some bugfixes and new features' # changelog for the new version
```

You can run `innoactive-portal applications v2 upload-build --help` to get more information on available parameters.

## Development

To run the client locally, you can clone the repository and install the dependencies via uv:

```sh
git clone https://github.com/Innoactive/Portal-Python-CLI.git
cd Portal-Python-CLI
uv sync --locked
```

To run the client, you can use the `uv run` command:

```sh
uv run python -m portal_client --help
```
