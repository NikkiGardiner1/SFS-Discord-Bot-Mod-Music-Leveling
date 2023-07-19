import discord
import asyncio
import logging
from discord.ext import commands
from discord import app_commands
from discord_slash import SlashCommand, SlashContext, cog_ext
from discord_slash.utils.manage_commands import create_option


logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(asctime)s %(message)s')

bot = commands.Bot(command_prefix='!')
slash = SlashCommand(bot, sync_commands=True)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="with slash commands"))
    logging.info(f'Logged in as {bot.user}')

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.embed_color = 0xFF0000

    async def cog_check(self, ctx: SlashContext):
        return ctx.author.guild_permissions.manage_roles

    @cog_ext.cog_slash(name="ban", description="Ban a member from the server", options=[
        create_option(name="member", description="The member to ban", option_type=6, required=True),
        create_option(name="reason", description="The reason for the ban", option_type=3, required=False)
    ])
    async def ban(self, ctx: SlashContext, member: discord.Member, reason=None):
        await member.ban(reason=reason)
        embed = discord.Embed(title=f'{member} has been banned.', color=self.embed_color)
        await ctx.send(embed=embed)
        logging.info(f'{ctx.author} banned {member} for reason: {reason}')

    @cog_ext.cog_slash(name="unban", description="Unban a member from the server", options=[
        create_option(name="member", description="The member to unban (username#discriminator)", option_type=3, required=True)
    ])
    async def unban(self, ctx: SlashContext, member: str):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')

        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                embed = discord.Embed(title=f'{user} has been unbanned.', color=self.embed_color)
                await ctx.send(embed=embed)
                logging.info(f'{ctx.author} unbanned {user}')
                return

    @cog_ext.cog_slash(name="timeout", description="Timeout a member for a specified number of seconds", options=[
        create_option(name="member", description="The member to timeout", option_type=6, required=True),
        create_option(name="seconds", description="The number of seconds to timeout the member for", option_type=4, required=True)
    ])
    async def timeout(self, ctx: SlashContext, member: discord.Member, seconds: int):
        timeout_role = discord.utils.get(ctx.guild.roles, name="Timeout")
        if not timeout_role:
            timeout_role = await ctx.guild.create_role(name="Timeout")

        overwrite = discord.PermissionOverwrite()
        overwrite.send_messages = False
        for channel in ctx.guild.text_channels:
            await channel.set_permissions(timeout_role, overwrite=overwrite)

        await member.add_roles(timeout_role)
        embed = discord.Embed(title=f'{member} has been timed out for {seconds} seconds.', color=self.embed_color)
        await ctx.send(embed=embed)
        logging.info(f'{ctx.author} timed out {member} for {seconds} seconds')
        await asyncio.sleep(seconds)
        await member.remove_roles(timeout_role)

    @cog_ext.cog_slash(name="lock", description="Lock a text or voice channel", options=[
        create_option(name="channel", description="The channel to lock (channel ID)", option_type=7, required=True)
    ])
    async def lock(self, ctx: SlashContext, channel: discord.abc.GuildChannel):
        overwrite = discord.PermissionOverwrite()
        if isinstance(channel, discord.TextChannel):
            overwrite.send_messages = False
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
            embed = discord.Embed(title=f'{channel.mention} has been locked.', color=self.embed_color)
            await ctx.send(embed=embed)
            logging.info(f'{ctx.author} locked {channel}')
        elif isinstance(channel, discord.VoiceChannel):
            overwrite.connect = False
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
            embed = discord.Embed(title=f'{channel.name} has been locked.', color=self.embed_color)
            await ctx.send(embed=embed)
            logging.info(f'{ctx.author} locked {channel}')

    @cog_ext.cog_slash(name="unlock", description="Unlock a text or voice channel", options=[
        create_option(name="channel", description="The channel to unlock (channel ID)", option_type=7, required=True)
    ])
    async def unlock(self, ctx: SlashContext, channel: discord.abc.GuildChannel):
        overwrite = discord.PermissionOverwrite()
        if isinstance(channel, discord.TextChannel):
            overwrite.send_messages = None
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
            embed = discord.Embed(title=f'{channel.mention} has been unlocked.', color=self.embed_color)
            await ctx.send(embed=embed)
            logging.info(f'{ctx.author} unlocked {channel}')
        elif isinstance(channel, discord.VoiceChannel):
            overwrite.connect = None
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
            embed = discord.Embed(title=f'{channel.name} has been unlocked.', color=self.embed_color)
            await ctx.send(embed=embed)
            logging.info(f'{ctx.author} unlocked {channel}')

class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.level_cooldown = 60
        self.level_roles = {}
        self.embed_color = 0x00FF00

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        # add leveling logic here

    @cog_ext.cog_slash(name="set_cooldown", description="Set the level cooldown time (in seconds)", options=[
        create_option(name="seconds", description="The number of seconds to set the level cooldown to", option_type=4, required=True)
    ])
    async def set_cooldown(self, ctx: SlashContext, seconds: int):
        self.level_cooldown = seconds
        embed = discord.Embed(title=f'Level cooldown set to {seconds} seconds.', color=self.embed_color)
        await ctx.send(embed=embed)
        logging.info(f'{ctx.author} set level cooldown to {seconds} seconds')

    @cog_ext.cog_slash(name="set_level", description="Manually set a member's level", options=[
        create_option(name="member", description="The member whose level to set", option_type=6, required=True),
        create_option(name="level", description="The level to set the member to", option_type=4, required=True)
    ])
    async def set_level(self, ctx: SlashContext, member: discord.Member, level: int):
        # set member's level here
        embed = discord.Embed(title=f"{member}'s level has been set to {level}.", color=self.embed_color)
        await ctx.send(embed=embed)
        logging.info(f"{ctx.author} set {member}'s level to {level}")

    @cog_ext.cog_slash(name="set_role", description="Set a role to be awarded at a certain level", options=[
        create_option(name="level", description="The level at which to award the role", option_type=4, required=True),
        create_option(name="role", description="The role to award at the specified level (role ID)", option_type=8, required=True)
    ])
    async def set_role(self, ctx: SlashContext, level: int, role: discord.Role):
        self.level_roles[level] = role
        embed = discord.Embed(title=f'Role {role} will be awarded at level {level}.', color=self.embed_color)
        await ctx.send(embed=embed)
        logging.info(f'{ctx.author} set role {role} to be awarded at level {level}')

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.embed_color = 0x0000FF

    @cog_ext.cog_slash(name="play", description="Play music from a URL", options=[
        create_option(name="url", description="The URL of the music to play", option_type=3, required=True)
    ])
    async def play(self, ctx: SlashContext, url: str):
        # add music playing logic here
        embed = discord.Embed(title=f'Playing music from {url}.', color=self.embed_color)
        await ctx.send(embed=embed)
        logging.info(f'{ctx.author} played music from {url}')

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not member == self.bot.user:
            return

        if before.channel and not after.channel:
            # bot has left the voice channel
            pass
        elif after.channel and not before.channel:
            # bot has joined the voice channel
            pass
        elif before.channel == after.channel:
            # bot is still in the same voice channel
            voice_client = after.channel.guild.voice_client
            if not voice_client.is_playing():
                # music has stopped playing
                await voice_client.disconnect()

bot.add_cog(Moderation(bot))
bot.add_cog(Leveling(bot))
bot.add_cog(Music(bot))

bot.run('YOUR_TOKEN_HERE')