"""
    Dummy conftest.py for pycarta.

    If you don't know what this is for, just leave it empty.
    Read more about conftest.py under:
    - https://docs.pytest.org/en/stable/fixture.html
    - https://docs.pytest.org/en/stable/writing_plugins.html
"""

import pytest

def pytest_addoption(parser):
    parser.addoption(
        "--sbgApiEndpoint", action="store", default="https://api.sbgenomics.com/v2/", help="Seven Bridges API URL."
    )
    parser.addoption(
        "--sbgProfile", action="store", default="default", help="Seven Bridges profile."
    )
    parser.addoption(
        "--sbgAuthToken", action="store", default=None, help="Seven Bridges authentication token."
    )
    parser.addoption(
        "--sbgProject", action="store", default=None, help="Seven Bridges project."
    )
    parser.addoption(
        "--ca_cert", action="store", default=None, help="Path to the MQTT CA certificate file."
    )
    parser.addoption(
        "--client_cert", action="store", default=None, help="Path to the MQTT client certificate file."
    )
    parser.addoption(
        "--client_key", action="store", default=None, help="Path to the MQTT client key file."
    )

@pytest.fixture(scope="session")
def tls_credentials(request):
    """
    Provides file paths for CA cert, client cert, and private key, as passed via command-line options.
    """
    return {
        "ca_cert_path": request.config.option.ca_cert,
        "client_cert_path": request.config.option.client_cert,
        "client_key_path": request.config.option.client_key,
    }

@pytest.fixture(scope="session", autouse=True)
def carta_profile():
    """Creates a test profile."""
    import os
    from pycarta.auth import Profile, CartaConfig
    from pycarta.auth.ui import UsernamePasswordDialog
    # Prompt the user for Carta login credentials
    profile = Profile(profile_name="pycarta_pytest_profile")
    profile.username = os.environ.get("CARTA_USER", None)
    profile.password = os.environ.get("CARTA_PASS", None)
    if profile.username is None or profile.password is None:
        credentials = UsernamePasswordDialog("Carta Sandbox Credentials")
        profile.username = credentials.username
        profile.password = credentials.password
    profile.environment = "development"
    CartaConfig().save_profile(profile.profile_name, profile)
    # return the profile
    yield profile
    # Clean up the profiles file
    CartaConfig().delete_profile(profile.profile_name)


@pytest.fixture(scope="session", autouse=True)
def carta_init(carta_profile):
    import pycarta
    pycarta.login(profile=carta_profile.profile_name)


@pytest.fixture(scope="session")
def sbg_api(request):
    import os
    import sevenbridges as sbg
    # User specified their token and, optionally, the API URL on the command line
    url = request.config.option.sbgApiEndpoint
    token = request.config.option.sbgAuthToken
    profile = request.config.option.sbgProfile
    if url and token:
        return sbg.Api(url=url, token=token)
    elif profile:
        return sbg.Api(config=sbg.Config(profile=profile))
    try:
        # If user has set Seven Bridges environment variables
        url = os.environ.get("SB_API_ENDPOINT", "https://api.sbgenomics.com/v2/")
        return sbg.Api(url=url, token=os.environ["SB_AUTH_TOKEN"])
    except KeyError:
        pass
    try:
        # If user has set up a Seven Bridges profile
        return sbg.Api()
    except sbg.SbgError:
        pass
    # If all else failse, skip this test
    pytest.skip(
        "No Seven Bridges credentials found. " \
        "CLI: --sbgApiEndpoint, --sbgAuthToken; " \
        "Environment: SB_API_ENDPOINT, SB_AUTH_TOKEN; " \
        "Seven Bridges profile (https://docs.sevenbridges.com/docs/store-credentials-to-access-seven-bridges-client-applications-and-libraries)")
    
@pytest.fixture(scope="session")
def sbg_project(request):
    import os
    # User specified the project on the command line
    project = request.config.option.sbgProject
    if project:
        return project
    try:
        # User set the project as an environment variable
        return os.environ["SB_PROJECT"]
    except KeyError:
        pass
    pytest.skip(
        "No Seven Bridges project specified. " \
        "CLI: --sbgProject; " \
        "Environment: SB_PROJECT")
    
@pytest.fixture(scope="session")
def sbg_app(sbg_api, sbg_project):
    import sevenbridges as sbg
    try:
        project = sbg_api.projects.query(name=sbg_project)[0]
        return [app for app in sbg_api.apps.query(project=project) if app.name == "cat"][0]
    except IndexError:
        pytest.skip("No Seven Bridges app named 'cat' found in project {}".format(sbg_project))
