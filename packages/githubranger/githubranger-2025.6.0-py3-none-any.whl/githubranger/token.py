import datetime

from .util import get


class Token:
    """A class to manage a global GitHub token - used in API requests."""

    _token = None

    @classmethod
    def set_token(cls, token):
        """Set the global GitHub token for the package.

        Parameters
        ----------
        token : str
            The GitHub token to set.

        """
        cls._token = token

    @classmethod
    def get_token(cls):
        """Get the global GitHub token for the package.

        Returns
        -------
        str
            The GitHub token.

        """
        return cls._token

    @classmethod
    def headers(cls):
        """Get the headers for GitHub API requests using the token.

        Returns
        -------
        dict
            Headers with the Authorization token.

        Raises
        ------
        RuntimeError
            If the token is not set.

        """
        return (
            {
                "Authorization": f"token {cls._token}",
            }
            if cls._token
            else {}
        ) | {
            "Accept": "application/vnd.github+json",
        }

    @classmethod
    def _rate(cls):
        """Check GitHub API rate limit for the token.

        Returns
        -------
        dict
            Dictionary with results.

        """
        if cls._token is None:
            raise RuntimeError("GitHub token not set. Use Token.set_token() first.")

        url = "https://api.github.com/rate_limit"
        headers = {"Authorization": f"token {cls._token}"}

        return get(url, headers=headers, timeout=10)["rate"]

    @classmethod
    def limit(cls):
        """Get the API requests limit allowed for the token.

        Returns
        -------
        int
            Maximum number of requests.

        """
        return cls._rate()["limit"]

    @classmethod
    def remaining(cls):
        """Get the remaining API requests allowed for the token.

        Returns
        -------
        int
            Remaining number of requests.

        """
        return cls._rate()["remaining"]

    @classmethod
    def reset_time(cls):
        """Get the time when the API requests limit will reset.

        For more friendly output, pass the output to print().

        Returns
        -------
        datetime.datetime
            Time when the limit will reset.

        """
        return datetime.datetime.fromtimestamp(cls._rate()["reset"])
