import pytest
from pycarta.auth import CartaConfig
from pycarta.auth import Profile
from pycarta.exceptions import ProfileNotFoundException


class TestCartaConfig:
    def test_init(self):
        """Test that the CartaConfig class can be initialized."""
        CartaConfig()

    def test_get_profiles(self):
        """Test that the get_profiles method returns a list of profiles."""
        config = CartaConfig()
        profiles = config.get_profiles()
        assert isinstance(profiles, list)

    def test_save_profile(self):
        """Test that the save_profile method saves a profile."""
        profile = Profile(
            username="test_user",
            environment="development",
            password="test_password",
            profile_name="test_profile")
        CartaConfig().save_profile("test_profile", profile)

    def test_get_profile(self):
        """Test that the get_profile method returns a profile."""
        config = CartaConfig()
        profile = config.get_profile("test_profile")
        assert isinstance(profile, Profile)

    def test_delete_profile(self):
        """Test that the delete_profile method deletes a profile."""
        CartaConfig().delete_profile("test_profile")
        with pytest.raises(ProfileNotFoundException):
            CartaConfig().get_profile("test_profile")
