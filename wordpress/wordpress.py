from functools import reduce
import mysql.connector

from wordpress.plugin import WordpressPlugin
from wordpress.wp_object import WPObject

class Post(WPObject):
    def __init__(self, parent = None, **data):
        super().__init__(parent)
        for key, value in data.items():
            setattr(self, key, value)
            
    def update_meta(self, key, value):
        with self.conn.cursor(prepared=True) as cursor:
            where = self._parent.where(prepared=True, post_id=self.ID, meta_key=key)

            query = '''
                UPDATE wp_postmeta
                SET meta_value=?
            ''' + where[0]
            parameters = (value,) + where[1]

            cursor.execute(query, parameters)
            self.conn.commit()


class Product(Post):
    def __init__(self, parent = None, **data):
        super().__init__(parent, **data)
    
    def set_price(self, price):
        self.update_meta("_price", price)
        self.update_meta("_regular_price", price)

class DBConnection():
    def __init__(self, **connection_info):
        self.connect(**connection_info)

    def __del__(self):
        self.conn.close()

    def connect(self, **connection_info):
        try:
            self.conn: mysql.connector.MySQLConnection = mysql.connector.connect(**connection_info)
        except mysql.connector.Error as err:
            print(err)
            exit()

    def where(self, prepared = False, **args: 'dict[str]'):
        params = ()
        def reducer(acc, key):
            nonlocal params
            if(acc == ""): acc += " WHERE "
            else: acc += " AND "

            if(prepared):
                params += (args[key],)
                return acc + "{}=? ".format(key)
            else: return acc + "{} = '{}' ".format(key, args[key])

        statement = reduce(
            reducer,
            args.keys(),
            ""
        )

        if prepared:
            return (statement, params)
        else:
            return statement


class Wordpress(DBConnection):
    def __init__(self, plugins: 'dict[str, WordpressPlugin]', **connection_info):
        super().__init__(**connection_info)

        for name, plugin in plugins.items():
            plugin._parent = self
        self.plugins = plugins

    def get_posts(self, type, **kwargs):
        with self.conn.cursor(dictionary=True) as cursor:
            query = "SELECT * FROM wp_posts" + self.where(**kwargs)
            cursor.execute(query)
            return [type(parent=self, **data) for data in cursor.fetchall()]