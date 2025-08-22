"""
Utility Commands Cog

Contains general utility commands like ping, status, help, etc.
"""

import logging
import os
from datetime import datetime
from typing import Tuple

import discord
from discord.ext import commands

from app.enum.colors import StatusColors


class UtilityCog(commands.Cog):
    """Cog containing utility commands."""

    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(self.__class__.__name__)

    @commands.command(name='ping', help='Check bot response time')
    async def ping(self, ctx):
        """Simple ping command."""
        latency, status = self.get_latency()
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Latência: {latency}ms",
            color=status
        )
        await ctx.send(embed=embed)

    @commands.command(name='status', help='Check bot and webhook status')
    async def status(self, ctx):
        """Display bot and webhooks status information."""
        try:
            # Get webhook status
            webhook_status = await self.bot.webhook_manager.get_webhook_status()

            embed = discord.Embed(
                title="🤖 Status do Fiapinho Bot",
                color=StatusColors.INFO_GREEN.value
            )

            latency = self.get_latency()
            # Bot info
            embed.add_field(
                name="📊 Bot Status",
                value=f"🟢 Online\n\n🏓 Ping: {latency[0]}ms",
                inline=True
            )

            # Guilds info
            embed.add_field(
                name="🏠 Servidores",
                value=f"Conectado a {len(self.bot.guilds)} servidor(es)",
                inline=True
            )

            # Sync task status
            task_status = "🟢 Ativo" if self.bot.sync_calendar_task.is_running() else "🔴 Parado"
            embed.add_field(
                name="⏰ Task de Sincronização \n\n",
                value=task_status,
                inline=True
            )

            # Webhook status
            if 'sync_calendar' in webhook_status:
                last_exec = webhook_status['sync_calendar'].get('last_execution')
                if last_exec:
                    if isinstance(last_exec, str):
                        last_exec_str = last_exec
                    else:
                        last_exec_str = last_exec.strftime("%d/%m/%Y %H:%M")
                else:
                    last_exec_str = "Nunca executado"

                embed.add_field(
                    name="📅 Última Sincronização do Calendário",
                    value=last_exec_str,
                    inline=False
                )

            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error in status command: {e}")
            await ctx.send(f"❌ Erro ao obter status: {str(e)}")

    @commands.command(name='info', help='Bot information')
    async def info(self, ctx):
        """Display bot information."""
        embed = discord.Embed(
            title="🤖 Fiapinho Bot",
            description="Bot para estudantes da FIAP - Gestão de eventos e calendário",
            color=StatusColors.INFO_GREEN.value
        )

        total_members = sum(guild.member_count for guild in self.bot.guilds)

        embed.add_field(
            name="📊 Estatísticas",
            value=f"Servidores: {len(self.bot.guilds)}\nUsuários: {total_members}",
            inline=True
        )

        embed.add_field(
            name="💻 Tecnologia",
            value="Python 3.13+\ndiscord.py",
            inline=True
        )

        embed.add_field(
            name="🔗 Links",
            value=f"[GitHub]({os.getenv('GITHUB_URL')})",
            inline=True
        )

        embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        embed.set_footer(
            text=f"Desenvolvido com ❤️ para os estudantes da FIAP • Bot ID: {self.bot.user.id}"
        )

        await ctx.send(embed=embed)

    @commands.command(name='uptime', help='Mostrar tempo de atividade do bot')
    async def uptime(self, ctx):
        """Show how long the bot has been running."""
        if not hasattr(self.bot, 'start_time'):
            embed = discord.Embed(
                title="⏰ Uptime",
                description="Tempo de atividade não disponível",
                color=StatusColors.ALERT.value
            )
        else:
            uptime = datetime.now() - self.bot.start_time
            days = uptime.days
            hours, remainder = divmod(uptime.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"

            embed = discord.Embed(
                title="⏰ Uptime",
                description=f"Bot ativo há: **{uptime_str}**",
                color=StatusColors.SUCCESS.value
            )

        await ctx.send(embed=embed)

    @commands.command(name='version', help='Exibe a versão do bot')
    async def version(self, ctx):
        """Show bot version information."""
        try:
            from app import __version__
            version = __version__
        except ImportError:
            __version__ = "0.1.0"
            version = __version__

        embed = discord.Embed(
            title="📋 Versão",
            description=f"Fiapinho Bot v{version}",
            color=StatusColors.INFO_GREEN.value
        )

        embed.add_field(
            name="✨ Recursos Principais",
            value="• Sincronização automática de calendário e eventos FIAP"
                  "\n• Notificações de eventos",
            inline=False
        )

        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Handle command errors for this cog."""
        if isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(
                title="⏳ Comando em Cooldown",
                description=f"Tente novamente em {error.retry_after:.1f} segundos",
                color=StatusColors.ALERT.value
            )
            await ctx.send(embed=embed)
        elif isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="❌ Permissões Insuficientes",
                description="Você não tem permissão para usar este comando",
                color=StatusColors.ERROR.value
            )
            await ctx.send(embed=embed)
        elif isinstance(error, commands.BotMissingPermissions):
            embed = discord.Embed(
                title="❌ Bot sem Permissões",
                description="O bot não tem permissões necessárias para executar este comando",
                color=StatusColors.ERROR.value
            )
            await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_ready(self):
        """Called when the cog is ready."""
        self.logger.info("Utility Cog loaded successfully")


    def get_latency(self) -> Tuple[int, int]:
        latency = round(self.bot.latency * 1000)
        status = StatusColors.SUCCESS.value \
            if latency < 100 else StatusColors.ALERT.value if latency < 200 else StatusColors.ERROR.value
        return latency, status


async def setup(bot):
    """Setup function for loading the cog."""
    await bot.add_cog(UtilityCog(bot))
