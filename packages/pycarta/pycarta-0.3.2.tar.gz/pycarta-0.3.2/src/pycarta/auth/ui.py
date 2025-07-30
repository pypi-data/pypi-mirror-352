from pycarta.auth import (
    CartaAgent,
    CartaConfig,
    Profile,
)
from pycarta.exceptions import (
    ProfileNotFoundException,
)
import logging
try:
    import tkinter as tk
    from tkinter import ttk
except ImportError:
    msg = "You appear to be running in a headless environment, e.g. Lambda, so " \
          "UI components can not be imported."
    raise ImportError(msg)

logger = logging.getLogger(__name__)

# region UsernamePassword
class UsernamePasswordDialog():
    """
    Generates a dialogue to prompt a user for their username and password.

    Properties
    ----------
    username : str
        The username entered by the user.
    password : str
        The password entered by the user.
    """
    def __init__(self, title: str=None, *args, **kwds):
        self._username = None
        self._password = None
        self._frames = []
        # Setup UI
        self.foreground = kwds.get("fg", kwds.get("foreground", "white"))
        self.background = kwds.get("bg", kwds.get("background", "dark gray"))
        kwargs = {k:v for k,v in kwds.items()
                  if k not in ("fg", "bg", "foreground", "background")}
        # Create the Window
        self._window = tk.Tk(*args, **kwargs)
        self._window.title(title or "Carta Login")
        # Layout frames
        self.frame_layout()
        # Stack frames
        for frame in self._frames:
            self._window.update()
            frame.pack()
        # Run the main loop
        self._window.mainloop()

    # def title(self, title: str) -> None:
    #     self._window.title(title)

    def insert_frame(self):
        self._frames.append(tk.Frame(master=self._window, bg=self.background))

    def insert_username_field(self, frame: None | tk.Frame=None):
        frame = frame or self._frames[-1]
        self._usernameEntry = tk.Entry(
            master=frame,
            width=40,
            background=self.foreground, foreground=self.background
        )
        self._usernameEntry.insert(tk.INSERT, "Enter your Carta username...")
        self._usernameEntry.bind(
            "<FocusIn>",
            lambda *args: self._usernameEntry.delete(0, tk.END))
        self._usernameEntry.pack()

    def insert_password_field(self, frame: None | tk.Frame=None):
        frame = frame or self._frames[-1]
        self._passwordEntry = tk.Entry(
            master=frame,
            width=40,
            background=self.foreground, foreground=self.background
        )
        self._passwordEntry.insert(tk.INSERT, "Enter your Carta password...")
        def onEnterHide(*args):
            self._passwordEntry.delete(0, tk.END)
            self._passwordEntry.config(show="*")
        self._passwordEntry.bind("<FocusIn>", onEnterHide)
        self._passwordEntry.pack()

    def insert_submit_button(self, frame: None | tk.Frame=None):
        frame = frame or self._frames[-1]
        self._button = tk.Button(
            master=frame,
            text="Submit",
            background=self.foreground, foreground=self.background,
            activebackground=self.background, activeforeground=self.foreground,
            command=self.onSubmitClick
        )
        self._button.pack()

    def frame_layout(self):
        self.insert_frame()
        self.insert_username_field()
        self.insert_password_field()
        self.insert_frame()
        self.insert_submit_button()
    
    def onSubmitClick(self):
        self._username = str(self._usernameEntry.get())
        self._password = str(self._passwordEntry.get())
        self._window.destroy()

    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password
# endregion


# region Carta Login
class CartaLogin(UsernamePasswordDialog):
    """
    Interactive dialogue to log into Carta. Use the CartaLogin.login(...)
    function to generate and return an AuthorizationAgent that can be used
    to access Carta-controlled resources.
    """
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

    @classmethod
    def login(
        cls,
        *args,
        environment: str | None=None,
        host: str | None=None,
        **kwds
    ) -> CartaAgent:
        """
        Presents the user with a graphical login dialogue.

        environment : str
            The Carta environment to use. Default: production.
        host : str
            The Carta host to use. Default: None
        args : tuple
            Arguments passed on to the Tkinter window.
        kwds : dict
            Foreground ("foreground" or "fg") and/or background ("background"
            or "bg") will set the window foreground and background colors. All
            other keyword arguments are passed on to the Tkinter window.

        Returns
        -------
        AuthorizationAgent
            An authorized agent for the Carta API.
        """
        dialog = cls(*args, **kwds)
        if environment is None and host is None:
            environment = "production"
        return CartaAgent(
            username=dialog.username,
            password=dialog.password,
            environment=environment,
            host=host,)
# endregion


