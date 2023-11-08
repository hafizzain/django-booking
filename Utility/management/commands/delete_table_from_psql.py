from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):
        print('running')
        import psycopg2

        # PostgreSQL connection parameters
        db_params = {
            "host": "localhost",
            "port": "5432",
            "database": "nstyle",
            "user": "postgres",
            "password": "1234",
        }

        # Name of the table you want to delete
        table_to_delete = "Promotions_userrestricteddiscount_client"

        try:
            # Connect to the PostgreSQL database
            conn = psycopg2.connect(**db_params)
            cursor = conn.cursor()

            # Get a list of all schemas in the database
            cursor.execute("SELECT schema_name FROM information_schema.schemata;")
            schemas = [row[0] for row in cursor.fetchall()]

            # Iterate over all schemas and delete the specified table if it exists
            for schema in schemas:
                print(schema)
                # Construct the DROP TABLE statement
                drop_table_query = f'DROP TABLE IF EXISTS "{schema}"."{table_to_delete}";'
                cursor.execute(drop_table_query)
                conn.commit()
                print(f"Deleted {table_to_delete} in schema {schema}")

        except Exception as e:
            print(f"Error: {e}")

        finally:
            cursor.close()
            conn.close()
        self.stdout.write(self.style.SUCCESS(
            'Table deleted Successfully!!'
        ))
