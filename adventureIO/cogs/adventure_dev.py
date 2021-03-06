from discord.ext.commands import Cog, group

import adventureIO.database as database


class AdventureDevelopmentCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    @group(name="dev")
    async def developer_group(self, ctx):
        ...

    @developer_group.group(name="add")
    async def developer_add_group(self, ctx):
        ...

    @developer_group.group(name="remove", aliases=["delete"])
    async def developer_remove_group(self, ctx):
        ...

    @developer_add_group.command(name="item")
    async def add_item_to_database(self, ctx, *, name):
        item = await database.check_item_exists(name)
        if item:
            return await ctx.send(f"This item already exists: {item}")

        await ctx.send(
            "Please provide Price, weight, rarity, use1 and use2"
            " separated by a space in that order, use '0' for defaults"
            )

        def check(msg):
            parts = msg.content.split(" ")
            if len(parts) != 5:
                return False

            if not all(part.isdigit() for part in parts):
                return False

            parts = [int(part) for part in parts]
            if (
                0 > parts[0] > 1_000_000_000
                or 0 > parts[1] > 1_000_000_000
                or not (0 < parts[2] < 4)
            ):
                return False
            return True

        msg = await self.bot.wait_for("message", check=check)

        add_item_keys = [
            ("price"),
            ("weight"),
            ("rarity"),
            ("use1"),
            ("use2"),
        ]
        kwargs = {"name": name.title()}

        for key, value in zip(add_item_keys, msg.content.split(" ")):
            value = value.replace("`", r"\`")

            if value.lower() == "0":
                kwargs[key] = None
            else:
                kwargs[key] = value

        print(kwargs)
        await database.add_item(**kwargs)
        await ctx.send("Done")

    @developer_remove_group.command(name="item")
    async def remove_item_command(self, ctx, *, item):
        try:
            item = int(item)
            _int = True
        except ValueError:
            _int = False

        if _int:
            await database.delete_by_id(item, 'items')
        else:
            await database.delete_by_name(item, 'items')

        await ctx.send("Done")

    @developer_remove_group.command(name="items")
    async def remove_many_items_command(self, ctx, *items):
        all_int = all(item.isdigit() for item in items)
        any_int = any(item.isdigit() for item in items)

        if not all_int and any_int:
            return await ctx.send("You can't mass delete by id and name")

        if all_int:
            int_items = [int(item) for item in items]
            await database.delete_many_by_id(int_items, "items")

        else:
            await database.delete_many_by_name(items, "items")

        await ctx.send("Done")

    @developer_group.command(name="get")
    async def developer_get_group(self, ctx):
        rarity_map = {
            "1": ("|", "|"),
            "2": (r'"', r'"'),
            "3": ("^", "::"),
            "4": ("%", "%")
        }

        rarity_to_str = {
            "1": "Common",
            "2": "Uncommon",
            "3": "Rare",
            "4": "Legendary"
        }

        all_items = [
            (
                f"|{'Id':^4}|{'Name':^26}|{'Price':^7}|"
                f"{'Weight':^8}|{'Rarirty':^11}|"
            ),
            (
                f"+{'-'*4}+{'-'*26}+{'-'*7}+{'-'*8}+"
                f"{'-'*11}+"
            )
        ]
        async for item in database.AllItems():
            _id, name, price, weight, rarity, use1, use2, shop = item
            _id = str(_id)
            price = str(price)
            weight = str(weight)
            rarity = str(rarity)

            prefix = rarity_map.get(rarity, ("|", "|"))[0]
            suffix = rarity_map.get(rarity, ("|", "|"))[1]
            rarity = rarity_to_str.get(rarity, "Common")
            _str = (
                f"{prefix}"
                f"{_id[:4]:^4}|{name[:26]:^26}|{price[:7]:^7}|"
                f"{weight[:8]:^8}|{rarity[:9]:^11}"
                f"{suffix}"
            )
            all_items.append(_str)

        msg = "```autohotkey\n{}```".format("\n".join(all_items))
        await ctx.send(msg)


def setup(bot):
    bot.add_cog(AdventureDevelopmentCog(bot))
