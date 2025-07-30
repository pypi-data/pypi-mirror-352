.. _quickstart:

Quick Start
===========

.. contents::


Authentication
--------------

Authentication is central to ``pycarta`` operation. This is handled on a session
basis to free the user from having to explicitly pass around an Authorization
Agent. There are several ways to authenticate:

Username and Password
^^^^^^^^^^^^^^^^^^^^^

A call to ``pycarta.login(username=<Carta username>, password=<Carta password>)``
will authenticate into the default environment. Alternatively, a user can be
prompted for their username and password using a pop-up interactive dialogue,
``pycarta.login(interactive=True)``.

.. note::

    By default, Carta will attempt to login to the Carta production host. If
    you need to log into the Carta development host you must specify the
    environment, e.g. ``pycarta.login(environment="development")`` or set an
    environment variable ``CARTA_ENV=development``.
    
    For special Carta deployments or for testing, an explicit host may be
    specified that supercedes the ``environment`` keyword, e.g.
    ``pycarta.login(host="https://...")``. However, this is a very rare use
    case and hardly worth mentioning.

Profiles
^^^^^^^^

A single user may hold several roles and need to pivot between Carta accounts.
While this is possible through repeated username/password challenges, such
challenges can be inconvenient. To accommodate this, users may setup a profile
file that stores usernames, passwords, and environments that are used
regularly. ``pycarta`` will look in ``$HOME/.carta/admin_tools/profiles.ini``
for profiles. These use a standard config format, e.g.::

    [sandbox]
    username = <USERNAME>
    environment = development
    password = <PASSWORD>

    [production]
    username = <USERNAME>
    environment = production
    password = <PASSWORD>

Once you log in, this file will also contain the Carta API token for this
account, which will be updated as needed and should not be specified
explicitly.

Profiles may be managed programmatically, e.g. using basic CRUD (Create,
Retrieve, Update, and Delete) operations

.. code:: python

    from pycarta.auth import CartaConfig, Profile, ProfileNotFoundException

    config = CartaConfig()

    # Get a list of available profiles
    profiles = config.get_profiles()

    # Create a new profile
    profile = Profile(
        username="test_user",
        environment="production",  # or "development"
        password="your_secure_password",
        profile_name="test_profile",
    )
    config.save_profile("test_profile", profile)

    # Retrieve an existing profile
    try:
        profile = config.get_profile("test_profile")
    exception ProfileNotFoundException:
        # If not found, a ProfileNotFoundException is raised.
        profile = None

    # Update an existing profile
    profile = config.get_profile("test_profile")
    profile.password = "new_password"
    config.save_profile("test_profile", profile)

    # Delete a profile
    config.delete_profile("test_profile")

Profiles may also be managed interactively using the Carta profile UI,

.. code:: python

    from pycarta.auth import CartaProfileUI

    CartaProfileUI()  # A GUI for viewing, adding, or modifying profiles.


Automatic Authentication
^^^^^^^^^^^^^^^^^^^^^^^^

Any action that requires login will attempt to login using information from the
environment. To enable automatic login, set the following environment variables::

    CARTA_USER=<Carta username>
    
    CARTA_PASS=<Carta password>

    CARTA_PROFILE=<Carta profile>

    CARTA_ENV=<Carta environment>  # optional

    CARTA_HOST=<Carta host URL>  # optional

If ``CARTA_PROFILE`` is set, then ``CARTA_USER`` and ``CARTA_PASS`` are
unnecessary.

The environment (``CARTA_ENV``) and host (``CARTA_HOST``) variables need only
be set if both of the following are true: you are using username/password
authentication and you are **not** using the production Carta environment.
(This will generally not be the case, so unless you know that you need them,
you can probably leave these unset.)


Require Authorization
^^^^^^^^^^^^^^^^^^^^^

If you want to ensure that only a select group of people can access a function
you can decorate your function with ``@pycarta.authorize(...)``. This
decorator will check if the authenticated user is part of the list of users or
a member of at least one of the listed groups before the decorated function
will run. For example,

.. code:: python

    import pycarta

    @pycarta.authorize()
    def requires_carta_account():
        print("This will only run if the user is authorized.")

    @pycarta.authorize(users=["Andy", "Beth", "Charlie"])
    def specific_users():
        print("This will only run for Andy, Beth, or Charlie.")

    @pycarta.authorize(groups=["MyOrg:All"])
    def users_in_group():
        print("This will only run for users who are members of 'MyOrg:All'.")


