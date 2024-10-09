import os
import click
import sqlite3
from pydantic import BaseModel, ValidationError, conint, constr

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, 'data/cli_class_base.sqlite')

@click.group()
def cli():
    """A CLI to interact with an SQLITE database."""
    pass

class UserModel(BaseModel):
    name: constr(min_length=2, max_length=50)
    age: conint(ge=0)

class Database:
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    age INTEGER NOT NULL
                )
            ''')
        conn.commit()
        conn.close()

class UserCrud(Database):
    def create_user(self, name: str, age: int):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("INSERT INTO users (name, age) VALUES (?, ?)", (name, age))
        conn.commit()
        conn.close()
        return f"User {name} created."

    def list_users(self, page: int, per_page: int):
        offset = (page - 1) * per_page
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM users LIMIT ? OFFSET ?", (per_page, offset))
        users = c.fetchall()

        if users:
            return users
        return []

    def find_one(self, id: int):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE id = ?", (id,))
        return c.fetchone()

    def update(self, id: int, name: str, age: int):
        if self.find_one(id) is None:
            return False
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("UPDATE users set name = ?, age = ? WHERE id = ?", (name, age, id))
        conn.commit()
        conn.close()
        return True

    def delete(self, id: int):
        conn = self.get_connection()
        c = conn.cursor()
        if self.find_one(id) is None:
            return False
        c.execute("DELETE FROM users WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        return True


class UserCLI:
    def __init__(self):
        self.crud = UserCrud(DB_NAME)

    def create_user(self, name: str, age: int):
        try:
            user = UserModel(name=name, age=age)
            result = self.crud.create_user(user.name, user.age)
            click.echo(result)
        except ValidationError as e:
            error_messages = [error['msg'] for error in e.errors()]
            click.echo(f"Input validation failed: {', '.join(error_messages)}")

    def list_users(self, page: int, per_page: int):
        users = self.crud.list_users(page, per_page)
        if users:
            click.echo(f"Users (Page {page}, Per Page: {per_page}):")
            for user in users:
                click.echo(f"ID: {user['id']}, Name: {user['name']}, Age: {user['age']}")
        else:
            click.echo("No users found.")

    def find_by_id(self, id: int):
        user = self.crud.find_one(id)
        if user:
            click.echo(f"User found:")
            click.echo(f"ID: {user['id']}, Name: {user['name']}, Age: {user['age']}")
        else:
            click.echo("User not found.")

    def delete_user(self, id: int):
        if self.crud.delete(id):
            click.echo(f"User with ID {id} deleted successfully.")
        else:
            click.echo(f"User with ID {id} not found.")

    def update_user(self, id: int, name: str = None, age: int = None):
        if self.crud.update(id, name, age):
            click.echo(f"User with ID {id} updated successfully.")
        else:
            click.echo(f"User with ID {id} not found.")

# Create an instance of UserCLI
user_cli = UserCLI()

# Define Click commands
@cli.command()
@click.option('--name','-n', prompt='Name', help='The name of the user')
@click.option('--age', '-a', prompt='Age', help='The age of the user')
def create_user(name: str, age: int):
    user_cli.create_user(name, age)

@cli.command()
@click.option('--page', '-p', type=int, default=1, help='Page number')
@click.option('--per-page', '-pp', type=int, default=10, help='Number of users per page')
def list_users(page: int, per_page: int):
    user_cli.list_users(page, per_page)

@cli.command()
@click.option('--id', '-i', type=int, prompt='ID', help='The ID of the user to find')
def find_by_id(id: int):
    user_cli.find_by_id(id)

@cli.command()
@click.option('--id', '-i', type=int, prompt='ID', help='The ID of the user to delete')
def delete_user(id: int):
    user_cli.delete_user(id)

@cli.command()
@click.option('--id', '-i', type=int, prompt='ID', help='The ID of the user to update')
@click.option('--name','-n', help='New name of the user')
@click.option('--age', '-a', type=int, help='New age of the user')
def update_user(id: int, name: str = None, age: int = None):
    user_cli.update_user(id, name, age)

if __name__ == '__main__':
    cli()
