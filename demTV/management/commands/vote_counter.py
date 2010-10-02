from django.core.management.base import NoArgsCommand
from demTvDjango.demTV.models import TimeSlot, Show, Vote, UserProfile
from django.contrib.auth.models import User
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mass_mail

class Command(NoArgsCommand):
    help = """
        Determines which show has most votes in each enabled timeslot.
        Sets this show as last_week_winner for those timeslots.
        Sends email to owners of those shows notifying them.
        Sends email to all users with new lineup.
    """

    def handle_noargs(self, **options):
        lineup = []
        allTimeSlots = TimeSlot.objects.filter(enabled=True).order_by('day').order_by('military_time')
        for timeslot in allTimeSlots:
             shows = Show.objects.filter(time_slot=timeslot).order_by('pk')
             top_show = Command.getTopShow(shows)
             if not top_show:
                 continue
             timeslot.last_week_winner = top_show
             timeslot.save()

             ctx_dict = { 'user': top_show.owner,
                          'show': top_show,
                          'timeslot': timeslot,
                        }
             subject = render_to_string('demTV/winner_email_subject.txt',
                                   ctx_dict)
             # Email subject *must not* contain newlines
             subject = ''.join(subject.splitlines())
        
             message = render_to_string('demTV/winner_email.txt',
                                   ctx_dict)
        
             top_show.owner.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)
            
             lineup.append(timeslot)
        # Send lineup to user
        Command.send_lineup_emails(lineup)

        # Clear votes for all shows
        shows = Show.objects.all()
        for show in shows:
            show.votes = 0
            show.save()

        # Clear all vote records
        Vote.objects.all().clear().delete()

    @staticmethod
    def getTopShow(shows):
        if shows:
            top_show = shows[0]
        else:
            return None
        
        for show in shows:
            if show.votes > top_show.votes:
                top_show = show
        return top_show


    @staticmethod
    def send_lineup_emails(lineup):
         if not lineup:
             return
 
         ctx_dict = { 'lineup': lineup,
                    }
         subject = render_to_string('demTV/lineup_email_subject.txt',
                               ctx_dict)
         # Email subject *must not* contain newlines
         subject = ''.join(subject.splitlines())

         message = render_to_string('demTV/lineup_email.txt',
                               ctx_dict)

         recipients = UserProfile.objects.filter(email_lineup=True)
         mails = (
             (
                 subject,
                 message,
                 settings.DEFAULT_FROM_EMAIL,
                 [u.user.email]
             ) for u in recipients
         )
         send_mass_mail(mails, fail_silently=True)
        
