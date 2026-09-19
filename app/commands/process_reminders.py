from datetime import datetime, UTC

from app import create_app
from app.extensions import db
from app.models.reminder import Reminder
from app.models.campaign import Campaign
from app.services.reminder_service import ReminderService
from app.services.campaign_service import CampaignService


def process_due_reminders():
    """
    Find and process reminders that are due.
    """

    now = datetime.now(UTC).replace(tzinfo=None)

    print()
    print("=" * 60)
    print("CHURCHCONNECT REMINDER PROCESSOR")
    print("=" * 60)
    print(f"Processor started: {now}")
    print()

    reminders = db.session.scalars(
        db.select(Reminder).where(
            Reminder.is_active.is_(True),
            Reminder.status == "scheduled",
            db.or_(
                db.and_(
                    Reminder.recurrence_type == "one_time",
                    Reminder.scheduled_at <= now
                ),
                db.and_(
                    Reminder.recurrence_type != "one_time",
                    Reminder.next_run_at.is_not(None),
                    Reminder.next_run_at <= now
                )
            )
        )
    ).all()

    print(f"Found {len(reminders)} due reminder(s).")
    print()

    if not reminders:

        print("No reminders to process.")

    else:

        for reminder in reminders:

            print("-" * 60)
            print(f"Reminder ID: {reminder.id}")
            print(f"Title: {reminder.title}")
            print(f"Audience: {reminder.audience_type}")
            print(f"Scheduled: {reminder.scheduled_at}")
            print(f"Next run: {reminder.next_run_at}")
            print()

            try:

                result = ReminderService.process_reminder(
                    reminder
                )

                print()
                print("Processing result:")
                print(f"Sent: {result['sent']}")
                print(f"Failed: {result['failed']}")
                print(f"Status: {result['status']}")
                print(f"Next run: {result['next_run_at']}")

            except Exception as error:

                print()
                print("REMINDER PROCESSING ERROR")
                print(error)

                db.session.rollback()

    print()


def process_due_campaigns():
    """
    Find and process campaigns that are due.
    """

    now = datetime.now(UTC).replace(tzinfo=None)

    print()
    print("=" * 60)
    print("CHURCHCONNECT CAMPAIGN PROCESSOR")
    print("=" * 60)
    print(f"Processor started: {now}")
    print()

    campaigns = db.session.scalars(
        db.select(Campaign).where(
            Campaign.is_active.is_(True),
            Campaign.status == "scheduled",
            Campaign.scheduled_at.is_not(None),
            Campaign.scheduled_at <= now
        )
    ).all()

    print(f"Found {len(campaigns)} due campaign(s).")
    print()

    if not campaigns:

        print("No campaigns to process.")

    else:

        for campaign in campaigns:

            print("-" * 60)
            print(f"Campaign ID: {campaign.id}")
            print(f"Title: {campaign.title}")
            print(f"Audience: {campaign.audience_type}")
            print(f"Scheduled: {campaign.scheduled_at}")
            print()

            try:

                result = CampaignService.process_campaign(
                    campaign
                )

                print()
                print("Campaign processing result:")
                print(f"Recipients: {result['total']}")
                print(f"Sent: {result['sent']}")
                print(f"Failed: {result['failed']}")
                print(f"Status: {result['status']}")

                if result.get("failure_reason"):

                    print(
                        f"Information: "
                        f"{result['failure_reason']}"
                    )

            except Exception as error:

                print()
                print("CAMPAIGN PROCESSING ERROR")
                print(error)

                db.session.rollback()

    print()


def process_all():
    """
    Process every scheduled ChurchConnect task.
    """

    print()
    print("=" * 60)
    print("CHURCHCONNECT AUTOMATION PROCESSOR")
    print("=" * 60)

    process_due_reminders()
    process_due_campaigns()

    print()
    print("=" * 60)
    print("CHURCHCONNECT PROCESSOR FINISHED")
    print("=" * 60)
    print()


if __name__ == "__main__":

    app = create_app()

    with app.app_context():

        process_all()