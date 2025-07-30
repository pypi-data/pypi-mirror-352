import pytest
import pycarta


@pytest.fixture(scope='module')
def setup():
    print('setup')
    yield
    print('teardown')


def test_get_agent():
    agent = pycarta.get_agent()
    assert isinstance(agent, pycarta.auth.CartaAgent)


class TestAuthorize:
    def setup_method(self):
        from pycarta.admin import get_current_user
        self.user = get_current_user()

    def test_no_args(self):
        @pycarta.authorize()
        def test():
            assert True
        test()

    def test_user(self):
        @pycarta.authorize(users=[self.user])
        def test():
            assert True
        test()

    def test_group(self):
        @pycarta.authorize(groups=['Test:Pytest'])
        def test():
            assert True
        test()

    def test_user_from_str(self):
        @pycarta.authorize(users=[self.user.name])
        def test():
            assert True
        test()

    def test_disallowed_user(self):
        @pycarta.authorize(users=['nobody'])
        def test():
            assert False
        with pytest.raises(pycarta.AuthenticationError):
            test()

    def test_disallowed_group(self):
        @pycarta.authorize(groups=['no_such_group'])
        def test():
            assert False
        with pytest.raises(pycarta.AuthenticationError):
            test()


def test_is_authenticated():
    assert pycarta.is_authenticated()


def test_interactive():
    if pycarta.is_interactive():
        pycarta.ioff()
        assert not pycarta.is_interactive()
        pycarta.ion()
        assert pycarta.is_interactive()
    else:
        pycarta.ion()
        assert pycarta.is_interactive()
        pycarta.ioff()
        assert not pycarta.is_interactive()
