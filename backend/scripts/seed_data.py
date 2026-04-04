"""
CourtAlert — Seed Script
Populates the database with realistic dummy data for demo/testing.

Run from backend/ directory:
    python scripts/seed_data.py

Creates:
  - 1 admin + 2 NGO users
  - 6 court records
  - 6 case registrations (1 inactive)
  - 15 hearings (mix of past/upcoming)
  - 12 notifications (delivered/failed/sent)
  - 5 whatsapp_commands (REG/STOP/STATUS/UNKNOWN)
"""

import asyncio
import sys
import os
from datetime import date, datetime, timezone, timedelta
import uuid

# Make sure app package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import text

from app.core.config import settings
from app.core.security import hash_password
from app.models.base import Base
from app.models.user import User
from app.models.court import Court
from app.models.registration import Registration
from app.models.hearing import Hearing
from app.models.notification import Notification
from app.models.whatsapp_command import WhatsappCommand
from app.models.enums import (
    UserRole, ChannelType, NotificationStatus, CommandType
)

# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

engine = create_async_engine(
    settings.async_database_url,
    connect_args={"ssl": "require"},
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

today = date.today()

def past(days: int) -> date:
    return today - timedelta(days=days)

def future(days: int) -> date:
    return today + timedelta(days=days)

def dt_past(days: int) -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=days)


# ---------------------------------------------------------------------------
# Seed functions
# ---------------------------------------------------------------------------

async def seed_users(db: AsyncSession) -> dict:
    print("  → Seeding users...")
    users = {
        "admin": User(
            email="admin@courtalert.in",
            hashed_password=hash_password("Admin@123"),
            full_name="CourtAlert Admin",
            org_name="CourtAlert",
            role=UserRole.admin,
        ),
        "ngo1": User(
            email="taha@dlsa-pune.org",
            hashed_password=hash_password("Ngo@12345"),
            full_name="Taha Kotwal",
            org_name="DLSA Pune",
            role=UserRole.ngo_user,
        ),
        "ngo2": User(
            email="priya@legalaid-mumbai.org",
            hashed_password=hash_password("Ngo@12345"),
            full_name="Priya Sharma",
            org_name="Legal Aid Society Mumbai",
            role=UserRole.ngo_user,
        ),
    }
    for u in users.values():
        db.add(u)
    await db.flush()
    print(f"     ✓ {len(users)} users created")
    return users


async def seed_courts(db: AsyncSession) -> list:
    print("  → Seeding courts...")
    courts = [
        Court(state_code="MH", district_code="PN", court_name="District Court, Pune",
              address="District Court Complex, Shivajinagar, Pune - 411005",
              latitude=18.530680, longitude=73.847820, pin_code="411005"),
        Court(state_code="MH", district_code="MB", court_name="Bombay High Court",
              address="Fort, Mumbai - 400032",
              latitude=18.931610, longitude=72.834750, pin_code="400032"),
        Court(state_code="DL", district_code="CC", court_name="Delhi High Court",
              address="Sher Shah Road, New Delhi - 110003",
              latitude=28.622760, longitude=77.240890, pin_code="110003"),
        Court(state_code="KA", district_code="BL", court_name="City Civil Court, Bengaluru",
              address="Mayo Hall Campus, Bengaluru - 560001",
              latitude=12.977410, longitude=77.596990, pin_code="560001"),
        Court(state_code="TN", district_code="CH", court_name="City Civil Court, Chennai",
              address="High Court Campus, Chennai - 600104",
              latitude=13.053040, longitude=80.282460, pin_code="600104"),
        Court(state_code="TS", district_code="HY", court_name="City Civil Court, Hyderabad",
              address="Nayapul, Hyderabad - 500001",
              latitude=17.386040, longitude=78.474540, pin_code="500001"),
    ]
    for c in courts:
        db.add(c)
    await db.flush()
    print(f"     ✓ {len(courts)} courts created")
    return courts


