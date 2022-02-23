from multiprocessing.connection import Connection
from typing import TYPE_CHECKING

import mysql.connector
if TYPE_CHECKING:
    from .wordpress import Wordpress


class WPObject():
    def __init__(self, parent: 'Wordpress' = None):
        self._parent = parent

    @property
    def conn(self) -> mysql.connector.MySQLConnection:
        return self._parent.conn