.. _administrative_tasks:

Administrative Tasks
--------------------

The reason to authenticate is to verify identify, and the reason to verify
identity is to exercise some control over who has access to what resources.

Users
^^^^^

``pycarta`` provides create and retrieve operations.

.. code:: python

    from pycarta.admin.user import (
        create_user,
        get_current_user,
        get_user,
        list_users,
        reset_user_password,
    )
    from pycarta.admin.types import User

    # Get the current user
    current_user = get_current_user()

    # Reset the current user's password
    reset_user_password(current_user.username)
    
    # List all users
    user_list = list_users()

    # Create a new user
    new_user = User(
        name="test_user",
        email="test@user.com",
        lastName="Babbott",
        firstName="Alice"
    )
    create_user(new_user)  # Raises an error if user exists.

    # Retrieve a user by email. Can also search by username, first_name
    # last_name and find those that are partial matches. Multiple matches are
    # returned as a list
    alice = get_user(email="alice@myorg.com")

Working with users provides the ultimate fine-grained control over who can
run your function(s), but listing everyone is tedious -- and fragile. The onus
is on you, the developer, to maintain an up-to-date list of users, so it's
often easier to work with groups.

Groups
^^^^^^

``pycarta`` provides create, retrieve, and update operations for groups.
These functions allows the developer to create new groups and to add users to
that group.

.. attention::

    Group names must be unique across the Carta platform. To reduce the risk of
    name conflicts, it is generally good to develop a naming convention that
    narrows the namespace, e.g. "MyCompany:MyGroup". Now your group name must
    only be unique within your company.

    The ``pycarta`` groups API makes this an easy convention to follow. See
    below for an example.

.. code:: python

    from pycarta.admin.types import Group
    from pycarta.admin.user import get_current_user
    from pycarta.admin.group import (
        add_user_to_group,
        create_group,
        list_members as list_group_members,
    )

    user = get_current_user()

    # Create a new group. Raises an exception if the group exists
    group = Group(name="MyGroup", organization="MyCompany")
    create_group(self.group)

    # Add the current user to this group
    add_user_to_group(user, group)

    # List the members of the group
    members = list_group_members(group)


Secrets
^^^^^^^

In addition to management, it can also be helpful to store sensitive
information, such as database usernames and passwords, so they are readily
accessible anywhere you run your code.

``pycarta`` provides secrets management to help store small content like this.

.. note::

    ``pycarta`` secrets cannot be shared between users, so your secret name
    need only be unique to you. This also allows you, the developer, to specify
    a secret name and oblige your users to store their own credentials to
    respect whether they have been given access to a particular resource, such
    as a database.

.. code:: python

    from pycarta.admin.secret import put_secret, get_secret

    put_secret(name="db-username", value="joe")
    put_secret(name="db-password", value="abc123def")

    username = get_secret("db-username")
    password = get_secret("db-password")

Normally, of course, you would want to prompt your user for their
password -- or other sensitive information -- using ``getpass`` or similar.

.. important::

    You may wish to prompt your users to provide their credentials as part of
    your code's execution if those credentials are needed for the code to
    execute properly.


Seven Bridges Integration
-------------------------

Bidirectionality is foundational to any part of a data infrastructure. After
all, what use is a data store that allows for data capture but doesn't allow
for data retrieval? Analogously, what use is a compute resource that doesn't
allow results to be retrieved?

Velsera's Seven Bridges platform (SBG) has adopted an API-centric approach to
low-code/no-code development. On SBG, users can deploy Apps -- callable command
line tools that serves as the basis for workflow development; and Workflows,
which connect the output from one App (or another Workflow) as the input into
others.

However, both Apps and Workflows share more in common than their ability to
connect to each other. They both represent a calculation whose value has
already been established. SBG's *Data Studio* provides a jupyter environment
for developing and early stage prototyping. These codes are then typically
refined into a CLI (using a local IDE) and deployed as an App.

But what about those workflows that cannot easily be moved into SBG? What if
the output of an App/Workflow is needed to shape further App development? How
can that second App be developed without calling the first App in an iterative
development cycle?