async def seed_registrations(db: AsyncSession, users: dict) -> dict:
    print("  → Seeding registrations...")
    ngo1_id = users["ngo1"].id
    ngo2_id = users["ngo2"].id

    regs = {
        "r1": Registration(
            cnr_number="MHPN0101234562024",
            phone_number="+919876543210",
            language="hi",
            case_title="Ramesh Patil vs State of Maharashtra",
            court_name="District Court, Pune",
            state_code="MH", district_code="PN",
            registered_by=ngo1_id,
            is_active=True,
            last_synced_at=dt_past(1),
        ),
        "r2": Registration(
            cnr_number="MHPN0209876542025",
            phone_number="+919876543211",
            language="mr",
            case_title="Sunita Sharma vs Pune Municipal Corporation",
            court_name="District Court, Pune",
            state_code="MH", district_code="PN",
            registered_by=ngo1_id,
            is_active=True,
            last_synced_at=dt_past(2),
        ),
        "r3": Registration(
            cnr_number="DLCC0312345672024",
            phone_number="+918765432109",
            language="hi",
            case_title="Amit Kumar vs Union of India",
            court_name="Delhi High Court",
            state_code="DL", district_code="CC",
            registered_by=ngo2_id,
            is_active=True,
            last_synced_at=dt_past(1),
        ),
        "r4": Registration(
            cnr_number="KABL0456789012025",
            phone_number="+917654321098",
            language="kn",
            case_title="Kavitha Reddy vs Revenue Authority",
            court_name="City Civil Court, Bengaluru",
            state_code="KA", district_code="BL",
            registered_by=ngo2_id,
            is_active=True,
            last_synced_at=dt_past(3),
        ),
        "r5": Registration(
            cnr_number="TNCH0598765432024",
            phone_number="+916543210987",
            language="ta",
            case_title="Meena Devi vs District Collector",
            court_name="City Civil Court, Chennai",
            state_code="TN", district_code="CH",
            registered_by=ngo1_id,
            is_active=True,
            last_synced_at=dt_past(2),
        ),
        "r6": Registration(
            cnr_number="MHPN0634567892023",
            phone_number="+915432109876",
            language="mr",
            case_title="Salim Khan vs State of Maharashtra",
            court_name="District Court, Pune",
            state_code="MH", district_code="PN",
            registered_by=ngo1_id,
            is_active=False,   # deactivated — user sent STOP
            last_synced_at=dt_past(10),
        ),
    }
    for r in regs.values():
        db.add(r)
    await db.flush()
    print(f"     ✓ {len(regs)} registrations created")
    return regs


