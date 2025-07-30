# pyfreeipa

Python module for accessing the FreeIPA/Red Hat Identity Manager API (a.k.a IPA)

This module does not do any exception handling, it wants your code to handle exceptions.

# Usage

The following sample sets up a IPA API object with minimal configuration.

```python
from pyfreeipa.Api import Api

ipaapi = Api(
    host="ipa.example.org",
    username="ipauser",
    password="somethingsecret"
)

response = ipaapi.ping()

if response.ok:
    result = response.json()['result']
    print('Good: %s' & result['summary'])
else:
    print('Bad: %s' % response.status_code)
```

Included is a `configuration` method that can read all the required configuration options from a yaml file.

# Examples

The `pyfreeipa` module itself can be executed as a wrapper script around `pyfreeipa.Api`

There are also some test scripts that demonstrate it's capabilites in the `test` directory, they have their own [documentation](tests/README.md).

# FreeIPA API Methods

The `Api` object supports both implemented and unimplemented methods

## Unimplemented Methods

Unimplemented methods are supported via the `Api.request()` method:

```python
from pyfreeipa.Api import Api

ipaapi = Api(
    host="ipa.example.org",
    username="ipauser",
    password="somethingsecret"
)

ipaapi.request(
    method='group_add_member',
    args=['groupname'],
    parameters={
        'users': [
            'anne',
            'bob',
            'claire'
        ]
    }
)
```


## Implemented Methods

The API methods implemented is incomplete as we're only adding them as we need them, each of these methdos includes some sanity checking, doing case insensitivity checks where necessary, and cleaning up the output so it's predictably formatted.

- `user_show`
- `user_find`
- `user`
- `users`
- `userlist`
- `user_getattr`
- `user_mod`
- `user_add`
- `group_find`
- `group`
- `groups`
- `grouplist`
- `group_add_member`
- `otptoken_find`
- `otptoken_show`
- `otptoken`
- `otptokens`
- `otptoken_remove_managedby`
- `otptoken_add_managedby`
- `otptoken_add`

# Other Methods

The `Api` object has a some methods that do not directly relate to requests to the IPA API

## `login()`

The IPA API login process that isn't standard HTTPS authentication, this method initiates the login and should be sufficient to maintain login througout a session.

## `get()`

A passthrough function that sends a `GET` request to the IPA API session. Returns a `requests.response` object.

## `post()`

A passthrough function that sends a `POST` request to the IPA API session. Returns a `requests.response` object.

## `put()`

A passthrough function that sends a `PUT` request to the IPA API session. Returns a `requests.response` object.

## `request()`

This function checks and verifies it's argments and converts regular string, dictionary, and list objects and converts them into the required data types to submit as a request, executes the request and returns a `requests.Response` object.

### Parameters

* `method` A the IPA API method to be called
* `args` A list of arguments for the method
* `params` A dictionary of parameters for the method

## `preprequest()`

This function checks and verifies it's argments and converts regular string, dictionary, and list objects and converts them into the required data types to submit as a request, executes the request and returns a `requests.PreparedRequest` object.

The use of `preprequest()` and `send()` methods allow a `POST` request to be prepared, then it can be examined or checked, and then if it's valid the `send()` method can execute it. Another use case is a 'dry run' scenario where the request can be prepared, but not executed.

### Parameters

* `method` A the IPA API method to be called
* `args` A list of arguments for the method
* `params` A dictionary of parameters for the method

## `send()`

This function sends a prepared request from the `preprequest()` function and sends it to be executed and returns a `requests.Response` object.

### Parameters

* `preprequest` A `requests.PreparedRequest` object, as per what's produced by `preprequest()`

## `warnings`

Emits a list of warnings that have occured.

## `clearwarnings()`

Clears the warnings list.
