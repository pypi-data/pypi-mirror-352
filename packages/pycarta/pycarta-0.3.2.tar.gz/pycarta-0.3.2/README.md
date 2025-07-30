# Summary

The goal behind `pycarta` is to simplify administrative actions, such as
assigning user permission, creating groups, and registering services,
requiring authentication, setting up and calling Carta services.

Many projects restrict who has access to information or analyses.
`pycarta` makes enforcing those access controls simple and painless.
While `pycarta` has many other uses, one of the most important allows
you, the developer, to control who has permission to execute your code
using the `@pycarta.authorize` decorator.

``` python
import pycarta

@pycarta.authorize(groups=["MyOrg:MyGroup"])
def my_function(*args, **kwds):
    # Code you want to protect.
    pass
```

Anyone not authorized to run `my_function` will receive an
`AuthenticationError`. Other functions, such as those defined in
`administrative_tasks`{.interpreted-text role="ref"} can be used to
setup who ultimately falls within these permissions.

# Definitions

Throughout, this documentation will refer to a number of Carta-specific
concepts and, while every effort has been made to remain true to the
*prima facia* meaning of terms, there are some nuances that may be
important in certain circumstances.

Group

    One or more users may form a group. This is particularly useful for
    assigning permissions to various Carta resources.

Resource

    Carta resources include authentication, projects, secrets, and
    services. Some, specifically projects and services, can be shared
    using the Carta permission system. Others (authentication and
    secrets) are specific to the user and cannot be shared.

Permissions

    As with other permission systems, Carta Permisions allows owners to
    share access to resources with other users, with groups, and even
    with other resources based on the users\' roles. Each resource will
    have exactly one owner, but other users may be granted admin, read,
    write, execute, and clone permissions. An *admin*, like the owner,
    may grant or rescind permission to anyone (except the owner). *read*
    and *write* permissions have their obvious meaning. *execute*
    permissions, which is particularly relevant to services, determine
    whether a user can make a call to (execute) the action accessible
    through the service API. Finally, *clone* permissions allow select
    resources to be duplicated, similar to forking a repository.

Project

    Projects are the basic unit of organization in Carta. While not
    required, projects generally correlate to an organization.

Secrets

    Carta provides a secure method for temporarily storing small
    secrets, such as usernames, passwords, tokens, etc. and are useful
    for accessing third-party resources. Because of their sensitive
    nature, secrets may not be shared between users.

Service

    A central function for Carta is to act as a proxy that abstracts
    away the details of a backend, third-party resource. Services are
    APIs exposed and authenticated through Carta. These are scoped with
    a `namespace`, which must be unique across the Carta platform, and a
    `service`, the name of the service. The functionality of the service
    is exposed through
    `https://carta.contextualize.us.com/<namespace>/<service>/{endpoints}`.

User

    A user is someone who has registered an account with Carta.

# Feature Request/Bug-Fix

For login issues, please contact
<customer.service@contextualize.us.com>.

To request a new feature or to report a bug, please email
[pycarta](mailto:a.t.901104402411.u-26296181.4165918c-9632-497d-8601-dfcb2f66ba78@tasks.clickup.com).
Please be sure to describe the goal of the new feature or, for a bug
report, a minimum code that reproduces the error. Note that if you
submit a feature request or bug report, the developers reserve the right
to contact you about that request.