async def seed_hearings(db: AsyncSession, regs: dict) -> dict:
    print("  → Seeding hearings...")
    hearings = {}

    # r1 — Patil vs State (3 hearings: 2 past, 1 upcoming in 7 days)
    hearings["h1_1"] = Hearing(registration_id=regs["r1"].id, hearing_date=past(60),
        hearing_type="First Hearing", court_room="Court No. 3",
        judge_name="Hon. Justice S.K. Joshi", purpose="Filing of documents", is_completed=True)
    hearings["h1_2"] = Hearing(registration_id=regs["r1"].id, hearing_date=past(20),
        hearing_type="Evidence", court_room="Court No. 3",
        judge_name="Hon. Justice S.K. Joshi", purpose="Cross examination", is_completed=True)
    hearings["h1_3"] = Hearing(registration_id=regs["r1"].id, hearing_date=future(7),
        hearing_type="Final Arguments", court_room="Court No. 3",
        judge_name="Hon. Justice S.K. Joshi", purpose="Final arguments", is_completed=False)

    # r2 — Sharma vs PMC (3 hearings: 1 past, 1 very soon, 1 future)
    hearings["h2_1"] = Hearing(registration_id=regs["r2"].id, hearing_date=past(45),
        hearing_type="First Hearing", court_room="Court No. 7",
        judge_name="Hon. Justice A.R. Patil", purpose="Initial arguments", is_completed=True)
    hearings["h2_2"] = Hearing(registration_id=regs["r2"].id, hearing_date=future(3),
        hearing_type="IA Hearing", court_room="Court No. 7",
        judge_name="Hon. Justice A.R. Patil", purpose="Stay application", is_completed=False)
    hearings["h2_3"] = Hearing(registration_id=regs["r2"].id, hearing_date=future(30),
        hearing_type="Final Arguments", court_room="Court No. 7",
        judge_name="Hon. Justice A.R. Patil", purpose="Final hearing", is_completed=False)

    # r3 — Kumar vs UoI (2 hearings: 1 past, 1 upcoming in 1 day)
    hearings["h3_1"] = Hearing(registration_id=regs["r3"].id, hearing_date=past(90),
        hearing_type="First Hearing", court_room="Court No. 12",
        judge_name="Hon. Justice M.K. Verma", purpose="Filing", is_completed=True)
    hearings["h3_2"] = Hearing(registration_id=regs["r3"].id, hearing_date=future(1),
        hearing_type="Written Statement", court_room="Court No. 12",
        judge_name="Hon. Justice M.K. Verma", purpose="Submission of written statement", is_completed=False)

    # r4 — Reddy vs Revenue (2 hearings: 1 past, 1 upcoming in 14 days)
    hearings["h4_1"] = Hearing(registration_id=regs["r4"].id, hearing_date=past(30),
        hearing_type="Framing of Issues", court_room="Court No. 2",
        judge_name="Hon. Justice P.R. Nair", purpose="Issue framing", is_completed=True)
    hearings["h4_2"] = Hearing(registration_id=regs["r4"].id, hearing_date=future(14),
        hearing_type="Evidence", court_room="Court No. 2",
        judge_name="Hon. Justice P.R. Nair", purpose="Evidence recording", is_completed=False)

    # r5 — Devi vs Collector (3 hearings)
    hearings["h5_1"] = Hearing(registration_id=regs["r5"].id, hearing_date=past(120),
        hearing_type="First Hearing", court_room="Court No. 5",
        judge_name="Hon. Justice R.S. Iyer", purpose="Initial filing", is_completed=True)
    hearings["h5_2"] = Hearing(registration_id=regs["r5"].id, hearing_date=past(15),
        hearing_type="Evidence", court_room="Court No. 5",
        judge_name="Hon. Justice R.S. Iyer", purpose="Evidence", is_completed=True)
    hearings["h5_3"] = Hearing(registration_id=regs["r5"].id, hearing_date=future(21),
        hearing_type="Final Arguments", court_room="Court No. 5",
        judge_name="Hon. Justice R.S. Iyer", purpose="Final arguments", is_completed=False)

    # r6 — Khan vs State (inactive case — 2 past hearings only)
    hearings["h6_1"] = Hearing(registration_id=regs["r6"].id, hearing_date=past(180),
        hearing_type="First Hearing", court_room="Court No. 1",
        judge_name="Hon. Justice B.D. Khan", purpose="Filing", is_completed=True)
    hearings["h6_2"] = Hearing(registration_id=regs["r6"].id, hearing_date=past(90),
        hearing_type="Evidence", court_room="Court No. 1",
        judge_name="Hon. Justice B.D. Khan", purpose="Evidence", is_completed=True)

    for h in hearings.values():
        db.add(h)
    await db.flush()
    print(f"     ✓ {len(hearings)} hearings created")
    return hearings


