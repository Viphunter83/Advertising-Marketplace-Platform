"""
app/services/email_service.py
Сервис для отправки email-уведомлений.
"""
import logging
from typing import Optional, Dict, Any
from pathlib import Path
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from jinja2 import Environment, FileSystemLoader
from app.config import settings

logger = logging.getLogger(__name__)

# Jinja2 для HTML шаблонов
template_dir = Path(__file__).parent.parent / "templates" / "emails"
if not template_dir.exists():
    template_dir.mkdir(parents=True, exist_ok=True)

jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))


class EmailService:
    """Сервис для отправки email."""
    
    @staticmethod
    async def send_email(
        to_email: str,
        subject: str,
        template_name: str,
        context: Dict[str, Any]
    ) -> bool:
        """
        Отправляет email через SendGrid.
        
        Args:
            to_email (str): Email получателя
            subject (str): Тема письма
            template_name (str): Имя HTML шаблона (без .html)
            context (dict): Контекст для шаблона
        
        Returns:
            bool: True если успешно отправлено
        """
        if not settings.sendgrid_api_key:
            logger.warning("SendGrid API key not configured, skipping email")
            return False
        
        try:
            # Рендерим HTML шаблон
            template = jinja_env.get_template(f"{template_name}.html")
            html_content = template.render(**context)
            
            # Создаём письмо
            message = Mail(
                from_email=Email(settings.sendgrid_from_email, settings.sendgrid_from_name),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_content)
            )
            
            # Отправляем через SendGrid
            sg = SendGridAPIClient(settings.sendgrid_api_key)
            response = sg.send(message)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Email sent to {to_email}: {subject}")
                return True
            else:
                logger.warning(f"Email send failed: {response.status_code}")
                return False
        
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False
    
    
    @staticmethod
    async def send_welcome_email(user_email: str, user_name: str) -> bool:
        """Приветственное письмо после регистрации."""
        return await EmailService.send_email(
            to_email=user_email,
            subject="Добро пожаловать в Advertising Marketplace!",
            template_name="welcome",
            context={
                "user_name": user_name,
                "login_url": f"{settings.frontend_url}/login"
            }
        )
    
    
    @staticmethod
    async def send_new_campaign_email(
        channel_owner_email: str,
        channel_owner_name: str,
        seller_name: str,
        campaign_id: str,
        budget: float
    ) -> bool:
        """Уведомление о новой заявке для владельца канала."""
        return await EmailService.send_email(
            to_email=channel_owner_email,
            subject=f"Новая заявка на размещение от {seller_name}",
            template_name="new_campaign",
            context={
                "channel_owner_name": channel_owner_name,
                "seller_name": seller_name,
                "budget": budget,
                "campaign_url": f"{settings.frontend_url}/channel/campaigns/{campaign_id}"
            }
        )
    
    
    @staticmethod
    async def send_campaign_accepted_email(
        seller_email: str,
        seller_name: str,
        channel_name: str,
        campaign_id: str
    ) -> bool:
        """Уведомление продавцу о принятии заявки."""
        return await EmailService.send_email(
            to_email=seller_email,
            subject=f"Заявка принята каналом {channel_name}",
            template_name="campaign_accepted",
            context={
                "seller_name": seller_name,
                "channel_name": channel_name,
                "campaign_url": f"{settings.frontend_url}/seller/campaigns/{campaign_id}"
            }
        )
    
    
    @staticmethod
    async def send_campaign_completed_email(
        channel_owner_email: str,
        channel_owner_name: str,
        payment_amount: float,
        campaign_id: str
    ) -> bool:
        """Уведомление о выплате владельцу канала."""
        return await EmailService.send_email(
            to_email=channel_owner_email,
            subject=f"Выплата {payment_amount} RUB зачислена на счёт",
            template_name="campaign_completed",
            context={
                "channel_owner_name": channel_owner_name,
                "payment_amount": payment_amount,
                "campaign_url": f"{settings.frontend_url}/channel/campaigns/{campaign_id}"
            }
        )

