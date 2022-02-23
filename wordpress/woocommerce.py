from wordpress.plugin import WordpressPlugin
from phpserialize import unserialize

class WooCommerce(WordpressPlugin):
    def get_product_attributes(self, product, taxonomy = None):
        def get_attributes_meta():
            cursor = self.conn.cursor(dictionary=True)
            query = '''
            SELECT * FROM 
                wp_posts JOIN wp_postmeta ON post_id=ID 
                WHERE ID='{}' AND meta_key='{}'
            '''.format(product.ID, "_product_attributes")

            cursor.execute(query)
            attributes_raw = cursor.fetchall()[0]["meta_value"]
            def decode(obj):
                if not isinstance(obj, dict):
                    return obj.decode() if isinstance(obj, bytes) else obj
                return {
                    key.decode(): decode(val)
                    for key, val in obj.items()
                }
            return decode(unserialize(bytes(attributes_raw, 'utf-8')))

        cursor = self.conn.cursor(dictionary=True)
        query = '''
            SELECT
                taxonomy, name
            FROM wp_posts, wp_term_relationships, wp_term_taxonomy, wp_terms
            WHERE
                ID = object_id
                AND wp_term_relationships.term_taxonomy_id = wp_term_taxonomy.term_taxonomy_id
                AND wp_term_taxonomy.term_id = wp_terms.term_id
                AND ID={product_id}
                {taxonomy_match}
        '''.format(
            product_id=product.ID,
            taxonomy_match = "AND taxonomy='{}'" % taxonomy if taxonomy else ""
        )

        cursor.execute(query)
        attributes = cursor.fetchall()
        cursor.close()
        return attributes