async def seed_notifications(db: AsyncSession, regs: dict, hearings: dict):
    print("  → Seeding notifications...")
    notifications = [
        # r1 h1_3 (upcoming in 7 days) — 7-day alert sent and delivered
        Notification(
            registration_id=regs["r1"].id, hearing_id=hearings["h1_3"].id,
            channel=ChannelType.whatsapp, status=NotificationStatus.delivered,
            message_text="⚖️ आपकी सुनवाई 7 दिन बाद है। केस: Ramesh Patil vs State of Maharashtra। कोर्ट: District Court, Pune। तारीख: " + future(7).strftime("%d %b %Y"),
            message_language="hi", days_before=7,
            twilio_sid="SM1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d",
            sent_at=dt_past(0), delivered_at=dt_past(0),
        ),
        # r2 h2_2 (upcoming in 3 days) — 7-day and 3-day alerts
        Notification(
            registration_id=regs["r2"].id, hearing_id=hearings["h2_2"].id,
            channel=ChannelType.whatsapp, status=NotificationStatus.delivered,
            message_text="⚖️ तुमची सुनावणी 7 दिवसांनंतर आहे। केस: Sunita Sharma vs PMC।",
            message_language="mr", days_before=7,
            twilio_sid="SM2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7",
            sent_at=dt_past(4), delivered_at=dt_past(4),
        ),
        Notification(
            registration_id=regs["r2"].id, hearing_id=hearings["h2_2"].id,
            channel=ChannelType.whatsapp, status=NotificationStatus.delivered,
            message_text="⚖️ तुमची सुनावणी 3 दिवसांनंतर आहे। केस: Sunita Sharma vs PMC।",
            message_language="mr", days_before=3,
            twilio_sid="SM3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8",
            sent_at=dt_past(0), delivered_at=dt_past(0),
        ),
        # r3 h3_2 (upcoming in 1 day) — all 3 alerts sent
        Notification(
            registration_id=regs["r3"].id, hearing_id=hearings["h3_2"].id,
            channel=ChannelType.whatsapp, status=NotificationStatus.delivered,
            message_text="⚖️ Your hearing is in 7 days. Case: Amit Kumar vs Union of India. Court: Delhi High Court.",
            message_language="hi", days_before=7,
            twilio_sid="SM4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9",
            sent_at=dt_past(6), delivered_at=dt_past(6),
        ),
        Notification(
            registration_id=regs["r3"].id, hearing_id=hearings["h3_2"].id,
            channel=ChannelType.whatsapp, status=NotificationStatus.delivered,
            message_text="⚖️ Your hearing is in 3 days. Case: Amit Kumar vs Union of India.",
            message_language="hi", days_before=3,
            twilio_sid="SM5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0",
            sent_at=dt_past(2), delivered_at=dt_past(2),
        ),
        Notification(
            registration_id=regs["r3"].id, hearing_id=hearings["h3_2"].id,
            channel=ChannelType.whatsapp, status=NotificationStatus.sent,
            message_text="⚖️ Your hearing is TOMORROW. Case: Amit Kumar vs Union of India. Court: Delhi High Court.",
            message_language="hi", days_before=1,
            twilio_sid="SM6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1",
            sent_at=dt_past(0), delivered_at=None,
        ),
        # r4 — failed WhatsApp, retried via SMS
        Notification(
            registration_id=regs["r4"].id, hearing_id=hearings["h4_2"].id,
            channel=ChannelType.whatsapp, status=NotificationStatus.failed,
            message_text="⚖️ ನಿಮ್ಮ ವಿಚಾರಣೆ 7 ದಿನಗಳಲ್ಲಿ ಇದೆ. ಕೇಸ್: Kavitha Reddy vs Revenue Authority.",
            message_language="kn", days_before=7,
            twilio_sid="SM7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2",
            error_message="WhatsApp delivery failed: number not on WhatsApp",
            sent_at=dt_past(7), delivered_at=None,
        ),
        Notification(
            registration_id=regs["r4"].id, hearing_id=hearings["h4_2"].id,
            channel=ChannelType.sms, status=NotificationStatus.delivered,
            message_text="CourtAlert: Nimma vicharne 7 dinagalalli ide. Case: Kavitha Reddy vs Revenue Authority. Court: Bengaluru.",
            message_language="kn", days_before=7,
            twilio_sid="SM8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3",
            sent_at=dt_past(7), delivered_at=dt_past(7),
        ),
        # r5 h5_3 — past alerts for past hearings
        Notification(
            registration_id=regs["r5"].id, hearing_id=hearings["h5_2"].id,
            channel=ChannelType.whatsapp, status=NotificationStatus.delivered,
            message_text="⚖️ உங்கள் விசாரணை 7 நாட்களில் உள்ளது. வழக்கு: Meena Devi vs Collector.",
            message_language="ta", days_before=7,
            twilio_sid="SM9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4",
            sent_at=dt_past(22), delivered_at=dt_past(22),
        ),
        Notification(
            registration_id=regs["r5"].id, hearing_id=hearings["h5_2"].id,
            channel=ChannelType.whatsapp, status=NotificationStatus.delivered,
            message_text="⚖️ உங்கள் விசாரணை 3 நாட்களில் உள்ளது. வழக்கு: Meena Devi vs Collector.",
            message_language="ta", days_before=3,
            twilio_sid="SM0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5",
            sent_at=dt_past(18), delivered_at=dt_past(18),
        ),
        Notification(
            registration_id=regs["r5"].id, hearing_id=hearings["h5_2"].id,
            channel=ChannelType.whatsapp, status=NotificationStatus.delivered,
            message_text="⚖️ உங்கள் விசாரணை நாளை உள்ளது. வழக்கு: Meena Devi vs Collector.",
            message_language="ta", days_before=1,
            twilio_sid="SM1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6",
            sent_at=dt_past(16), delivered_at=dt_past(16),
        ),
        # r6 — inactive case, old notification
        Notification(
            registration_id=regs["r6"].id, hearing_id=hearings["h6_2"].id,
            channel=ChannelType.whatsapp, status=NotificationStatus.delivered,
            message_text="⚖️ तुमची सुनावणी 7 दिवसांनंतर आहे। केस: Salim Khan vs State.",
            message_language="mr", days_before=7,
            twilio_sid="SM2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7",
            sent_at=dt_past(97), delivered_at=dt_past(97),
        ),
    ]
    for n in notifications:
        db.add(n)
    await db.flush()
    print(f"     ✓ {len(notifications)} notifications created")


