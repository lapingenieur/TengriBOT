import discord
from discord.ext import commands
from messages import *


def get_langs(server):
    return sorted([r.name.split(" ")[1] for r in server.roles if r.name.startswith("Connait")])


def get_role_learn(server, lang):
    return discord.utils.get(server.roles, name=f'Apprend {lang}')


def get_role_know(server, lang):
    return discord.utils.get(server.roles, name=f'Connait {lang}')


def enum(people):
    return f"`{'`, `'.join(people[:-1])}` et `{people[-1]}`"


def normalize(word):
    """Normalize a word."""
    return word[0].upper() + word[1:].lower()


def is_moderator(context):
    """Check the author is a moderator."""
    modo_roles = {"igidarúren «prophètes»", "díngen «divinités»", "Admin"}
    return not modo_roles.isdisjoint({role.name for role in context.message.author.roles})


class Assignations(commands.Cog):
    """Commandes d'assignations"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def ilearn(self, context, *args):
        """Assigner le rôle "Apprends" pour une langue."""
        if len(args) < 1:
            await context.channel.send(LANG_MISSING)
        else:
            server = context.message.guild
            lang = normalize(args[0])
            if lang not in get_langs(server):
                await context.channel.send(LANG_UNKNOWN.format(lang=lang))
            else:
                await context.message.author.remove_roles(get_role_know(server, lang))
                await context.message.author.add_roles(get_role_learn(server, lang))
                await context.channel.send(ROLES_CHANGE.format(role_verb=VERB_LEARN, role=LANG.format(lang=lang)))

    @commands.command(pass_context=True)
    async def iknow(self, context, *args):
        """Assigner le rôle "Connait" pour une langue."""
        if len(args) < 1:
            await context.channel.send(LANG_MISSING)
        else:
            server = context.message.guild
            lang = normalize(args[0])
            if lang not in get_langs(server):
                await context.channel.send(LANG_UNKNOWN.format(lang=lang))
            else:
                await context.message.author.remove_roles(get_role_learn(server, lang))
                await context.message.author.add_roles(get_role_know(server, lang))
                await context.channel.send(ROLES_CHANGE.format(role_verb=VERB_KNOW, role=LANG.format(lang=lang)))

    @commands.command(pass_context=True)
    async def forget(self, context, *args):
        """Oublier une certaine langue."""
        if len(args) < 1:
            await context.channel.send(LANG_MISSING)
        else:
            server = context.message.guild
            lang = normalize(args[0])
            if lang not in get_langs(server):
                await context.channel.send(LANG_UNKNOWN.format(lang=lang))
            else:
                await context.message.author.remove_roles(get_role_know(server, lang), get_role_learn(server, lang))
                await context.channel.send(ROLES_CHANGE.format(role_verb=VERB_FORGET, role=LANG.format(lang=lang)))

    @commands.command(pass_context=True)
    async def newlang(self, context, *args):
        """[MOD ONLY] Ajouter une langue."""
        if not is_moderator(context):
            await context.channel.send(MODO_FORBIDDEN)
        elif len(args) < 1:
            await context.channel.send(LANG_MISSING)
        else:
            server = context.message.guild
            lang = normalize(args[0])
            if lang in get_langs(server):
                await context.channel.send(LANG_EXISTS.format(lang=lang))
            else:
                await server.create_role(name=ROLE_KNOW.format(lang=lang))
                await server.create_role(name=ROLE_LEARN.format(lang=lang))
                await context.channel.send(LANG_NEW.format(lang=lang))

    @commands.command(pass_context=True)
    async def rmvlang(self, context, *args):
        """[MOD ONLY] Supprimer une langue."""
        if not is_moderator(context):
            await context.channel.send(MODO_FORBIDDEN)
        elif len(args) < 1:
            await context.channel.send(LANG_MISSING)
        else:
            server = context.message.guild
            lang = normalize(args[0])
            if lang not in get_langs(server):
                await context.channel.send(LANG_UNKNOWN.format(lang=lang))
            else:
                await get_role_know(server, lang).delete()
                await get_role_learn(server, lang).delete()
                await context.channel.send(LANG_RMV.format(lang=lang))

    @commands.command(pass_context=True)
    async def speakers(self, context, *args):
        """Afficher la liste des gens qui connaissent une certaine langue."""
        if len(args) < 1:
            await context.channel.send(LANG_MISSING)
        else:
            server = context.message.guild
            lang = normalize(args[0])
            speakers = sorted([user.name for user in server.members if (get_role_know(server, lang) in user.roles)])
            if lang not in get_langs(server):
                await context.channel.send(LANG_UNKNOWN.format(lang=lang))
            elif len(speakers) == 0:
                await context.channel.send(ROLES_NOBODY.format(role_verb=VERB_KNOW, role=LANG.format(lang=lang)))
            elif len(speakers) == 1:
                await context.channel.send(ROLES_ONE.format(role_verb=VERB_KNOW, speaker=speakers[0],
                                                            role=LANG.format(lang=lang)))
            else:
                await context.channel.send(ROLES_MANY.format(role_verb=VERB_KNOW, persons=enum(speakers),
                                                             role=LANG.format(lang=lang), nb=len(speakers)))

    @commands.command(pass_context=True)
    async def learners(self, context, *args):
        """Afficher la liste des gens qui apprennent une certaine langue."""
        if len(args) < 1:
            await context.channel.send(LANG_MISSING)
        else:
            server = context.message.guild
            lang = normalize(args[0])
            speakers = sorted([user.name for user in server.members if (get_role_learn(server, lang) in user.roles)])
            if lang not in get_langs(server):
                await context.channel.send(LANG_UNKNOWN.format(lang=lang))
            elif len(speakers) == 0:
                await context.channel.send(ROLES_NOBODY.format(role_verb=VERB_LEARN, role=LANG.format(lang=lang)))
            elif len(speakers) == 1:
                await context.channel.send(ROLES_ONE.format(role_verb=VERB_LEARN, person=speakers[0],
                                                            role=LANG.format(lang=lang)))
            else:
                await context.channel.send(ROLES_MANY.format(role_verb=VERB_LEARN, persons=enum(speakers),
                                                             role=LANG.format(lang=lang), nb=len(speakers)))

    @commands.command(pass_context=True)
    async def langs(self, context):
        """Afficher la liste des langages du serveur."""
        languages = get_langs(context.message.guild)
        await context.channel.send(LANG_LIST.format(nb_lang=len(languages), langs=languages))

    @commands.command(pass_context=True)
    async def ideols(self, context):
        """Afficher la liste des idéolinguistes du serveur."""
        server = context.message.guild
        role = discord.utils.get(server.roles, name='Idéolinguiste')
        ideols = sorted([user.name for user in server.members if (role in user.roles)])
        if len(ideols) == 0:
            await context.channel.send(ROLES_NOBODY.format(role_verb=VERB_BE, role=IDEOL))
        elif len(ideols) == 1:
            await context.channel.send(ROLES_ONE.format(role_verb=VERB_BE, person=ideols[0], role=IDEOL))
        else:
            await context.channel.send(ROLES_MANY.format(role_verb=VERB_BE, persons=enum(ideols),
                                                         role=IDEOL, nb=len(ideols)))

    @commands.command(pass_context=True)
    async def ideol(self, context):
        """Assigner le rôle idéolinguiste."""
        server = context.message.guild
        role = discord.utils.get(server.roles, name='Idéolinguiste')
        await context.message.author.add_roles(role)
        await context.channel.send(IDEOL_ADD)

    @commands.command(pass_context=True)
    async def rmvideol(self, context):
        """Retirer le rôle idéolinguiste."""
        server = context.message.guild
        role = discord.utils.get(server.roles, name='Idéolinguiste')
        await context.message.author.remove_roles(role)
        await context.channel.send(IDEOL_RMV)
