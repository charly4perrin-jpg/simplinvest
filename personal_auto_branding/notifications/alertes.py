"""
Alertes — notifie le gestionnaire par email et/ou SMS.
Déclenché automatiquement sur : lead chaud, incident de crise, post publié.

Variables d'environnement :
  ALERT_EMAIL_FROM, ALERT_EMAIL_TO, ALERT_EMAIL_PASSWORD (Gmail SMTP)
  TWILIO_SID, TWILIO_TOKEN, TWILIO_FROM, TWILIO_TO  (SMS, optionnel)
"""

import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from config.settings import DATA_DIR


# ── EMAIL ─────────────────────────────────────────────────────────

def envoyer_email(sujet: str, corps: str, destinataire: str = None) -> bool:
    expediteur = os.getenv("ALERT_EMAIL_FROM")
    dest = destinataire or os.getenv("ALERT_EMAIL_TO")
    password = os.getenv("ALERT_EMAIL_PASSWORD")

    if not all([expediteur, dest, password]):
        _log_alerte("email_non_configure", sujet)
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[AutoBranding] {sujet}"
    msg["From"] = expediteur
    msg["To"] = dest
    msg.attach(MIMEText(corps, "html", "utf-8"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(expediteur, password)
            server.sendmail(expediteur, dest, msg.as_string())
        _log_alerte("email_envoye", sujet)
        return True
    except Exception as e:
        _log_alerte("email_erreur", f"{sujet} — {e}")
        return False


# ── SMS ───────────────────────────────────────────────────────────

def envoyer_sms(message: str) -> bool:
    sid = os.getenv("TWILIO_SID")
    token = os.getenv("TWILIO_TOKEN")
    from_num = os.getenv("TWILIO_FROM")
    to_num = os.getenv("TWILIO_TO")

    if not all([sid, token, from_num, to_num]):
        return False

    try:
        from twilio.rest import Client
        Client(sid, token).messages.create(body=message[:160], from_=from_num, to=to_num)
        _log_alerte("sms_envoye", message[:60])
        return True
    except ImportError:
        _log_alerte("twilio_non_installe", "pip install twilio")
        return False
    except Exception as e:
        _log_alerte("sms_erreur", str(e))
        return False


# ── ALERTES MÉTIER ────────────────────────────────────────────────

def alerter_lead_chaud(client_id: str, contact: str, score: int):
    sujet = f"🔥 Lead chaud détecté — {contact} ({score}/100)"
    corps = f"""
    <div style="font-family:system-ui;max-width:480px;margin:0 auto;background:#0f0f0f;color:#e8e8e8;padding:32px;border-radius:12px">
      <h2 style="color:#f97316;margin:0 0 16px">🔥 Lead chaud détecté</h2>
      <p style="color:#888;margin:0 0 24px">Compte géré : <strong style="color:#e8e8e8">{client_id}</strong></p>
      <div style="background:#1a1a1a;border:1px solid #2e2e2e;border-radius:8px;padding:20px;margin-bottom:24px">
        <p style="margin:0 0 8px"><strong>Contact :</strong> {contact}</p>
        <p style="margin:0 0 8px"><strong>Score :</strong> {score}/100</p>
        <p style="margin:0"><strong>Date :</strong> {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
      </div>
      <p style="color:#888;font-size:13px">Ce contact s'est engagé fortement avec le contenu.
      Connecte-toi au dashboard pour voir l'historique et envoyer un message d'approche.</p>
      <a href="http://localhost:5000/client/{client_id}/leads"
         style="display:inline-block;margin-top:16px;background:#4f8ef7;color:#fff;padding:10px 20px;border-radius:6px;text-decoration:none;font-weight:600">
        Voir le lead →
      </a>
    </div>
    """
    envoyer_email(sujet, corps)
    envoyer_sms(f"[AutoBranding] Lead chaud : {contact} ({score}/100) sur {client_id}")


def alerter_incident(client_id: str, type_incident: str, contenu: str, auteur: str):
    sujet = f"⚠️ Incident détecté — {type_incident}"
    corps = f"""
    <div style="font-family:system-ui;max-width:480px;margin:0 auto;background:#0f0f0f;color:#e8e8e8;padding:32px;border-radius:12px">
      <h2 style="color:#ef4444;margin:0 0 16px">⚠️ Intervention humaine requise</h2>
      <p style="color:#888;margin:0 0 24px">Compte : <strong style="color:#e8e8e8">{client_id}</strong></p>
      <div style="background:#450a0a;border:1px solid #991b1b;border-radius:8px;padding:20px;margin-bottom:24px">
        <p style="margin:0 0 8px"><strong>Type :</strong> {type_incident}</p>
        <p style="margin:0 0 8px"><strong>Auteur :</strong> {auteur}</p>
        <p style="margin:0 0 8px"><strong>Contenu :</strong> {contenu[:200]}</p>
        <p style="margin:0"><strong>Date :</strong> {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
      </div>
      <p style="color:#ef4444;font-size:13px">
        Le système a suspendu la réponse automatique. Une intervention manuelle est nécessaire.
      </p>
      <a href="http://localhost:5000/client/{client_id}"
         style="display:inline-block;margin-top:16px;background:#ef4444;color:#fff;padding:10px 20px;border-radius:6px;text-decoration:none;font-weight:600">
        Gérer l'incident →
      </a>
    </div>
    """
    envoyer_email(sujet, corps)
    envoyer_sms(f"[AutoBranding] ⚠️ INCIDENT sur {client_id} — {type_incident}. Action requise.")


def alerter_post_publie(client_id: str, sujet_post: str, url: str):
    sujet = f"✅ Post publié — {sujet_post[:50]}"
    corps = f"""
    <div style="font-family:system-ui;max-width:480px;margin:0 auto;background:#0f0f0f;color:#e8e8e8;padding:32px;border-radius:12px">
      <h2 style="color:#22c55e;margin:0 0 16px">✅ Post publié avec succès</h2>
      <p style="color:#888;margin:0 0 24px">Compte : <strong style="color:#e8e8e8">{client_id}</strong></p>
      <div style="background:#14532d;border:1px solid #166534;border-radius:8px;padding:20px;margin-bottom:24px">
        <p style="margin:0 0 8px"><strong>Sujet :</strong> {sujet_post}</p>
        <p style="margin:0"><strong>Publié le :</strong> {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
      </div>
      <a href="{url}" style="display:inline-block;margin-top:16px;background:#22c55e;color:#000;padding:10px 20px;border-radius:6px;text-decoration:none;font-weight:600">
        Voir sur LinkedIn →
      </a>
    </div>
    """
    envoyer_email(sujet, corps)


def _log_alerte(type_log: str, message: str):
    log_path = DATA_DIR / "metrics" / "alertes.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {type_log} | {message}\n")
