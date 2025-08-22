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
            ("add_event", "Adicionar evento manualmente"),
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

    @fiap_group.command(name='add_event', description='Adiciona um evento manualmente ao calendário')
    async def add_manual_event(self, ctx: commands.Context, *, args: str = None):
        """Add a manual event to the calendar system.
        
        Usage: !fiap add_even
            title="Event Title"
            description="Event Description"
            start="DD/MM/YYYY HH:MM"
            end="DD/MM/YYYY HH:MM"
            type="EventType"
            course="CourseName"
            teams="TeamslLink"
            location="Location"
        
        Required: title, description, start, end
        Optional: type (default: Custom), course, teams, location
        """
        if not ctx.author.get_role(Roles.ADMINISTRATOR.value):
            embed = discord.Embed(
                title='❌ Esse comando só pode ser executado por administradores',
                color=FiapColors.RED.value
            )
            await ctx.send(embed=embed)
            return

        if not args:
            embed = discord.Embed(
                title="📋 Como usar o comando add_event",
                description=(
                    "**Uso:**\n"
                    '`!fiap add_event title="Título do Evento" description="Descrição" start="DD/MM/AAAA HH:MM" '
                    'end="DD/MM/AAAA HH:MM"`\n\n'
                    "**Parâmetros obrigatórios:**\n"
                    "• `title` - Título do evento\n"
                    "• `description` - Descrição do evento\n"
                    "• `start` - Data/hora de início (formato: DD/MM/AAAA HH:MM)\n"
                    "• `end` - Data/hora de fim (formato: DD/MM/AAAA HH:MM)\n\n"
                    "**Parâmetros opcionais:**\n"
                    "• `type` - Tipo do evento (padrão: Custom)\n"
                    "• `course` - Nome do curso\n"
                    "• `teams` - Link do Teams quando o evento for em formato de Live\n"
                    "• `location` - Local do evento quando não é Live \n\n"
                    "**Exemplo:**\n"
                    '`!fiap add_event title="Aula de Python" description="Aula sobre estruturas de dados" '
                    'start="25/12/2024 14:30" end="25/12/2024 16:30" type="Aula" course="Análise e Desenvolvimento"`'
                ),
                color=FiapColors.RED.value
            )
            await ctx.send(embed=embed)
            return

        self.logger.info(f"Manual event addition requested by {ctx.author}")

        embed = discord.Embed(
            title="📝 Adicionando Evento",
            description="Processando dados do evento...",
            color=StatusColors.INFO_BLUE.value
        )
        message = await ctx.send(embed=embed)

        try:
            from datetime import datetime
            import time
            import uuid
            import re
            import validators
            
            # Parse arguments using regex to handle quoted strings
            arg_pattern = r'(\w+)="([^"]+)"'
            matches = re.findall(arg_pattern, args)
            
            if not matches:
                embed = discord.Embed(
                    title="❌ Formato Inválido",
                    description='Use o formato: `title="Título" description="Descrição" '
                                'start="DD/MM/AAAA HH:MM" end="DD/MM/AAAA HH:MM"`\n'
                                'Use `!fiap add_event` sem parâmetros para ver o formato completo.',
                    color=StatusColors.ERROR.value
                )
                await message.edit(embed=embed)
                return

            params = {key: value for key, value in matches}

            required = ['title', 'description', 'start', 'end']
            missing = [param for param in required if param not in params]
            
            if missing:
                embed = discord.Embed(
                    title="❌ Parâmetros Obrigatórios Faltando",
                    description=f"Os seguintes parâmetros são obrigatórios: {', '.join(missing)}\n"
                                f"Use `!fiap add_event` sem parâmetros para ver o formato completo.",
                    color=StatusColors.ERROR.value
                )
                await message.edit(embed=embed)
                return

            try:
                start_dt = datetime.strptime(params['start'], "%d/%m/%Y %H:%M")
                end_dt = datetime.strptime(params['end'], "%d/%m/%Y %H:%M")
            except ValueError:
                embed = discord.Embed(
                    title="❌ Formato de Data Inválido",
                    description="Use o formato DD/MM/AAAA HH:MM para as datas.\nExemplo: start=\"25/12/2024 14:30\"",
                    color=StatusColors.ERROR.value
                )
                await message.edit(embed=embed)
                return
            
            if start_dt >= end_dt:
                embed = discord.Embed(
                    title="❌ Datas Inválidas",
                    description="A data de início deve ser anterior à data de fim.",
                    color=StatusColors.ERROR.value
                )
                await message.edit(embed=embed)
                return

            teams_link = params.get('teams')
            if teams_link and not validators.url(teams_link):
                embed = discord.Embed(
                    title="❌ Link Inválido",
                    description="O link do Teams fornecido não é uma URL válida.",
                    color=StatusColors.ERROR.value
                )
                await message.edit(embed=embed)
                return

            webhook = self.bot.webhook_manager.webhooks.get('sync_calendar')
            if not webhook:
                embed = discord.Embed(
                    title="❌ Webhook Não Encontrado",
                    description="Sistema de calendário não encontrado.",
                    color=StatusColors.ERROR.value
                )
                await message.edit(embed=embed)
                return

            event_id = f"manual_{int(time.time())}_{uuid.uuid4().hex[:8]}"
            manual_event = {
                'id': event_id,
                'content': params['title'],
                'name': params['title'],
                'description': params['description'],
                'timeopen': int(start_dt.timestamp()),
                'timeclose': int(end_dt.timestamp()),
                'timeopen_formated': start_dt.strftime("%d/%m/%Y"),
                'type': params.get('type', 'Custom'),
                'course_name': params.get('course', None),
                'local': teams_link or params.get('location', "A definir"),
                'module': "manual_events",
                'is_manual': True,
                'created_by': str(ctx.author.id),
                'created_at': datetime.now().timestamp()
            }

            existing_events = await webhook.load_existing_events()

            existing_ids = {event.get('id') for event in existing_events if event.get('id')}
            if event_id in existing_ids:
                embed = discord.Embed(
                    title="❌ Erro",
                    description="Erro interno: ID do evento já existe. Tente novamente.",
                    color=StatusColors.ERROR.value
                )
                await message.edit(embed=embed)
                return

            existing_events.append(manual_event)
            await webhook.save_events(existing_events)

            channel_id = os.getenv('DISCORD_CALENDAR_CHANNEL_ID')
            if channel_id:
                channel = self.bot.get_channel(int(channel_id))
                if channel:
                    embed_event, images = await webhook.create_event_embed(manual_event)
                    notification_msg = await channel.send(
                        "📅 **Evento adicionado manualmente!**",
                        embed=embed_event,
                        files=images
                    )

                    manual_event['discord_message_id'] = notification_msg.id
                    manual_event['discord_channel_id'] = channel.id
                    manual_event['notification_sent_at'] = datetime.now().timestamp()

                    for i, event in enumerate(existing_events):
                        if event.get('id') == event_id:
                            existing_events[i] = manual_event
                            break
                    await webhook.save_events(existing_events)
            
            embed = discord.Embed(
                title="✅ Evento Adicionado",
                description=(
                    f"Evento '{params['title']}' foi adicionado com sucesso!\n\n"
                    f"**ID:** {event_id}\n"
                    f"**Início:** {start_dt.strftime('%d/%m/%Y às %H:%M')}\n"
                    f"**Fim:** {end_dt.strftime('%d/%m/%Y às %H:%M')}\n"
                    f"**Tipo:** {params.get('type', 'Custom')}"
                ),
                color=StatusColors.SUCCESS.value
            )
            
            await message.edit(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error adding manual event: {e}")
            embed = discord.Embed(
                title="❌ Erro Inesperado",
                description=f"Ocorreu um erro ao adicionar o evento: {str(e)}",
                color=StatusColors.ERROR.value
            )
            await message.edit(embed=embed)


async def setup(bot):
    await bot.add_cog(FiapinhoCog(bot))
