from django.core.mail import send_mail
from django.conf import settings


def enviar_email_recuperacao(email_destino: str, username: str, token: str):
    """Envia e-mail com link de recuperação de senha."""
    link = f"http://localhost:8000/recuperar-senha/confirmar/?token={token}"
    assunto = "Recuperação de senha - Papelaria Mundo Letrado"
    mensagem_texto = (
        f"Olá, {username}!\n\n"
        f"Recebemos uma solicitação para redefinir sua senha.\n"
        f"Acesse o link abaixo (válido por 1 hora):\n\n"
        f"{link}\n\n"
        f"Se você não solicitou isso, ignore este e-mail.\n\n"
        f"Papelaria Mundo Letrado"
    )
    mensagem_html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 500px; margin: 0 auto;">
        <div style="background-color: #1F3A5F; padding: 20px; text-align: center;">
            <h1 style="color: #D4A017; margin: 0;">Papelaria Mundo Letrado</h1>
        </div>
        <div style="padding: 30px; background-color: #F5F7FA;">
            <p>Olá, <strong>{username}</strong>!</p>
            <p>Recebemos uma solicitação para redefinir sua senha.</p>
            <p>Clique no botão abaixo (link válido por <strong>1 hora</strong>):</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{link}"
                   style="background-color: #1F3A5F; color: white; padding: 12px 30px;
                          text-decoration: none; border-radius: 5px; font-weight: bold;">
                    Redefinir minha senha
                </a>
            </div>
            <p style="color: #6B7280; font-size: 12px;">
                Se você não solicitou isso, ignore este e-mail.
            </p>
        </div>
    </div>
    """
    send_mail(
        subject=assunto,
        message=mensagem_texto,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email_destino],
        html_message=mensagem_html,
        fail_silently=False,
    )
