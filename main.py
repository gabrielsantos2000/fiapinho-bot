"""
Fiapinho Discord Bot
A Discord bot for FIAP College students to manage and sync calendar events.

This version demonstrates how to use Cogs for better command organization.
"""

import os
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

import discord
from discord.ext import commands, tasks

from app.webhooks.webhook import WebhookManager
from app.enum.colors import StatusColors

# Load environment variables
load_dotenv()


# Setup logging
def setup_logging():
    log_level = getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper())
    log_file = os.getenv('LOG_FILE', 'logs/bot.log')

    # Create logs directory if it doesn't exist
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )


class FiapinhoBot(commands.Bot):
    """Main Discord bot class for Fiapinho using Cogs."""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(
            command_prefix=os.getenv('BOT_PREFIX', '/'),
            intents=intents,
            description='Fiapinho - Discord bot for FIAP College students',
            help_command=None
        )

        self.webhook_manager = WebhookManager(self)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.start_time = datetime.now()  # Track bot start time

        # List of cogs to load
        self.initial_cogs = [
            'app.cogs.fiap',
            'app.cogs.utility'
        ]

    async def setup_hook(self):
        """Called when the bot is starting up."""
        self.logger.info("Setting up Fiapinho bot...")

        # Load cogs
        await self.load_cogs()

        # Start webhooks tasks
        if not self.sync_calendar_task.is_running():
            self.sync_calendar_task.start()
            
        # Start event expiration checking task
        if not self.check_expired_events_task.is_running():
            self.check_expired_events_task.start()

    async def load_cogs(self):
        """Load all cogs."""
        for cog in self.initial_cogs:
            try:
                await self.load_extension(cog)
                self.logger.info(f"Loaded cog: {cog}")
            except Exception as e:
                self.logger.error(f"Failed to load cog {cog}: {e}")

    async def on_ready(self):
        """Called when the bot has successfully logged in."""
        self.logger.info(f'{self.user} has connected to Discord!')
        self.logger.info(f'Bot is in {len(self.guilds)} guilds')

        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="FIAP Calendar Events"
            )
        )

    async def on_command_error(self, ctx, error):
        """Global error handler for commands."""
        if isinstance(error, commands.CommandNotFound):
            return

        self.logger.error(f'Command error in {ctx.command}: {error}')

        embed = discord.Embed(
            title="❌ Erro no Comando",
            description=f"Ocorreu um erro: {str(error)}",
            color=StatusColors.ERROR.value
        )
        await ctx.send(embed=embed)

    @tasks.loop(hours=int(os.getenv('WEBHOOK_INTERVAL_HOURS', '24')))
    async def sync_calendar_task(self):
        """Periodic task to sync FIAP calendar events."""
        try:
            self.logger.info("Starting calendar sync task...")
            await self.webhook_manager.sync_calendar()
        except Exception as e:
            self.logger.error(f"Error in calendar sync task: {e}")

    @sync_calendar_task.before_loop
    async def before_sync_calendar_task(self):
        """Wait for bot to be ready before starting the sync task."""
        await self.wait_until_ready()

    @tasks.loop(minutes=int(os.getenv('EVENT_EXPIRATION_CHECK_HOURS', '2')))
    async def check_expired_events_task(self):
        """Periodic task to check for expired events and update their messages."""
        try:
            self.logger.info("Starting expired events check task...")
            webhook = self.webhook_manager.webhooks.get('sync_calendar')
            if webhook:
                await webhook.check_expired_events()
            else:
                self.logger.warning("Calendar webhook not found for expired events check")
        except Exception as e:
            self.logger.error(f"Error in expired events check task: {e}")

    @check_expired_events_task.before_loop
    async def before_check_expired_events_task(self):
        """Wait for bot to be ready before starting the expired events check task."""
        await self.wait_until_ready()

    async def close(self):
        """Clean shutdown of the bot."""
        self.logger.info("Shutting down Fiapinho bot...")
        if self.sync_calendar_task.is_running():
            self.sync_calendar_task.cancel()
        if self.check_expired_events_task.is_running():
            self.check_expired_events_task.cancel()
        await super().close()

    # ==================== ADMIN COMMANDS ====================

    @commands.command(name='reload', hidden=False)
    @commands.is_owner()
    async def reload_cog(self, ctx, cog_name: str):
        """Reload a specific cog (Owner only)."""
        try:
            await self.reload_extension(f'app.cogs.{cog_name}')
            embed = discord.Embed(
                title="✅ Cog Recarregado",
                description=f"Cog '{cog_name}' recarregado com sucesso!",
                color=StatusColors.SUCCESS.value
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erro ao Recarregar",
                description=f"Erro ao recarregar cog '{cog_name}': {str(e)}",
                color=StatusColors.ERROR.value
            )
            await ctx.send(embed=embed)

    @commands.command(name='load', hidden=True)
    @commands.is_owner()
    async def load_cog(self, ctx, cog_name: str):
        """Load a specific cog (Owner only)."""
        try:
            await self.load_extension(f'app.cogs.{cog_name}')
            embed = discord.Embed(
                title="✅ Cog Carregado",
                description=f"Cog '{cog_name}' carregado com sucesso!",
                color=StatusColors.SUCCESS.value
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erro ao Carregar",
                description=f"Erro ao carregar cog '{cog_name}': {str(e)}",
                color=StatusColors.ERROR.value
            )
            await ctx.send(embed=embed)

    @commands.command(name='unload', hidden=True)
    @commands.is_owner()
    async def unload_cog(self, ctx, cog_name: str):
        """Unload a specific cog (Owner only)."""
        try:
            await self.unload_extension(f'app.cogs.{cog_name}')
            embed = discord.Embed(
                title="✅ Cog Descarregado",
                description=f"Cog '{cog_name}' descarregado com sucesso!",
                color=StatusColors.SUCCESS.value
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erro ao Descarregar",
                description=f"Erro ao descarregar cog '{cog_name}': {str(e)}",
                color=StatusColors.ERROR.value
            )
            await ctx.send(embed=embed)

    @commands.command(name='cogs', hidden=True)
    @commands.is_owner()
    async def list_cogs(self, ctx):
        """List all loaded cogs (Owner only)."""
        loaded_cogs = [cog for cog in self.cogs.keys()]

        embed = discord.Embed(
            title="📦 Cogs Carregados",
            description="Lista de todos os cogs carregados:",
            color=StatusColors.INFO_GREEN.value
        )

        if loaded_cogs:
            embed.add_field(
                name="Cogs Ativos",
                value="\n".join(f"• {cog}" for cog in loaded_cogs),
                inline=False
            )
        else:
            embed.add_field(
                name="Nenhum Cog",
                value="Nenhum cog carregado",
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name='help_fiapinho')
    async def help_command(self, ctx, *, command_name: str = None):
        """Custom help command with better formatting."""
        if command_name:
            # Show help for specific command
            command = self.get_command(command_name)
            if not command:
                await ctx.send(f"❌ Comando '{command_name}' não encontrado.")
                return

            embed = discord.Embed(
                title=f"❓ Ajuda: {command.name}",
                description=command.help or "Sem descrição disponível",
                color=StatusColors.INFO_GREEN.value
            )

            if command.usage:
                embed.add_field(
                    name="Uso",
                    value=f"`{ctx.prefix}{command.name} {command.usage}`",
                    inline=False
                )

            if command.aliases:
                embed.add_field(
                    name="Aliases",
                    value=", ".join(command.aliases),
                    inline=False
                )
        else:
            embed = discord.Embed(
                title="🤖 Comandos do Fiapinho Bot",
                description="Lista de comandos disponíveis:",
                color=StatusColors.INFO_GREEN.value
            )

            main_commands = [cmd.name for cmd in self.commands if not cmd.hidden]
            if main_commands:
                embed.add_field(
                    name="📂 Comandos Principais",
                    value=", ".join(f"`{cmd}`" for cmd in main_commands),
                    inline=False
                )
            
            # Group commands by cog
            for cog_name, cog in self.cogs.items():
                commands_list = [cmd.name for cmd in cog.get_commands() if not cmd.hidden]
                if commands_list:
                    # Clean up cog name for display
                    display_name = cog_name.replace('Cog', '').replace('Fiapinho', 'FIAP')
                    embed.add_field(
                        name=f"📂 {display_name}",
                        value=", ".join(f"`{cmd}`" for cmd in commands_list),
                        inline=False
                    )

            embed.set_footer(text="Use !help <comando> para mais detalhes sobre um comando específico")

        await ctx.send(embed=embed)


def main():
    """Main function to run the bot."""
    setup_logging()
    logger = logging.getLogger('main')

    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        logger.error("DISCORD_BOT_TOKEN is required! Please check your .env file.")
        return

    bot = FiapinhoBot()

    try:
        bot.run(token)
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
    finally:
        if not bot.is_closed():
            bot.close()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nBot stopped by user")
