import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import settings
from graph.state import ClarifAIState

logger = logging.getLogger(__name__)


def send_escalation_email(
    to_email: str,
    tenant_id: str,
    question: str,
    generation: str,
    confidence_score: float,
    messages: list,
) -> bool:
    """Send escalation email to the tenant's support team."""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"[ClarifAI Escalation] Customer question requires human support"
        msg["From"] = settings.smtp_from_email
        msg["To"] = to_email

        # Build conversation history
        history = ""
        for m in messages:
            role = "Customer" if m["role"] == "user" else "AI"
            history += f"{role}: {m['content']}\n\n"

        body = f"""
A customer question has been escalated and requires human attention.

TENANT ID: {tenant_id}
CONFIDENCE SCORE: {confidence_score} (threshold: 0.7)

CUSTOMER QUESTION:
{question}

AI ATTEMPTED ANSWER:
{generation or "No answer was generated"}

FULL CONVERSATION HISTORY:
{history or "No previous messages"}

Please follow up with the customer directly.

— ClarifAI Escalation System
        """

        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_username, settings.smtp_password)
            server.sendmail(settings.smtp_from_email, to_email, msg.as_string())

        logger.info(f"Escalation email sent to {to_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send escalation email: {e}")
        return False


async def escalate(state: ClarifAIState) -> dict:
    """
    Escalation node — marks conversation as escalated and sends email.
    Runs when router decides to escalate OR when confidence score is too low.
    """
    logger.info(f"Escalating conversation for tenant {state['tenant_id']}")

    # Send email if tenant has escalation email configured
    escalation_email = state.get("escalation_email")
    if escalation_email:
        send_escalation_email(
            to_email=escalation_email,
            tenant_id=state["tenant_id"],
            question=state["question"],
            generation=state.get("generation", ""),
            confidence_score=state.get("confidence_score", 0.0),
            messages=state.get("messages", []),
        )

    # Generate a human-friendly escalation message
    escalation_message = (
        "I've escalated your question to our support team. "
        "A human agent will follow up with you shortly. "
        "Thank you for your patience."
    )

    messages = state.get("messages", [])
    messages.append({"role": "assistant", "content": escalation_message})

    return {
        "escalated": True,
        "generation": escalation_message,
        "messages": messages,
    }