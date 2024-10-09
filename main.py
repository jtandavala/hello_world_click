import sqlite3
import click
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def connect_db():
    db_path =  os.path.join(BASE_DIR, 'data/cli_db.sqlite')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = connect_db()
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


@click.group()
def cli():
    """A CLI to interact with an SQLITE database."""
    pass

@cli.command()
@click.option('--name', '-n', prompt="Name", help="The name of the user.")
@click.option('--age', '-a', prompt="The age of the user")
def add_user(name, age):
    conn = connect_db()
    c = conn.cursor()
    c.execute('INSERT INTO users (name, age) VALUES (?, ?)', (name, age))
    conn.commit()
    conn.close()
    click.echo(f"User {name} created.")


@cli.command()
@click.option('--id','-i', help='The id is required')
@click.pass_context
def find_by_id(ctx, id):
    if not id:
        click.echo("id is required")
        ctx.abort()
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (id))
    user = c.fetchone()
    if not user:
        click.echo(f"User with ID {id} does not exist")
    click.echo(f"ID: {user['id']}, Name: {user['name']}, Age: {user['age']}")


@cli.command()
@click.option('--id', '-i', help="The Id of user")
@click.option('--name', '-n', help='The new name of user')
@click.option('--age', '-a', help='The new age of user')
@click.pass_context
def update_user(ctx, id, name, age):
    if not id:
        click.echo("Id is required")
        ctx.abort()
    conn = connect_db()
    c = conn.cursor()
    c.execute("UPDATE users set name = ?, age = ? WHERE id = ?", (name, age ,id))
    conn.commit()
    conn.close()
    click.echo(f"User with ID {id} was updated.")


@cli.command()
@click.option('--page', '-p', default=1, help='Page number')
@click.option('--per-page', '-pr', default=5, help='Numbers of users per page')
def list_users(page, per_page):
    conn = connect_db()
    c = conn.cursor()

    offset = (page - 1) * per_page

    c.execute('SELECT * FROM users LIMIT ? OFFSET ?', (per_page, offset))
    users = c.fetchall()
    conn.close()

    if users:
        for user in users:
            click.echo(f"ID: {user['id']}, Name: {user['name']}, Age: {user['age']}")
    else:
        click.echo(f"No users found on page {page}")

@cli.command()
@click.option('--id', '-i', help='The id of user')
@click.pass_context
def delete_user(ctx, id):
    if not id:
        click.echo("id is required")
        ctx.abort()
    conn = connect_db()
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id = ?", (id))
    conn.commit()
    conn.close()
    click.echo(f"User with ID {id} was deleted")

if __name__ == '__main__':
    init_db()
    cli()
