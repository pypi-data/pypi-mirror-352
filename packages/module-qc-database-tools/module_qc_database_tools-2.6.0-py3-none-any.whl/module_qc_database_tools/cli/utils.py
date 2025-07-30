from __future__ import annotations

import itkdb
import typer
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from requests.adapters import HTTPAdapter
from rich import print as rich_print
from urllib3.util.retry import Retry


def mount_retry_adapter(
    client: itkdb.Client, total: int = 5, backoff_factor: float = 1.0
) -> itkdb.Client:
    """
    Mounts the Retry adapter with maximum number of retries and a backoff factor.
    """
    adapter = HTTPAdapter(
        pool_connections=10,
        pool_maxsize=10,
        max_retries=Retry(
            total=total,
            backoff_factor=backoff_factor,
            status_forcelist=[500, 502, 503, 504],
        ),
    )
    client.mount("http://", adapter)
    client.mount("https://", adapter)
    return client


def get_itkdb_client(
    *, access_code1: str | None = None, access_code2: str | None = None
) -> itkdb.Client:
    """
    Create an itkdb client using access codes (if provided).

    Args:
        access_code1 (:obj:`str` or :obj:`None`): access code 1
        access_code2 (:obj:`str` or :obj:`None`): access code 2

    Returns:
        client (:obj:`itkdb.Client`): an itkdb client
    """
    if access_code1 and access_code2:
        user = itkdb.core.User(access_code1=access_code1, access_code2=access_code2)
        return mount_retry_adapter(itkdb.Client(user=user))
    return mount_retry_adapter(itkdb.Client())


def get_dbs_or_client(
    *,
    localdb: bool = False,
    mongo_uri: str = "mongodb://localhost:27017/localdb",
    itkdb_access_code1: str | None = None,
    itkdb_access_code2: str | None = None,
    localdb_name: str = "localdb",
    userdb_name: str | None = None,
    mongo_serverSelectionTimeout=5,
):
    """
    Create either an itkdb client or a localdb/userdb database pair.

    Args:
        localdb (:obj:`bool`): whether to use localdb or not
        access_code1 (:obj:`str` or :obj:`None`): access code 1
        access_code2 (:obj:`str` or :obj:`None`): access code 2
        localdb_name (:obj:`str`): name of the localDB database
        userdb_name (:obj:`str` or :obj:`None`): name of the userDB database if needed
        mongo_serverSelectionTimeout (:obj:`int`): how long in seconds before timing out
    Returns:
        client (:obj:`itkdb.Client` or :obj:`pymongo.database.Database`): an itkdb client or localdb database
        userdb (:obj:`pymongo.database.Database` or :obj:`None`): a userdb if userdb_name specified and using localdb
    """

    client = None
    userdb = None

    if localdb:
        kwargs = {"serverSelectionTimeoutMS": mongo_serverSelectionTimeout * 1000}

        mongo_client = MongoClient(mongo_uri, **kwargs)
        try:
            db_names = mongo_client.list_database_names()
        except ConnectionFailure as exc:
            rich_print("[red]Unable to connect to mongoDB[/]")
            raise typer.Exit(1) from exc

        if localdb_name not in db_names:
            rich_print(
                f"[red][underline]{localdb_name}[/underline] not in [underline]{db_names}[/underline][/red]."
            )
            raise typer.Exit(1)

        client = mongo_client[localdb_name]
        if userdb_name:
            if userdb_name not in db_names:
                rich_print(
                    f"[red][underline]{userdb_name}[/underline] not in [underline]{db_names}[/underline][/red]."
                )
                raise typer.Exit(1)
            userdb = mongo_client[userdb_name]
    else:
        client = get_itkdb_client(
            access_code1=itkdb_access_code1, access_code2=itkdb_access_code2
        )

    return client, userdb
