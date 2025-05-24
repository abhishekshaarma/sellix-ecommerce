class Page:
    @staticmethod
    def get_seller_pages(seller_id):
        """
        Retrieve all pages for a seller
        """
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM pages
                    WHERE seller_id = %s
                    ORDER BY created_at DESC
                """, (seller_id,))
                return cursor.fetchall()
        finally:
            connection.close()
    
    @staticmethod
    def get_by_id(page_id):
        """
        Retrieve a page by its ID
        """
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM pages WHERE id = %s", (page_id,))
                return cursor.fetchone()
        finally:
            connection.close()
    
    @staticmethod
    def get_by_slug(seller_id, slug):
        """
        Retrieve a page by seller ID and slug
        """
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM pages
                    WHERE seller_id = %s AND slug = %s
                """, (seller_id, slug))
                return cursor.fetchone()
        finally:
            connection.close()
    
    @staticmethod
    def get_by_slug_any_seller(slug):
        """
        Retrieve a published page by slug from any seller
        """
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM pages
                    WHERE slug = %s AND is_active = 1
                    LIMIT 1
                """, (slug,))
                return cursor.fetchone()
        finally:
            connection.close()
    
    @staticmethod
    def create(seller_id, title, content, slug, is_active=True):
        """
        Create a new page
        """
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO pages (seller_id, title, content, slug, is_active)
                    VALUES (%s, %s, %s, %s, %s)
                """, (seller_id, title, content, slug, is_active))
                connection.commit()
                return cursor.lastrowid
        except Exception as e:
            connection.rollback()
            print(f"Error creating page: {e}")
            return None
        finally:
            connection.close()
    
    @staticmethod
    def update(page_id, data):
        """
        Update a page
        """
        connection = get_db_connection()
        try:
            # Build the SET part of the query
            set_clause = ", ".join([f"{key} = %s" for key in data.keys()])
            values = list(data.values())
            values.append(page_id)
            
            with connection.cursor() as cursor:
                cursor.execute(f"""
                    UPDATE pages
                    SET {set_clause}
                    WHERE id = %s
                """, values)
                connection.commit()
                return True
        except Exception as e:
            connection.rollback()
            print(f"Error updating page: {e}")
            return False
        finally:
            connection.close()
    
    @staticmethod
    def delete(page_id):
        """
        Delete a page
        """
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM pages WHERE id = %s", (page_id,))
                connection.commit()
                return True
        except Exception as e:
            connection.rollback()
            print(f"Error deleting page: {e}")
            return False
        finally:
            connection.close()
