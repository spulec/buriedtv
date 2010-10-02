from django.core.management.base import NoArgsCommand
from demTvDjango.demTV.models import TimeSlot, Show, Day
from django.contrib.auth.models import User
from demTvDjango.demTV.JtvClient import JtvClient
from settings import JTVKey, JTVSecret
from datetime import datetime, date
import time
from demTvDjango.demTV.parsers import SimpleParserSingle
from time import strftime, localtime
from demTvDjango.demTV.oauth import OAuthToken
from django.core.mail import mail_admins

class Command(NoArgsCommand):
    help = """
        Makes clips out of any shows that aired today.
    """
    
    def handle_noargs(self, **options):
            client = JtvClient(JTVKey, JTVSecret)
            day = Day.objects.get(name=strftime("%A", localtime()))
            try:
                timeslots = TimeSlot.objects.filter(day=day)
            except(TimeSlot.DoesNotExist):
                print "No timeslots found for this day"
                return
            clip_errors = []
            for timeslot in timeslots:
                # Get a current datetime
                day = date.today()
                # Change the time portion for the episode
                start = datetime(day.year, day.month, day.day, timeslot.military_time)
                end = datetime(day.year, day.month, day.day, timeslot.military_time + 1)

                # Convert to epoch time
                start_time = time.mktime(start.timetuple())
                end_time = time.mktime(end.timetuple())

                show = timeslot.last_week_winner

                #Change this to use the shows credentials
                token = OAuthToken(show.jtv_token, show.jtv_secret)
                clip = client.post('/clip/create.xml', {
                    'start_time': start_time,
                    'end_time': end_time,
                    'title': show.name,
                    'description': str(date.today()),
                    'tags': "woot",
                }, token).read()

                print clip 
                # Parse response to confirm success
                p = SimpleParserSingle()
                p.feed(clip, 'id')
                if not p.data:
                    clip_errors.append("Timeslot:" + str(timeslot) + ";Show:" + show.name)
                
            # Sends email if any errors
            if clip_errors:
                mail_admins("Error creating clips", str(clip_errors))                         


