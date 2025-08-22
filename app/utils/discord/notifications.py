import logging
import os
from datetime import datetime

from discord import Embed

from app.enum.colors import StatusColors


class FiapinhoNotification:

    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(f"{self.__class__.__name__}")

    async def send_auth_failure_notification(self):
        """Send notification about authentication failure."""
        try:
            channel_id = os.getenv('DISCORD_MONITORING_CHANNEL_ID')
            if not channel_id:
                return

            channel = self.bot.get_channel(int(channel_id))
            if not channel:
                return

            embed = Embed(
                title="❌ Falha na Autenticação FIAP",
                description="Não foi possível fazer login na plataforma FIAP após várias tentativas.",
                color=StatusColors.ERROR.value,
                timestamp=datetime.now()
            )

            embed.add_field(
                name="🔧 Ação Necessária",
                value="Verifique as credenciais FIAP nas variáveis de ambiente.",
                inline=False
            )

            await channel.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error sending auth failure notification: {e}")
