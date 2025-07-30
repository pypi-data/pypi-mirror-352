import logging

import requests

from .token import Token
from .util import get


class User:
    """A GitHub user with methods to check existence and repository access.

    Parameters
    ----------
    username : str
        The GitHub username of the user.
    """

    def __init__(self, username):
        self.username = username
        self.api_url = f"https://api.github.com/users/{self.username}"

    def __repr__(self):
        """Return a string representation of the user."""
        return f"User(username='{self.username}')"

    def exists(self):
        """Check if the GitHub user exists.

        Returns
        -------
        bool
            True if the user exists, False otherwise.
        """
        url = self.api_url
        try:
            get(url, headers=Token.headers())
            return True
        except ValueError:
            return False

    def can_access(self, repo):
        """Check if the user can access a specific repository.

        Parameters
        ----------
        repo : Repo
            An instance of the Repo class representing the GitHub repository.

        Returns
        -------
        bool
            True if the user can access the repository, False otherwise.
        """
        if not self.exists():
            logging.warning(f"'{self}' does not exist.")
            return False

        url = f"{repo.api_url}/collaborators/{self.username}"
        response = requests.get(url, headers=Token.headers())  # to allow 404 responses
        return response.status_code == 204
