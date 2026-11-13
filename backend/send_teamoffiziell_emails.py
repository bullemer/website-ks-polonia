"""
One-time script: Send login emails to all Teamoffizielle.
Run on the server after deploy: python3 send_teamoffiziell_emails.py
"""
import asyncio
import os
import sys
import secrets
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def main():
    from config import SITE_URL
    from database import get_pool, close_pool
    from auth import hash_password
    from mailer import send_email

    pool = await get_pool()

    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT DISTINCT m.id, m.vorname, m.nachname, m.email, m.password_hash,
                   STRING_AGG(DISTINCT t.mannschaftsname, ', ' ORDER BY t.mannschaftsname) as teams
            FROM members m
            JOIN member_teams mt ON mt.member_id = m.id AND mt.status = 'active'
            JOIN teams t ON t.id = mt.team_id
            WHERE mt.role IN ('trainer', 'co-trainer', 'manager', 'teamoffizieller')
              AND m.is_active = TRUE
            GROUP BY m.id
            ORDER BY m.nachname, m.vorname
        """)

    print(f"\n{'='*60}")
    print(f"Teamoffizielle gefunden: {len(rows)}")
    print(f"{'='*60}\n")

    sent = []
    skipped = []
    errors = []

    for row in rows:
        member = dict(row)

        if not member.get("email") or not member["email"].strip():
            skipped.append(f"  ⚠  {member['vorname']} {member['nachname']} (ID {member['id']}) — keine E-Mail")
            continue

        email = member["email"].strip().lower()
        pw = secrets.token_urlsafe(10)[:10]
        hashed = hash_password(pw)

        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE members SET password_hash = $1, email_verified = TRUE, updated_at = NOW() WHERE id = $2",
                hashed, member["id"],
            )

        body = (
            f"Hallo {member['vorname']},\n\n"
            f"wir haben gute Neuigkeiten! Unser Mitgliederportal für KS Polonia Hamburg wurde "
            f"erweitert und bietet dir jetzt eine eigene Team-Verwaltung.\n\n"
            f"Als Teamoffizieller für {member['teams']} kannst du ab sofort:\n\n"
            f"  ⚽  Deinen Kader verwalten (Spieler hinzufügen, Rollen zuweisen)\n"
            f"  💰  Die Beitragszahlungen deines Teams einsehen und erfassen\n"
            f"  📝  Die Teamseite auf ks-polonia.de bearbeiten\n"
            f"  📸  Fotos und Inhalte für deine Mannschaft hochladen\n\n"
            f"═══════════════════════════════════\n"
            f"Deine Zugangsdaten:\n\n"
            f"  🌐  Portal: https://www.ks-polonia.de/portal/login\n"
            f"  📧  E-Mail: {email}\n"
            f"  🔑  Passwort: {pw}\n"
            f"═══════════════════════════════════\n\n"
            f"Nach dem Login findest du den Button \"Team verwalten\" auf deiner Portal-Startseite.\n\n"
            f"Wir möchten das Portal für euch Trainer und Betreuer so einfach und nützlich wie "
            f"möglich gestalten. Daher freuen wir uns über jede Rückmeldung:\n\n"
            f"  → Was fehlt dir?\n"
            f"  → Was könnten wir verbessern?\n"
            f"  → Welche Funktionen wünschst du dir?\n\n"
            f"Schick uns deine Ideen einfach als Antwort auf diese E-Mail oder schreib "
            f"an info@ks-polonia.de.\n\n"
            f"Wir freuen uns auf dein Feedback und auf eine erfolgreiche Zusammenarbeit! 💪\n\n"
            f"Sportliche Grüße,\n"
            f"Vorstand KS Polonia Hamburg e.V. 1988\n"
        )

        ok, err = send_email(
            subject="Dein neuer Teamportal-Zugang – KS Polonia",
            text_body=body,
            to_email=email,
        )
        if ok:
            sent.append(f"  ✅  {member['vorname']} {member['nachname']} → {email} ({member['teams']})")
            print(f"  ✅  Gesendet: {member['vorname']} {member['nachname']} → {email}")
        else:
            errors.append(f"  ❌  {member['vorname']} {member['nachname']}: {err}")
            print(f"  ❌  Fehler: {member['vorname']} {member['nachname']}: {err}")

    await close_pool()

    print(f"\n{'='*60}")
    print(f"ERGEBNIS")
    print(f"{'='*60}")
    print(f"  Gesendet:  {len(sent)}")
    print(f"  Übersprungen: {len(skipped)}")
    print(f"  Fehler:    {len(errors)}")
    print()
    if skipped:
        print("Übersprungen (keine E-Mail):")
        for s in skipped:
            print(s)
    if errors:
        print("\nFehler:")
        for e in errors:
            print(e)
    print()

if __name__ == "__main__":
    asyncio.run(main())
