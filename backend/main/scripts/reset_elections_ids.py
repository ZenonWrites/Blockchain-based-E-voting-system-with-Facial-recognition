from django.db import connection

def reset_election_auto_increment():
    with connection.cursor() as cursor:
        # Reset auto-increment for SQLite
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='main_election';")
        print("Auto-increment counter for 'Election' table has been reset.")

reset_election_auto_increment()