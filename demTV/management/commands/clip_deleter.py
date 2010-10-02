from django.core.management import BaseCommand
from demTvDjango.demTV.models import TimeSlot, Show, Day
from demTvDjango.demTV.JtvClient import JtvClient
from settings import JTVKey, JTVSecret
from demTvDjango.demTV.parsers import SimpleParserSingle
from demTvDjango.demTV.oauth import OAuthToken


class Command(BaseCommand):
    help = """
        Deletes the clip with show and id given as the argument.
    """
   
    args = "The show and id of the clip to delete"
 
    def handle(self, show, clip_id, **options):
            client = JtvClient(JTVKey, JTVSecret)
            clip_show = Show.objects.get(name=show)
            token = OAuthToken(clip_show.jtv_token, clip_show.jtv_secret)
            response = client.post('/clip/destroy/' + clip_id + '.xml', {}, token ).read()
            
            # Parse response to confirm success
            p = SimpleParserSingle()
            p.feed(response, 'message')
            print p.data

