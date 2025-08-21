import os
import logging

import discord

from app.utils.colors import FiapColors, StatusColors
from discord.ext import commands

class FiapinhoCog(commands.Cog):
    """Cog containing Fiapinho-related commands."""
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(self.__class__.__name__)

        self.prefix = os.getenv('BOT_PREFIX')
        self.subcommands_fiap_group = [
            ("sync_calendar", "Sincronizar calendário"),
            ("events_montly", "Mostrar eventos recentes"),
            ("events_today", "Mostrar eventos de hoje"),
            ("events_week", "Mostrar eventos da semana"),
            ("events_day [day]", "Mostrar os eventos do dia")
        ]

    @commands.group(name="fiap", help="Comandos relacionados a Fiap")
    async def fiap_groud(self, ctx):
        """Group command for Fiapinho commands."""
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="📚 Comandos Fiapinho",
                description=f"Use `{self.prefix}fiap <subcommando>` para acessar as funcionalidades do Fiapinho:",
                color=FiapColors.RED
            )

            for cmd, desc in self.subcommands_fiap_group:
                embed.add_field(
                    name=f"{self.prefix}fiap {cmd}",
                    value=desc,
                    inline=False
                )

    @fiap_groud.command(name='sync_calendar', help='Realiza a sincronização do calendário')
    async def sync_calendar(self, ctx):
        """Manually trigger calendar sync."""
        if ctx.author.has_permissions(administrator=False):
            embed = discord.Embed(
                title="❌ Esse comando só pode ser executado por administradores",
                color=FiapColors.RED
            )

            await ctx.send(embed=embed)
            return

        self.logger.info(f"Manual sync requested by {ctx.author}")

        # Send initial response
        embed = discord.Embed(
            title="🔄 Sincronização Manual",
            description="Iniciando sincronização do calendário FIAP...",
            color=StatusColors.INFO_BLUE
        )
        message = await ctx.send(embed=embed)

        try:
            # Execute sync
            result = await self.bot.webhook_manager.sync_calendar()

            if result:
                embed = discord.Embed(
                    title="✅ Sincronização Concluída",
                    description="Calendário FIAP sincronizado com sucesso!",
                    color=StatusColors.SUCCESS
                )
            else:
                embed = discord.Embed(
                    title="❌ Falha na Sincronização",
                    description="Erro durante a sincronização. Verifique os logs para detalhes.",
                    color=StatusColors.SUCCESS
                )

            await message.edit(embed=embed)

        except Exception as e:
            self.logger.error(f"Error in manual sync command: {e}")
            embed = discord.Embed(
                title="⚠️ Erro Inesperado",
                description=f"Ocorreu um erro: {str(e)}",
                color=StatusColors.SUCCESS
            )
            await message.edit(embed=embed)

async def setup(bot):
    await bot.add_cog(FiapinhoCog(bot))
