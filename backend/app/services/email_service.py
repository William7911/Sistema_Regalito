import smtplib
import ssl
import asyncio
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

logger = logging.getLogger("email_service")


class EmailService:
    @staticmethod
    def _send_sync(to_email: str, subject: str, html_content: str, text_content: str = "") -> bool:
        if not settings.SMTP_HOST or not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            logger.warning(
                f"[SMTP NO CONFIGURADO] No se puede enviar correo a {to_email}. "
                f"Se requiere configurar SMTP_HOST, SMTP_USER y SMTP_PASSWORD en .env."
            )
            return False

        from_addr = settings.SMTP_FROM_EMAIL or settings.SMTP_USER
        from_display = f"{settings.SMTP_FROM_NAME} <{from_addr}>"

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = from_display
        msg["To"] = to_email

        if text_content:
            msg.attach(MIMEText(text_content, "plain", "utf-8"))
        if html_content:
            msg.attach(MIMEText(html_content, "html", "utf-8"))

        try:
            if settings.SMTP_USE_SSL or settings.SMTP_PORT == 465:
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, context=context, timeout=15) as server:
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                    server.sendmail(from_addr, [to_email], msg.as_string())
            else:
                with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
                    if settings.SMTP_USE_TLS:
                        context = ssl.create_default_context()
                        server.starttls(context=context)
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                    server.sendmail(from_addr, [to_email], msg.as_string())
            logger.info(f"Correo de verificación entregado exitosamente a {to_email} vía {settings.SMTP_HOST}:{settings.SMTP_PORT}")
            return True
        except Exception as e:
            logger.error(f"Error al enviar correo SMTP a {to_email}: {e}")
            return False

    @classmethod
    async def enviar_codigo_recuperacion(cls, to_email: str, nombre_usuario: str, codigo: str) -> bool:
        logger.info(f"[RECUPERACIÓN DE CONTRASEÑA] Código generado para '{to_email}' ({nombre_usuario}): {codigo}")

        subject = f"{codigo} es tu código de recuperación - Tienda El Regalito"
        html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; padding: 24px; margin: 0;">
    <div style="max-width: 520px; margin: 0 auto; background-color: #ffffff; border-radius: 14px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
        <div style="background-color: #0A5C5E; background: linear-gradient(135deg, #0D7377, #0A5C5E); padding: 24px; text-align: center;">
            <h1 style="color: #ffffff; margin: 0; font-size: 22px; font-weight: 700; letter-spacing: -0.5px;">Tienda El Regalito</h1>
            <p style="color: #AEE2E4; margin: 4px 0 0 0; font-size: 13px;">Sistema de Punto de Venta e Inventario</p>
        </div>
        <div style="padding: 28px 24px;">
            <h2 style="color: #1e293b; font-size: 18px; margin-top: 0; margin-bottom: 12px; font-weight: 600;">Recuperación de Contraseña</h2>
            <p style="color: #334155; font-size: 14px; line-height: 1.6; margin-bottom: 20px;">
                Hola <strong>{nombre_usuario}</strong>,<br>
                Hemos recibido una solicitud para restablecer tu contraseña. Utiliza el siguiente código de verificación de 6 dígitos:
            </p>
            <div style="text-align: center; margin: 28px 0;">
                <div style="display: inline-block; background-color: #F0FDFA; border: 2px dashed #0D7377; border-radius: 10px; padding: 14px 28px;">
                    <span style="font-family: monospace; font-size: 34px; font-weight: 700; letter-spacing: 10px; color: #0A5C5E;">{codigo}</span>
                </div>
            </div>
            <p style="color: #64748b; font-size: 13px; line-height: 1.5; margin-bottom: 16px;">
                Este código es válido durante los próximos <strong>15 minutos</strong> y puede utilizarse una única vez.
            </p>
            <p style="color: #94a3b8; font-size: 12px; line-height: 1.5; border-top: 1px solid #f1f5f9; padding-top: 16px; margin-bottom: 0;">
                Si tú no solicitaste este cambio, puedes ignorar este mensaje; tu contraseña actual continuará siendo segura.
            </p>
        </div>
        <div style="background-color: #f8fafc; padding: 12px; text-align: center; border-top: 1px solid #f1f5f9;">
            <span style="color: #94a3b8; font-size: 11px;">Panajachel, Sololá, Guatemala · Tienda El Regalito</span>
        </div>
    </div>
</body>
</html>"""
        text_content = f"Hola {nombre_usuario},\n\nTu código de recuperación es: {codigo}\n\nExpira en 15 minutos.\n\nSi no solicitaste este código, ignora este correo.\n\nTienda El Regalito"
        return await asyncio.to_thread(cls._send_sync, to_email, subject, html_content, text_content)

