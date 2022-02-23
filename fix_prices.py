import os
import mariadb
from wordpress import Wordpress
from dotenv import load_dotenv

from wordpress.woocommerce import WooCommerce
from wordpress.wordpress import Product

load_dotenv()

wp = Wordpress(
    user=os.getenv('USER'),
    password=os.getenv('PASSWORD'),
    host=os.getenv('HOST'),
    port=int(os.getenv('PORT')),
    database=os.getenv('DATABASE'),
    plugins={
        "woocommerce": WooCommerce()
    }
)
wc: WooCommerce = wp.plugins["woocommerce"]

products: 'list[Product]' = wp.get_posts(post_type="product", type=Product)
variations: 'list[Product]' = wp.get_posts(post_type="product_variation", type=Product)

print(variations[1].__dict__)
variations[1].set_price(123)