from __future__ import annotations
import os
import smtplib
from email.mime.text import MIMEText


def send_email(to_email: str, subject: str, html_body: str) -> None:
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    from_name = os.getenv("SMTP_FROM_NAME", "HR Decision Lab")

    if not all([host, user, password]):
        raise RuntimeError(
            "Email is not configured. Set SMTP_HOST, SMTP_USER, and SMTP_PASSWORD environment variables."
        )

    msg = MIMEText(html_body, "html", "utf-8")
    msg["Subject"] = subject
    msg["From"] = f"{from_name} <{user}>"
    msg["To"] = to_email

    if port == 465:
        with smtplib.SMTP_SSL(host, port) as server:
            server.login(user, password)
            server.sendmail(user, [to_email], msg.as_string())
    else:
        with smtplib.SMTP(host, port) as server:
            server.starttls()
            server.login(user, password)
            server.sendmail(user, [to_email], msg.as_string())


def invite_email_html(name: str, invite_url: str, deadline_text: str, is_candidate: bool) -> str:
    greeting = f"مرحبًا {name}،" if name else "مرحبًا،"
    consent_note = (
        "<p>سيتم مشاركة نتيجتك مع مسؤول التوظيف كجزء من عملية التقييم.</p>" if is_candidate else ""
    )
    deadline_note = f"<p>يرجى إكمال التقييم قبل: <strong>{deadline_text}</strong></p>" if deadline_text else ""
    return f"""
    <div dir="rtl" style="font-family: sans-serif; line-height: 1.8;">
        <p>{greeting}</p>
        <p>تمت دعوتك لإكمال تقييم قصير في "مختبر قرار الموارد البشرية".</p>
        {consent_note}
        {deadline_note}
        <p><a href="{invite_url}" style="background:#c9a24b; color:#151b26; padding:12px 24px;
        text-decoration:none; border-radius:6px; display:inline-block;">ابدأ التقييم</a></p>
        <p style="color:#888; font-size:13px;">إذا لم يعمل الزر، افتحي هذا الرابط مباشرة: {invite_url}</p>
    </div>
    """


def results_ready_email_html(admin_name: str, dashboard_url: str) -> str:
    greeting = f"مرحبًا {admin_name}،" if admin_name else "مرحبًا،"
    return f"""
    <div dir="rtl" style="font-family: sans-serif; line-height: 1.8;">
        <p>{greeting}</p>
        <p>انتهى جميع المدعوين في هذه الدفعة من إكمال التقييم، ونتائجهم جاهزة الآن للاطلاع.</p>
        <p><a href="{dashboard_url}" style="background:#c9a24b; color:#151b26; padding:12px 24px;
        text-decoration:none; border-radius:6px; display:inline-block;">عرض النتائج</a></p>
    </div>
    """


def share_result_email_html(sender_name: str, dominant_archetype_ar: str, dominant_archetype: str,
                             narrative_summary: str, app_url: str) -> str:
    """Type 2: a user sharing THEIR OWN result with a friend/colleague via email."""
    sender_line = f"{sender_name} شارك معك نتيجته" if sender_name else "شخص شاركك نتيجته"
    narrative_block = f"<p style='color:#ccc;'>{narrative_summary}</p>" if narrative_summary else ""
    return f"""
    <div dir="rtl" style="font-family: sans-serif; line-height: 1.8; background:#151b26; color:#ede8d8; padding:24px;">
        <p style="color:#c9a24b;">{sender_line} من "مختبر قرار الموارد البشرية":</p>
        <h2 style="margin:8px 0;">{dominant_archetype_ar}</h2>
        <p style="color:#9aa4b8; margin-top:-8px;">{dominant_archetype}</p>
        {narrative_block}
        <p><a href="{app_url}" style="background:#c9a24b; color:#151b26; padding:12px 24px;
        text-decoration:none; border-radius:6px; display:inline-block;">جرّب نمط قرارك أنت أيضًا</a></p>
    </div>
    """