SBG has refined the process of creating new Apps and connecting those Apps to
create complex Workflows. ``pycarta.sbg`` allows users to call Seven Bridges
Apps and Workflows as python functions, even handling file upload and results
download so, apart from the execution time, Seven Bridges Apps and Workflows
can be integrated seamlessly into existing python code.

Seven Bridges Login
^^^^^^^^^^^^^^^^^^^

Connections to SBG are authenticated through an API key. ``pycarta.sbg``
extends the convenience of SBG API keys by adding a more transportable way to
access your SBG API key.

If you have set up `SBG authentication <https://sevenbridges-python.readthedocs.io/en/latest/quickstart.html#authentication-and-configuration>`_
using a sevenbridges credentials file, or if you've set the necessary
environment variables, or if you've stored your Seven Bridges API key as a
Carta secret, in a process that will be demonstrated below, then logging into
``pycarta`` will log you into SBG automatically, e.g.

.. code:: python

    import pycarta as pc

    pc.login()
    # You are now authorized to call SBG Apps and Workflows

.. TODO:: Add other ways to log into SBG.

But before you can actually use SBG Apps and Workflows, you must turn them into
python functions.

Executing Seven Bridges Apps
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Executing Apps is at the heart of the SBG platform. It is also at the heart of
the ``pycarta.sbg`` module.

While in general, you are unlikely to create a single python ``ExecutableApp``,
and you can jump to the next section if you wish, it may be helpful to
understand how these are created so you better understand the options used when
you try to create an ``ExecutableProject``.

.. code:: python

    import pycarta as pc
    from pycarta import get_agent
    from pycarta.sbg import ExecutableApp

    # Login to Carta and to Seven Bridges
    pc.login()
    # Get the Carta Agent (for handling calls to Carta)
    agent = get_agent()
    # Get the sevenbridges.Api object (to communicate with SBG)
    sbg_api = agent.sbg_manager.api
    # Retrieve a Seven Bridges App
    sbg_app = sbg_api.app.get("MyAppName", project="division/project")
    # Create an ExecutableApp
    app = ExecutableApp(
        sbg_app,
        cleanup=True,
        polling_freq=5.0,
        overwrite_local=True,
        overwrite_remote=True,
        strict=True,)
    # Now the app is ready to use.
    result = app(input="myfile.csv", num_roads=42)

When the app is run on the last line, the local file "myfile.csv" will first be
uploaded to SBG. ``sbg_app`` is an App that expects two parameters: an input
file and an integer. If we assume that ``sbg_app`` writes a file -- perhaps an
image generated from the input file -- then that image will be downloaded after
the task is complete.

The comments make most of this very self explanatory, but the ExecutableApp has
several options that control how it behaves.

- ``cleanup``: This determines whether the function will delete files that were uploaded to SBG and results files after they are downloaded.
- ``polling_freq``: How often to check if the SBG task is still running. Default: 10 seconds. Minimum: 3 seconds.
- ``overwrite_local``: Whether to overwrite local files with the results of the calculation.
- ``overwrite_remote``: Whether to overwrite remote files with files uploaded from your local system.

The last option, ``strict``, requires a more detailed explanation. Python is a
`duck-typed language <https://en.wikipedia.org/wiki/Duck_typing>`_ but
`CWL <https://www.commonwl.org/>`_, the workflow language that powers Seven
Bridges, is strongly typed. The ``strict`` keyword more strictly enforces
typing when making a call to the SBG App. This is generally a good idea, hence
the default (True), because this ensures the value passed to the function is
valid before time and effort is wasted in allocating resources and running a
task that is likely to fail.

Each ``ExecutableApp`` constructs documentation from the CWL, including
descriptions, argument names and types, and titles, allowing users to
interrogate newly created apps and learn how to use them.


ExecutableProject
^^^^^^^^^^^^^^^^^

SBG divisions are divided into projects and, in some ways, are the basic unit
of the SBG platform. Projects are collections of Apps, Workflows, Tasks, and
Files that can be shared with others. If you've been granted access to a
project, you're first step is likely to explore what applications are
available.

Fortunately, this is easily done using an ``ExecutableProject``.

.. code:: python

    import pycarta as pc
    from pycarta.sbg import ExecutableProject

    pc.login()
    sandbox = ExecutableProject(project="division/sandbox")
    result = sandbox.hello_world()

``sandbox`` is a unique class that contains all the applications associated
with the "division/sandbox" project. Apps are documented so you can interrogate
each to learn what it does and its call signature.
