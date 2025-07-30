import botocore
import pytest
from pycarta.auth import CartaAgent, CartaConfig
from pycarta.auth import CartaLoginUI, CartaProfileUI
from pycarta.auth.agent import CognitoAgent
from pycarta.exceptions import AuthenticationError
from subprocess import run
from multiprocessing import Process
from random import randint
from time import sleep
from warnings import warn


@pytest.fixture(scope="module")
def server():
    # Spin up a little Flask web server.
    # Use Multiprocessing to run this in a separate process.
    # Use subprocess to execute.
    port = str(randint(1024, 65535))
    server = Process(target=run, args=(
        ["fastapi", "dev", "server_auth.py", "--port", port],))
    server.start()
    sleep(10) # Give the server time to start
    yield port
    server.terminate()
    server.join()


@pytest.mark.skip(reason="Mock not set up.")
def test_CognitoAuthenticationAgent(server, caplog):
    caplog.set_level("DEBUG")
    agent = CognitoAgent(token="test_token", host=f"http://localhost:{server}")
    with pytest.raises(botocore.exceptions.InvalidRegionError) as e_top:
        with pytest.raises(AuthenticationError) as e_info:
            # This should because the nothing about the server is valid. :)
            agent.authenticate(username="dummy", password="password")
    # Set the token -- simulating authentication.
    agent.token = "test_token"
    agent.host = f"http://localhost:{server}"
    # Test that the agent has been set up properly
    assert agent.token == "test_token", "'agent' has the wrong token."
    assert agent.host == f"http://localhost:{server}", "'agent' has the wrong host."
    assert agent.is_authenticated(), "'agent' is not authenticated."

    r = agent.request("get", "auth")
    assert r.ok, f"GET request failed ({r.status_code}): {r.reason}"
    assert "userPoolId" in r.json()
    assert "userPoolWebClientId" in r.json()
    assert "region" in r.json()

    r = agent.get("auth")
    assert r.ok, f"GET request failed ({r.status_code}): {r.reason}"
    assert "userPoolId" in r.json()
    assert "userPoolWebClientId" in r.json()
    assert "region" in r.json()

    r = agent.post("auth", json={"data": "test"})
    assert r.ok, f"POST request failed ({r.status_code}): {r.reason}"
    assert r.text.strip("'\"") == "auth POST: test"

    r = agent.put("auth", json={"data": "test"})
    assert r.ok, f"PUT request failed ({r.status_code}): {r.reason}"
    assert r.text.strip("'\"") == "auth PUT: test"

    r = agent.head("auth")
    # Has no body, so we just check the status code
    assert r.ok, f"HEAD request failed ({r.status_code}): {r.reason}"

    r = agent.patch("auth", json={"data": "test"})
    assert r.ok, f"PATCH request failed ({r.status_code}): {r.reason}"
    assert r.text.strip("'\"") == "auth PATCH: test"

    r = agent.delete("auth")
    assert r.ok, f"DELETE request failed ({r.status_code}): {r.reason}"
    assert r.text.strip("'\"") == "auth DELETE"

    r = agent.delete("auth", json={"data": "test"})
    assert r.ok, f"DELETE request failed ({r.status_code}): {r.reason}"
    assert r.text.strip("'\"") == "auth DELETE: test"


def test_CartaAuthenticationAgent(server, caplog, carta_profile):
    caplog.set_level("DEBUG")
    profile = carta_profile
    # Check defaults
    agent = CartaAgent()
    assert agent.url is CartaAgent.HOST_DEV
    agent = CartaAgent(environment="production")
    assert agent.url is CartaAgent.HOST_PROD
    # Login with Profile
    agent = CartaAgent(profile=profile)
    assert agent.username
    assert agent.token
    assert agent.host == CartaAgent.HOST_DEV
    # Verify that the agent is reauthenticated when the token becomes invalid.
    if agent.token:
        agent.token = "ABC" + agent.token[:-3]  # Invalidate the token
    agent.get("user/authenticated")
    # Delete the token
    agent.token = None
    agent.get("user/authenticated")


def test_ui():
    # Make sure the password dialog works
    try:
        agent = CartaLoginUI.login(
            host=CartaAgent.HOST_DEV,
            title="Enter Invalid Carta Credentials")
        assert True
    except:
        warn("Carta authentication failed. If you did not enter a valid "
             "username and password, then this is expected and this warning "
             "may be ignored. To get rid of this error, enter a valid "
             "username and password for the Carta Sandbox account.")
        pass
    try:
        with open(CartaConfig.carta_profiles_path, "r") as ifs:
            old_config = ifs.read()
    except FileNotFoundError:
        old_config = None
    try:
        CartaProfileUI()
    except:
        assert False, "CartaProfileUI failed."
    finally:
        if old_config is not None:
            with open(CartaConfig.carta_profiles_path, "w") as ofs:
                ofs.write(old_config)
