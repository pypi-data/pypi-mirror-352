from pydantic import BaseModel, Field
from typing import Optional


class Profile(BaseModel):
    username: Optional[str] = None
    environment: Optional[str] = Field(default=None)
    password: Optional[str] = None
    token: Optional[str] = None
    aws_profile: Optional[str] = None

    profile_name: str = Field(exclude=True, default=None)

    def is_production(self):
        return self.environment and self.environment.lower() == "production"

    def invalidate_token(self) -> bool:
        """
        Deletes token data. Returns true if username and password are available
        for revalidation.

        :return:
            True if the user can be revalidated with username and password,
            False otherwise.
        :rtype: bool
        """
        # TODO: Confirm the following change does not break the intended
        # functionality. The double negative doesn't make sense and the
        # presence or absence of a token is immaterial if the intent is
        # to end up with an invalidated token.
        # can_revalidate = not not (self.token and self.username and self.password)
        # return can_revalidate
        can_validate = self.username and self.password
        self.set_token(None)
        return can_validate

    def set_token(self, token):
        self.token = token
        if self.profile_name:
            # import here to avoid circular import.
            from .config import CartaConfig
            CartaConfig().save_profile(self.profile_name, self)