# region CartaProfile
class CartaProfile(UsernamePasswordDialog):
    def __init__(self, title: None | str=None, *args, **kwds):
        self._cartaConfig = CartaConfig()
        self._profile: Profile = Profile()
        self._profile_name: None | str = None
        self._environment: None | str = None
        self._aws_profile: None | str = None
        self._password_placeholder: None | str = None
        super().__init__(title or "Carta Profile Editor", *args, **kwds)
    
    def frame_layout(self, *args, **kwds):
        self.insert_frame()
        self.insert_profile_name_field()
        self.insert_username_field()
        self.insert_password_field()
        self.insert_environment_field()
        self.insert_aws_profile_field()
        self.insert_frame()
        self.insert_submit_button()
        self.insert_frame()
        self.insert_status_bar()

    def onSubmitClick(self):
        self._profile_name = str(self._profileComboBox.get())
        self._username = str(self._usernameEntry.get())
        self._password = str(self._passwordEntry.get())
        self._environment = str(self._environmentComboBox.get())
        self._aws_profile = str(self._awsProfileEntry.get())
        if self._profile_name:
            # Set the profile data from these values
            self._profile.profile_name = self._profile_name
            self._profile.username = self._username
            if self._password != self._password_placeholder:
                self._profile.password = self._password
            self._profile.environment = self._environment
            self._profile.aws_profile = self._aws_profile
            # TODO: CartaConfig does not currently respect invalidated tokens.
            self._profile.invalidate_token()
            self._cartaConfig.save_profile(self._profile_name, self._profile)
            self._cartaConfig.load()
            # Update status bar
            self._statusLabel.configure(text=f"Saved profile '{self._profile_name}'")
        else:
            self._statusLabel.configure(text="Please enter a profile name")
    
    def insert_status_bar(self, frame: None | tk.Frame=None):
        # frame = frame or self._frames[-1]
        frame = frame or self._window
        self._usernameEntry.update()
        self._statusLabel = tk.Label(
            master=frame,
            width=self._usernameEntry.winfo_width(),
            text="",
            background=self.background, foreground=self.foreground,
            relief=tk.SUNKEN, anchor=tk.W,
            padx=5, pady=5,
        )
        self._statusLabel.pack(side=tk.BOTTOM, fill=tk.X)

    def insert_profile_name_field(self, frame: None | tk.Frame=None):
        frame = frame or self._frames[-1]
        profile_names = self._cartaConfig.get_profiles()
        self._profileComboBox = ttk.Combobox(
            master=frame,
            width=40,
            state="normal",
            values=profile_names,
            # postcommand=self._cartaConfig.get_profiles,
            postcommand=lambda: self._profileComboBox.configure(values=self._cartaConfig.get_profiles()),
            background=self.foreground, foreground=self.background,)
        self._profileComboBox.insert(tk.INSERT, "Select a profile or enter a new profile name...")
        self._profileComboBox.bind(
            "<<ComboboxSelected>>",
            lambda *args: self.updateProfileFields())
        self._profileComboBox.pack()

    def insert_environment_field(self, frame: None | tk.Frame=None):
        frame = frame or self._frames[-1]
        values = ["production", "development"]
        self._environmentComboBox = ttk.Combobox(
            master=frame,
            width=40,
            state="readonly",
            values=values,
            background=self.foreground, foreground=self.background,)
        self._environmentComboBox.current(0)
        self._environmentComboBox.pack()

    def insert_aws_profile_field(self, frame: None | tk.Frame=None):
        frame = frame or self._frames[-1]
        self._awsProfileEntry = tk.Entry(
            master=frame,
            width=40,
            background=self.foreground, foreground=self.background
        )
        self._awsProfileEntry.insert(tk.INSERT, "(Optional) Enter an AWS profile...")
        self._awsProfileEntry.bind(
            "<FocusIn>",
            lambda *args: self._awsProfileEntry.delete(0, tk.END))
        self._awsProfileEntry.pack()

    def updateProfileFields(self):
        try:
            self._profile = self._cartaConfig.get_profile(self._profileComboBox.get())
        except ProfileNotFoundException:
            self._profile = Profile(profile_name=self._profileComboBox.get())
        # set username
        self._usernameEntry.delete(0, tk.END)
        if self._profile.username:
            self._usernameEntry.insert(tk.INSERT, self._profile.username)
        # set password
        self._passwordEntry.delete(0, tk.END)
        if self._profile.password:
            pwd = self._profile.password
            prefix = pwd[:min(2, len(pwd)//2)]
            suffix = pwd[-1*min(2, len(pwd)//2):]
            body = "*" * max(3, len(pwd) - len(prefix) - len(suffix))
            self._password_placeholder = prefix + body + suffix
            self._passwordEntry.insert(tk.INSERT, self._password_placeholder)
        # set environment
        self._environmentComboBox.current(0 if self._profile.is_production() else 1)
        # set aws_profile
        if self._profile.aws_profile:
            self._awsProfileEntry.delete(0, tk.END)
            self._awsProfileEntry.set(self._profile.aws_profile)
            self._awsProfileEntry.insert(tk.INSERT, self._profile.aws_profile)
# endregion


if __name__ == "__main__":  # pragma: no cover
    def test_UsernamePasswordDialog():
        app = UsernamePasswordDialog()
        print("Username:", app.username)
        print("Password:", app.password)

    def test_CartaProfile():
        try:
            with open(CartaConfig.carta_profiles_path, "r") as ifs:
                old_config = ifs.read()
        except IOError:
            old_config = None
        app = CartaProfile()
        with open(CartaConfig.carta_profiles_path, "r") as ifs:
            print(ifs.read())
        if old_config:
            with open(CartaConfig.carta_profiles_path, "w") as ofs:
                ofs.write(old_config)

    
    # Run tests
    print("# ##### Testing UsernamePasswordDialog ##### #")
    # test_UsernamePasswordDialog()

    print()

    print("# ##### Testing CartaProfile ##### #")
    test_CartaProfile()
