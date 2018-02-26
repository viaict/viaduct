# OAuth2 API authentication.

For more detailed documentation on OAuth2, see [oauth.com](https://www.oauth.com).
If anything on this page is unclear, please get in touch by sending an e-mail to
[ict@svia.nl](mailto:ict@svia.nl) or by opening an issue.



## Client registration

All users on the site are able to register clients to interact with the OAuth
endpoints. On the site, navigate to
[/oauth/clients/](https://svia.nl/oauth/clients/) to get an overview of the
current set of your registered applications. In the same overview you can
register new clients or revoke access from third party applications.

To register a new client you have to define a name, description and a list of
valid redirect URLs. The redirect URLs can contain regular expressions, however
it is strongly recommended to use a single redirect URL for your application.
When your application needs to keep state, use the `state` parameter to pass a
set of data to the authorization server. In the response of the authorization
server, the same data will be present.

```
CALLBACK: http://example.com/path

GOOD: https://example.com/path
BAD:  http://example.com/bar
BAD:  http://example.com/
BAD:  http://example.com:8080/path
BAD:  http://subdomain.example.com:8080/path
BAD:  http://example.org
```
```
CALLBACK: http://example.com/path/*

GOOD: https://example.com/path/
GOOD: https://example.com/path/foo/bar
BAD: https://example.com/path
```

## Endpoints

There are two primary endpoints developers will be using during the OAuth
process. Your authorization endpoint is where the users will be directed to
begin the **authorization flow**. After the application obtains an authorization
code, it will exchange that code for an access token at the **token endpoint**.
The token endpoint is also responsible for issuing access tokens for other grant
types.

The endpoints for [svia.nl](https://svia.nl/) are:
- Authorization endpoint : [svia.nl/oauth/authorize/](https://svia.nl/oauth/authorize/)
- Token endpoint : [svia.nl/oauth/token/](https://svia.nl/oauth/token/)
- Revoke endpoint : [svia.nl/oauth/revoke/](https://svia.nl/oauth/revoke/)
- Token details : [svia.nl/api/token/info/](https://svia.nl/api/token/info/)

## Scopes

Scope is a way to limit an app’s access to a user’s data. Rather than granting
complete access to a user’s account, it is often useful to give apps a way to
request a more limited scope of what they are allowed to do on behalf of a user.
Scopes in requests and responses will always be space separated. This means that
when requesting multiple scopes in an URL, the space needs to be properly
encoded.

## Client Authentication

### Authorization code grant

Two step based request where the user logs in into the website and retrieves
a code. This code can be used by the third party application to request an
access token. This grant is used when the owner/developer is not the same user
as the user using the application.

```
GET /oauth/authorize/?response_type=code&client_id=CLIENT_ID&redirect_uri=REDIRECT_URI&scope=SCOPES&state=STATE
```

 - `response_type=code`, indicating that the application expects to
receive an authorization code if successful.

 - `client_id=CLIENT_ID`, the public identifier for the app.

 - `redirect_uri=REDIRECT_URI` This URL must match one of the URLs the developer
registered when creating the application.

 - `scope=SCOPE` (optional) The request may have one or more scope values indicating
access requested by the application.

 - `state=STATE` (recommended) The state parameter is used by the application to store
request-specific data and/or prevent CSRF attacks.

When the request is successful, the user will presented with the confirmation
screen where he has to authorize the application.

![Allowed access](./img/allow_access.png)

When the user has successfully accepted the terms, a request will be done to
your redirect URL.

```
GET http://example.com?code=CODE&state=STATE
```

The response will contain a code that is valid for 30 seconds, to request a
token at the token endpoint:
```
POST /oauth/token/?grant_type=authorization_code&client_id=CLIENT_ID&client_secret=CLIENT_SECRET&code=CODE&state=STATE
```

### Implicit

Two step based request where the user logs in into the website and the callback
is called with a valid access code. This code can be used by the third party
application to request an access token. This grant is used when application is
served as a web application.

```
GET /oauth/authorize/?response_type=token&client_id=CLIENT_ID&redirect_uri=REDIRECT_URI&scope=SCOPE&state=STATE
```

 - `response_type=token`, indicating that the application expects to
receive an token if successful.

 - `client_id=CLIENT_ID`, the public identifier for the app.

 - `redirect_uri=REDIRECT_URI` This URL must match one of the URLs the developer
registered when creating the application.

 - `scope=SCOPE` (optional) The request may have one or more scope values indicating
access requested by the application.

 - `state=STATE` (recommended) The state parameter is used by the application to store
request-specific data and/or prevent CSRF attacks.

When the request is successful, the user will presented with the confirmation
screen where he has to authorize the application.

![Allowed access](./img/allow_access.png)

When the user has successfully accepted the terms, a request will be done to
your redirect URL.

```
GET example.com/#access_token=TOKEN&expires_in=EXPIRES&token_type=TOKEN_TYPE&scope=SCOPES&state=STATE
```

### Password

The Password grant is used when the application exchanges the user’s username
and password for an access token. This is exactly the thing OAuth was created to
prevent in the first place, so you should never allow third-party apps to use
this grant. Third parties should only use Implicit or Authorization code Grants.

```
POST /oauth/token/?grant_type=password&username=USERNAME&password=PASSWORD&client_id=CLIENT_ID&client_secret=CLIENT_SECRET&state=STATE
```

 - `grant_type=password` to set the token type to password.

 - `username=USERNAME` The user's username for via, so in this case your e-mail.

 - `password=PASSWORD` The user's password.

 - `client_id=CLIENT_ID` the public identifier for the application.

 - `CLIENT_SECRET=CLIENT_SECRET` the private key for the application

 - `scope=SCOPE` (optional) The scope requested by the application.

`state=STATE` (recommended) The state parameter is used by the application to store
request-specific data and/or prevent CSRF attacks.

### Client Credentials

The Client Credentials grant is used when applications request an access token
to access their own resources, not on behalf of a user. In our current
implementation this means that the token will have the same rights as the user
that created the client.

```
POST /oauth/token/?grant_type=client_credentials&client_id=CLIENT_ID&client_secret=CLIENT_SECRET&state=STATE
```
 - `client_id=CLIENT_ID` the public identifier for the application.

 - `CLIENT_SECRET=CLIENT_SECRET` the private key for the application

 - `state=STATE` (recommended) The state parameter is used by the application to store
request-specific data and/or prevent CSRF attacks.


## Refresh token

After an access token expires, using it to make a request from the API will
result in an error. At this point, if a refresh token was included when the
original access token was issued, it can be used to request a fresh access token
from the authorization server:

```
POST /oauth/token?grant_type=refresh_token&client_id=CLIENT_ID&client_secret=CLIENT_SECRET&refresh_token=REFRESH_TOKEN

```

Important to know is that a refresh token is only valid for a single refresh.
This means that the response containing the new access_token, also contains a
new refresh token.

Refresh tokens are included in the Password grant and the Authentication code
grant.
## Token response

The response with an access token should contain the following properties:

 - `access_token`  The access token string as issued by the authorization server.

 - `token_type`  The type of token this is, typically just the string "bearer".

 - `expires_in`  If the access token expires, the server should reply with the
duration of time the access token is granted for.

 - `refresh_token` (optional) A refresh token that applications can use to obtain
another access token. However, tokens issued with the implicit grant cannot be
issued a refresh token.

 - `scope` The set of scopes granted by the user to the token. It is possible that
the user did not allow all scopes requested. Therefor it is a good practice to
check whether all scopes have been retrieved correctly.


Example response of the token endpoint:
```
{
    "access_token": "mYyXugyAI3Eq3n5sWemdxHEKhzkQKF",
    "expires_in": 3600,
    "token_type": "Bearer",
    "scope": "somescope",
    "refresh_token": "eFxpcraN7cERG4mRtjVENDIckd52mj",
    "version": "v2.9.0.5"
}
```

## Token inspection and basic information
Any token can be used to request basic information about the token and the user.

```
GET /api/token/info/
Authorization: Bearer TOKEN
```

Will respond with basic information regarding the user:

```
{
    "active": "true",
    "client_id": "a",
    "expires": "2018-01-06T20:22:07",
    "first_name": "Maico",
    "last_name": "Timmerman",
    "scope": [
        "read"
    ],
    "username": "maico.timmerman@gmail.com"
}
```

## Revoke access

The user explicitly wishes to revoke the application’s access, such as if they
have found an application they no longer want to use listed on their
authorizations page
