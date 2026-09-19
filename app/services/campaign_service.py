from datetime import datetime

from app.extensions import db
from app.models.campaign import Campaign
from app.models.member import Member
from app.models.message import Message
from app.services.sms_service import SMSService


class CampaignService:
    """
    Handles campaign recipient selection, SMS delivery,
    and message history recording.
    """

    @staticmethod
    def get_recipients(campaign):
        """
        Recalculate the campaign audience at send time.

        This is intentional:
        members may have been added, removed, deactivated,
        or opted out after the campaign was created.
        """

        if campaign.audience_type == "all":

            return db.session.scalars(
                db.select(Member)
                .where(
                    Member.church_id == campaign.church_id,
                    Member.is_active.is_(True),
                    Member.sms_opt_in.is_(True)
                )
                .order_by(Member.id.asc())
            ).all()

        recipient_ids = set()

        for group in campaign.groups:

            if not group.is_active:
                continue

            for member in group.members:

                if (
                    member.church_id == campaign.church_id
                    and member.is_active
                    and member.sms_opt_in
                ):
                    recipient_ids.add(member.id)

        if not recipient_ids:
            return []

        return db.session.scalars(
            db.select(Member)
            .where(
                Member.church_id == campaign.church_id,
                Member.id.in_(recipient_ids),
                Member.is_active.is_(True),
                Member.sms_opt_in.is_(True)
            )
            .order_by(Member.id.asc())
        ).all()

    @staticmethod
    def process_campaign(campaign):
        """
        Send a campaign immediately.

        Every recipient gets an individual Message history record.

        Returns a result dictionary containing:
        - sent
        - failed
        - total
        - status
        - failure_reason
        """

        # -------------------------------------------------
        # SAFETY CHECK
        # -------------------------------------------------

        if campaign.status == "sending":

            return {
                "sent": campaign.total_sent,
                "failed": campaign.total_failed,
                "total": campaign.total_recipients,
                "status": "sending",
                "failure_reason": (
                    "This campaign is already being processed."
                )
            }

        if campaign.status == "sent":

            return {
                "sent": campaign.total_sent,
                "failed": campaign.total_failed,
                "total": campaign.total_recipients,
                "status": "sent",
                "failure_reason": (
                    "This campaign has already been sent."
                )
            }

        if not campaign.is_active:

            return {
                "sent": 0,
                "failed": 0,
                "total": 0,
                "status": "failed",
                "failure_reason": (
                    "This campaign is inactive."
                )
            }

        # -------------------------------------------------
        # CHANNEL CHECK
        # -------------------------------------------------

        if campaign.channel != "sms":

            campaign.status = "failed"
            campaign.failure_reason = (
                "Only SMS campaigns are currently supported."
            )

            db.session.commit()

            return {
                "sent": 0,
                "failed": 0,
                "total": 0,
                "status": "failed",
                "failure_reason": campaign.failure_reason
            }

        # -------------------------------------------------
        # MARK AS SENDING BEFORE API CALLS
        # -------------------------------------------------

        campaign.status = "sending"
        campaign.failure_reason = None
        campaign.sent_at = None

        db.session.commit()

        # -------------------------------------------------
        # RECALCULATE RECIPIENTS
        # -------------------------------------------------

        recipients = CampaignService.get_recipients(campaign)

        campaign.total_recipients = len(recipients)
        campaign.total_sent = 0
        campaign.total_failed = 0

        db.session.commit()

        # -------------------------------------------------
        # NO RECIPIENTS
        # -------------------------------------------------

        if not recipients:

            campaign.status = "failed"
            campaign.failure_reason = (
                "No eligible SMS recipients were found."
            )

            db.session.commit()

            return {
                "sent": 0,
                "failed": 0,
                "total": 0,
                "status": "failed",
                "failure_reason": campaign.failure_reason
            }

        # -------------------------------------------------
        # SEND SMS
        # -------------------------------------------------

        sent = 0
        failed = 0
        failures = []

        for member in recipients:

            # Create message history record first.
            message_record = Message(
                church_id=campaign.church_id,
                member_id=member.id,
                recipient_phone=member.phone,
                message=campaign.message,
                channel="sms",
                source="campaign",
                source_id=campaign.id,
                status="pending"
            )

            db.session.add(message_record)
            db.session.flush()

            try:

                success = SMSService.send_sms(
                    member.phone,
                    campaign.message
                )

                if success:

                    sent += 1

                    message_record.status = "sent"
                    message_record.sent_at = datetime.utcnow()

                else:

                    failed += 1

                    message_record.status = "failed"
                    message_record.failure_reason = (
                        "SMS provider rejected the message."
                    )

                    failures.append(
                        f"{member.name}: SMS provider rejected "
                        f"the message."
                    )

            except Exception as error:

                failed += 1

                message_record.status = "failed"
                message_record.failure_reason = str(error)

                failures.append(
                    f"{member.name}: {str(error)}"
                )

            # Save message history and campaign progress
            # after every recipient.
            campaign.total_sent = sent
            campaign.total_failed = failed

            db.session.commit()

        # -------------------------------------------------
        # FINAL STATUS
        # -------------------------------------------------

        campaign.total_sent = sent
        campaign.total_failed = failed
        campaign.sent_at = datetime.utcnow()

        if failed == 0:

            campaign.status = "sent"
            campaign.failure_reason = None

        elif sent > 0:

            campaign.status = "sent"

            campaign.failure_reason = (
                f"{failed} recipient(s) failed to receive the "
                f"campaign."
            )

        else:

            campaign.status = "failed"

            campaign.failure_reason = (
                "; ".join(failures)
                if failures
                else "All recipients failed."
            )

        db.session.commit()

        return {
            "sent": sent,
            "failed": failed,
            "total": len(recipients),
            "status": campaign.status,
            "failure_reason": campaign.failure_reason
        }