import aiosqlite as asql
import sqlite3 as sql


async def setup_tables(items=True):
    if items:
        SQL = (
            """
                CREATE TABLE IF NOT EXISTS items(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    price INT DEFAULT 0,
                    weight INT DEFAULT 0,
                    rarity INT DEFAULT 1,
                    use_value INT DEFAULT 0,
                    use_value2 INT DEFAULT 0
                );
            """
        )

        async with asql.connect("adventuredb.db") as db:
            await db.execute(SQL)
            await db.commit()


async def check_item_exists(name):
    async with asql.connect("adventuredb.db") as db:
        async with db.execute(
            "SELECT * FROM items WHERE name=?;", (name,)) as curs:
            result = await curs.fetchone()

    if result:
        return result
    return False


async def add_item(
    name, _id=None, price=None, weight=None, rarity=None, use1=None, use2=None
):
    SQL = "INSERT INTO items ("

    if _id:
        SQL += "id, name"
        values = [_id, name]
    else:
        SQL += "name"
        values = [name]

    if price:
        SQL += ", price"
        values.append(price)

    if weight:
        SQL += ", weight"
        values.append(weight)

    if rarity:
        SQL += ", rarity"
        values.append(rarity)

    if use1:
        SQL += ", use_value"
        values.append(use1)

        if use2:
            SQL += ", use_value2"
            values.append(use2)

    else:
        if use2:
            SQL += ", use_value"
            values.append(use2)

    SQL += f") VALUES (?{', ?'*(len(values)-1)});"

    async with asql.connect("adventuredb.db") as db:
        await db.execute(SQL, values)
        await db.commit()



