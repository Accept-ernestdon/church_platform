from datetime import datetime

from app.extensions import db
from app.models.reminder import Reminder
from app.models.member import Member
from app.models.message import Message
from app.services.sms_service import SMSService
from app.dashboard.routes import calculate_next_run


class ReminderService:

    @staticmethod
    def get_recipients(reminder):
        """
        Get the members who should receive this reminder.
        """

        query = db.select(Member).where(
            Member.church_id == reminder.church_id,
            Member.is_active.is_(True),
            Member.sms_opt_in.is_(True)
        )

        # Selected groups only
        if reminder.audience_type == "groups":

            selected_group_ids = [
                group.id for group in reminder.groups
            ]

            if not selected_group_ids:
                return []

            members = db.session.scalars(query).all()

            return [
                member
                for member in members
                if any(
                    group.id in selected_group_ids
                    for group in member.groups
                )
            ]

        # All active members who opted in
        return db.session.scalars(query).all()

    @staticmethod
    def process_reminder(reminder):
        """
        Process one reminder and update its scheduling information.

        Each SMS delivery attempt is also recorded in Message History.
        """

        if not reminder:
            return {
                "success": False,
                "message": "Reminder not found."
            }

        if not reminder.is_active:
            return {
                "success": False,
                "message": "Reminder is inactive."
            }

        members = ReminderService.get_recipients(reminder)

        sent_count = 0
        failed_count = 0

        # Send the reminder
        for member in members:

            if not member.phone:
                continue

            message_record = Message(
                church_id=reminder.church_id,
                member_id=member.id,
                recipient_phone=member.phone,
                message=reminder.message,
                channel="sms",
                source="reminder",
                source_id=reminder.id,
                status="pending"
            )

            db.session.add(message_record)
            db.session.flush()

            try:
                success = SMSService.send_sms(
                    member.phone,
                    reminder.message
                )

                if success:

                    sent_count += 1

                    message_record.status = "sent"
                    message_record.sent_at = datetime.utcnow()

                else:

                    failed_count += 1

                    message_record.status = "failed"
                    message_record.failure_reason = (
                        "SMS provider rejected the message."
                    )

            except Exception as error:

                failed_count += 1

                message_record.status = "failed"
                message_record.failure_reason = str(error)

        # Record this run
        run_time = datetime.utcnow()

        reminder.last_run_at = run_time
        reminder.total_sent += sent_count

        # One-time reminder
        if reminder.recurrence_type == "one_time":

            reminder.status = "completed"
            reminder.is_active = False
            reminder.next_run_at = None
            reminder.sent_at = run_time

        # Recurring reminder
        else:

            current_run = (
                reminder.next_run_at
                or reminder.scheduled_at
            )

            next_run = calculate_next_run(
                scheduled_at=current_run,
                recurrence_type=reminder.recurrence_type,
                recurrence_interval=reminder.recurrence_interval
            )

            # Check whether the recurrence has reached its end date
            if (
                next_run is None
                or (
                    reminder.recurrence_end_date
                    and next_run > reminder.recurrence_end_date
                )
            ):

                reminder.status = "completed"
                reminder.is_active = False
                reminder.next_run_at = None
                reminder.sent_at = run_time

            else:

                reminder.status = "scheduled"
                reminder.is_active = True
                reminder.next_run_at = next_run

        db.session.commit()

        return {
            "success": True,
            "sent": sent_count,
            "failed": failed_count,
            "status": reminder.status,
            "next_run_at": reminder.next_run_at
        }