async def seed_whatsapp_commands(db: AsyncSession, regs: dict):
    print("  → Seeding whatsapp_commands...")
    commands = [
        WhatsappCommand(
            from_number="+919876543210",
            body="REG MHPN0101234562024 HI",
            command_type=CommandType.REG,
            cnr_extracted="MHPN0101234562024",
            language_extracted="hi",
            registration_id=regs["r1"].id,
            response_sent="✅ Registered successfully!\n\n📋 Case: Ramesh Patil vs State of Maharashtra\n🏛️ Court: District Court, Pune",
            twilio_sid="SMa1b2c3d4e5f6a7b8c9d0e1f2a3b4c5",
            received_at=dt_past(30),
        ),
        WhatsappCommand(
            from_number="+919876543211",
            body="REG MHPN0209876542025 MR",
            command_type=CommandType.REG,
            cnr_extracted="MHPN0209876542025",
            language_extracted="mr",
            registration_id=regs["r2"].id,
            response_sent="✅ Registered successfully!\n\n📋 Case: Sunita Sharma vs Pune Municipal Corporation",
            twilio_sid="SMb2c3d4e5f6a7b8c9d0e1f2a3b4c5d6",
            received_at=dt_past(20),
        ),
        WhatsappCommand(
            from_number="+919876543210",
            body="STATUS",
            command_type=CommandType.STATUS,
            cnr_extracted=None,
            language_extracted=None,
            registration_id=regs["r1"].id,
            response_sent="📋 You have 1 active case(s):\n\n• Ramesh Patil vs State of Maharashtra",
            twilio_sid="SMc3d4e5f6a7b8c9d0e1f2a3b4c5d6e7",
            received_at=dt_past(10),
        ),
        WhatsappCommand(
            from_number="+915432109876",
            body="STOP",
            command_type=CommandType.STOP,
            cnr_extracted=None,
            language_extracted=None,
            registration_id=regs["r6"].id,
            response_sent="✅ Unsubscribed. 1 case(s) deactivated. You will no longer receive alerts.",
            twilio_sid="SMd4e5f6a7b8c9d0e1f2a3b4c5d6e7f8",
            received_at=dt_past(5),
        ),
        WhatsappCommand(
            from_number="+919999999999",
            body="Hello who is this?",
            command_type=CommandType.UNKNOWN,
            cnr_extracted=None,
            language_extracted=None,
            registration_id=None,
            response_sent="👋 Welcome to CourtAlert!\n\nCommands:\n• REG <CNR> <LANG> — Register a case\n• STATUS — View your active cases\n• STOP — Unsubscribe",
            twilio_sid="SMe5f6a7b8c9d0e1f2a3b4c5d6e7f8a9",
            received_at=dt_past(2),
        ),
    ]
    for c in commands:
        db.add(c)
    await db.flush()
    print(f"     ✓ {len(commands)} whatsapp_commands created")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main():
    print("\n🌱 CourtAlert Seed Script")
    print("=" * 40)

    async with AsyncSessionLocal() as db:
        try:
            # Check if already seeded
            result = await db.execute(text("SELECT COUNT(*) FROM users"))
            count = result.scalar_one()
            if count > 0:
                print(f"\n⚠️  Database already has {count} user(s).")
                confirm = input("   Re-seed? This will ADD more records (y/N): ").strip().lower()
                if confirm != "y":
                    print("   Aborted.")
                    return

            users  = await seed_users(db)
            await seed_courts(db)
            regs   = await seed_registrations(db, users)
            hrngs  = await seed_hearings(db, regs)
            await seed_notifications(db, regs, hrngs)
            await seed_whatsapp_commands(db, regs)

            await db.commit()
            print("\n✅ Seed complete!")
            print("\n📋 Login credentials:")
            print("   Admin  → admin@courtalert.in   / Admin@123")
            print("   NGO 1  → taha@dlsa-pune.org    / Ngo@12345")
            print("   NGO 2  → priya@legalaid-mumbai.org / Ngo@12345")

        except Exception as e:
            await db.rollback()
            print(f"\n❌ Seed failed: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(main())
