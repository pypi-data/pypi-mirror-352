import pandas as pd
import tqdm

from .token import Token
from .util import get


class Org:
    """
    A GitHub organization with methods to interact with it.

    Parameters
    ----------
    name : str
        The name of the GitHub organization.

    """

    def __init__(self, name):
        self.name = name
        self.api_url = f"https://api.github.com/orgs/{self.name}"

    def __repr__(self):
        """Return a string representation of the organization."""
        return f"Org(name='{self.name}')"

    def exists(self):
        """
        Check if the GitHub organization exists.

        Returns
        -------
        bool
            True if the organization exists, False otherwise.

        """
        url = self.api_url
        try:
            get(url, headers=Token.headers(), params=None)
            return True
        except ValueError:
            return False

    @property
    def n_private_repos(self):
        """
        Get the number of private repositories in the organization.

        Returns
        -------
        int
            Number of private repositories.

        """
        url = f"{self.api_url}"
        return get(url, headers=Token.headers()).get("total_private_repos", 0)

    @property
    def n_public_repos(self):
        """
        Get the number of public repositories in the organization.

        Returns
        -------
        int
            Number of public repositories.

        """
        url = f"{self.api_url}"
        return get(url, headers=Token.headers()).get("public_repos", 0)

    @property
    def n_repos(self):
        """
        Get the total number of repositories in the organization.

        Returns
        -------
        int
            Total number of repositories (private + public).

        """
        return self.n_private_repos + self.n_public_repos

    def repos(self):
        """
        Fetch all repositories in the organization and return as pd.DataFrame.

        All dates are converted to UTC and then localized to None.

        Returns
        -------
        pandas.DataFrame
            A DataFrame where each row is a repository and columns are repo metadata.

        """
        url = f"{self.api_url}/repos"
        params = {"per_page": 100, "page": 1}

        data = pd.DataFrame()
        params = {"per_page": 100, "page": 1}

        fetched_repos = 0
        with tqdm.tqdm(total=self.n_repos, desc="Fetching repos") as pbar:
            while True:
                if not (page := get(url, headers=Token.headers(), params=params)):
                    break

                page_data = (
                    pd.DataFrame(page)
                    .loc[
                        :,
                        [
                            "id",
                            "name",
                            "full_name",
                            "description",
                            "private",
                            "is_template",
                            "url",
                            "html_url",
                            "clone_url",
                            "fork",
                            "created_at",
                            "updated_at",
                            "pushed_at",
                            "default_branch",
                            "size",
                            "archived",
                        ],
                    ]
                    .set_index("id", verify_integrity=True)
                    .assign(
                        created_at=lambda df_: pd.to_datetime(
                            df_.created_at
                        ).dt.tz_localize(None),
                        updated_at=lambda df_: pd.to_datetime(
                            df_.updated_at
                        ).dt.tz_localize(None),
                        pushed_at=lambda df_: pd.to_datetime(
                            df_.pushed_at
                        ).dt.tz_localize(None),
                    )
                )

                data = pd.concat([data, page_data], axis=0)

                fetched_repos += len(page_data)
                pbar.update(len(page_data))

                params["page"] += 1

        return data
