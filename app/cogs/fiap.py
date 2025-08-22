import os
import logging

import discord

from app.enum.colors import FiapColors, StatusColors
from app.enum.discord.roles import Roles
from discord.ext import commands

class FiapinhoCog(commands.Cog):
    """Cog containing Fiapinho-related commands."""
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(self.__class__.__name__)

        self.prefix = os.getenv('BOT_PREFIX')
        self.subcommands_fiap_group = [
            ("sync_calendar", "Sincronizar calendário"),
            ("check_expired", "Atualiza os eventos já expirados"),
            ("events_montly", "Mostrar eventos recentes"),
            ("events_today", "Mostrar eventos de hoje"),
            ("events_week", "Mostrar eventos da semana"),
            ("events_day [day]", "Mostrar os eventos do dia")
        ]

    @commands.group(name="fiap", help="Comandos relacionados a Fiap")
    async def fiap_group(self, ctx):
        """Group command for Fiapinho commands."""
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="📚 Comandos Fiapinho",
                description=f"Use `{self.prefix}fiap <subcommando>` para acessar as funcionalidades do Fiapinho:",
                color=FiapColors.RED.value
            )

            for cmd, desc in self.subcommands_fiap_group:
                embed.add_field(
                    name=f"{self.prefix}fiap {cmd}",
                    value=desc,
                    inline=False
                )
            
            await ctx.send(embed=embed)

    @fiap_group.command(name='sync_calendar', help='Realiza a sincronização do calendário')
    async def sync_calendar(self, ctx:commands.Context):
        """Manually trigger calendar sync."""
        self.logger.info(f"Is owner {not commands.is_owner()}")
        if not commands.is_owner():
            embed = discord.Embed(
                title="❌ Esse comando só pode ser executado por administradores",
                color=FiapColors.RED.value
            )

            await ctx.send(embed=embed)
            return

        self.logger.info(f"Manual sync requested by {ctx.author}")

        embed = discord.Embed(
            title="🔄 Sincronização Manual",
            description="Iniciando sincronização do calendário FIAP...",
            color=StatusColors.INFO_BLUE.value
        )
        message = await ctx.send(embed=embed)

        try:
            result = await self.bot.webhook_manager.sync_calendar(resync=True)

            if result:
                embed = discord.Embed(
                    title="✅ Sincronização Concluída",
                    description="Calendário FIAP sincronizado com sucesso!",
                    color=StatusColors.SUCCESS.value
                )
            else:
                embed = discord.Embed(
                    title="❌ Falha na Sincronização",
                    description="Erro durante a sincronização. Verifique os logs para detalhes.",
                    color=StatusColors.ERROR.value
                )

            await message.edit(embed=embed)

        except Exception as e:
            self.logger.error(f"Error in manual sync command: {e}")
            embed = discord.Embed(
                title="⚠️ Erro Inesperado",
                description=f"Ocorreu um erro: {str(e)}",
                color=StatusColors.SUCCESS.value
            )
            await message.edit(embed=embed)

    @fiap_group.command(name='events_montly', description='Exibe os eventos do mês')
    async def events_montly(self, ctx:commands.Context):
        """Manually trigger events recentes."""
        if not ctx.author.get_role(Roles.ADMINISTRATOR.value):
            embed = discord.Embed(
                title='❌ Esse comando só pode ser executado por administradores',
                color=FiapColors.RED.value
            )

            await ctx.send(embed=embed)
            return

    @fiap_group.command(name='check_expired', description='Verifica e atualiza eventos expirados')
    async def check_expired_events(self, ctx: commands.Context):
        """Manually trigger expired events check."""
        if not ctx.author.get_role(Roles.ADMINISTRATOR.value):
            embed = discord.Embed(
                title='❌ Esse comando só pode ser executado por administradores',
                color=FiapColors.RED.value
            )
            await ctx.send(embed=embed)
            return

        self.logger.info(f"Manual expired events check requested by {ctx.author}")

        embed = discord.Embed(
            title="🔍 Verificando Eventos Expirados",
            description="Verificando eventos expirados e atualizando mensagens...",
            color=StatusColors.INFO_BLUE.value
        )
        message = await ctx.send(embed=embed)

        try:
            webhook = self.bot.webhook_manager.webhooks.get('sync_calendar')
            if not webhook:
                embed = discord.Embed(
                    title="❌ Webhook Não Encontrado",
                    description="Webhook do calendário não foi encontrado.",
                    color=StatusColors.ERROR.value
                )
                await message.edit(embed=embed)
                return

            result = await webhook.check_expired_events()

            if result:
                embed = discord.Embed(
                    title="✅ Verificação Concluída",
                    description="Eventos expirados verificados e atualizados com sucesso!",
                    color=StatusColors.SUCCESS.value
                )
            else:
                embed = discord.Embed(
                    title="⚠️ Erro na Verificação",
                    description="Erro durante a verificação de eventos expirados. Verifique os logs para detalhes.",
                    color=StatusColors.ERROR.value
                )

            await message.edit(embed=embed)

        except Exception as e:
            self.logger.error(f"Error in manual expired events check command: {e}")
            embed = discord.Embed(
                title="⚠️ Erro Inesperado",
                description=f"Ocorreu um erro: {str(e)}",
                color=StatusColors.ERROR.value
            )
            await message.edit(embed=embed)


async def setup(bot):
    await bot.add_cog(FiapinhoCog(bot))
