from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from demTvDjango.demTV.models import UserProfile, Show, Day, TimeSlot, Vote
from demTvDjango.demTV.forms import ContactForm, UserForm, UserProfileForm, BaseShowFormSet
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.comments.views.comments import post_comment
from django.forms.models import modelformset_factory, inlineformset_factory
from time import localtime, gmtime, strftime
from JtvClient import JtvClient
from oauth import OAuthToken, OAuthError
from django.utils import simplejson
from django.core.mail import send_mail
from demTvDjango.settings import DEFAULT_JUSTINTV_EMAIL, DEFAULT_CONTACT_EMAIL, JTVKey, JTVSecret
from demTvDjango.demTV.parsers import SimpleParserSingle, SimpleParserMultiple, SimpleParserDict
import string
from random import Random
import facebook.djangofb as facebook
from facebookconnect.models import FacebookProfile
from django.template import RequestContext

# Create your views here.
@login_required
def profile(request):
    return user(request, request.user.username)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            profile = UserProfile(user=new_user, bio="", display_email=False, email_lineup=True)
            profile.save()
            return HttpResponseRedirect("/live/")
    else:
        form = UserCreationForm()
    return render_to_response("registration/register.html", {
        'baseUser': getAuthUser(request),
        'form': form,
    })

def user(request, user):
    user = get_object_or_404(User, username=user)
    shows = Show.objects.filter(owner=user)

    try:
        profile = user.get_profile()
    except UserProfile.DoesNotExist:
        profile = UserProfile(user=user, bio="", display_email=False, email_lineup=True)
        profile.save()

    return render_to_response('demTV/user.html', {
        'baseUser': getAuthUser(request),
        'user': user,
        'profile': profile,
        'shows': shows,
    }, context_instance=RequestContext(request))

@login_required
def editUser(request, username):
    if request.user.username != username:
        return render_to_response('demTV/error.html', {
            'baseUser': getAuthUser(request),
            'error': "You can't edit other user's profiles.",
        })

    user = User.objects.get(username=username)   
    profile = UserProfile.objects.get(user=user)

    result = None
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            result = "Profile updated successfully"
    else:
        user_form = UserForm(instance=user)
        profile_form = UserProfileForm(instance=profile)
    return render_to_response('demTV/manageUser.html', {
        'baseUser': getAuthUser(request),
        'user_form': user_form,
        'profile_form': profile_form,
        'result_message': result,
    })

"""
@facebook.require_login()
@login_required
def comment_post_wrapper(request):
    # Clean the request to prevent form spoofing
    if request.user.is_authenticated():
        if not (request.user.get_full_name() == request.POST['name'] or \
               request.user.email == request.POST['email']):
            return render_to_response('demTV/error.html', {
                'baseUser': getAuthUser(request),
                'error':"You registered user...trying to spoof a form...eh?",
            })
        return post_comment(request)
    return render_to_response('demTV/error.html', {
        'baseUser': getAuthUser(request),
        'error':"You anonymous cheater...trying to spoof a form?",
    })
"""

def show(request, show):
    show = get_object_or_404(Show, relative_url=show)
    isBroadcasting = False
    pubCode = None
    client = JtvClient(JTVKey, JTVSecret)
    login = show.jtv_login
    try:
        clips = client.get('/channel/clips/' + login + '.xml').read()
    except OAuthError:    
        clips = ""

    # Parse xml clips and get embed codes
    p = SimpleParserMultiple()
    try:
        p.feed(clips, 'embed_code')
    except(AttributeError):
        pass
    if p.data:
        episodes = p.data
    else:
        episodes = []

    if request.user.is_authenticated():
        curr = currentTimeSlot()
        if curr and (curr.last_week_winner == show) and (request.user == show.owner):
            isBroadcasting = True
            token = OAuthToken(show.jtv_token, show.jtv_secret)
            try:
                pubCode = client.get('/channel/publisher_embed.html', token).read() 
            except OAuthError:
                pass

    return render_to_response('demTV/show.html', {
        'baseUser': getAuthUser(request),
        'show': show,
        'episodes': episodes,
        'request': request,
        'minutes': getMinutes(),
        'seconds': getSeconds(),
        'isBroadcasting': isBroadcasting,
        'pubCode': pubCode,
    })

@login_required
def editShows(request, username):
    if request.user.username != username:
        return render_to_response('demTV/error.html', {
            'baseUser': getAuthUser(request),
            'error': "You can't edit other people's shows.",
        })

    ShowFormSet = inlineformset_factory(User, Show, formset=BaseShowFormSet, extra=1, fields=('name', 'description', 'time_slot'))
   
    try:
        user = User.objects.get(username=username)
    except(User.DoesNotExist):
        return render_to_response('demTV/error.html', {
            'baseUser': getAuthUser(request),
            'error': 'There is no such user.',
        })

    result = None
    if request.method == 'POST':
        formset = ShowFormSet(request.POST, request.FILES, instance=user)
        if formset.is_valid():
            forms = formset.save(commit=False)
            for form in forms:
                # Check if new show
                if not form.votes:
                    form.votes = 0
                    # Create jtv channel/login
                    login = "buriedtv_" + randomString()
                    password = randomString()
                    form.jtv_login = login
                    form.jtv_password = password
                    client = JtvClient(JTVKey, JTVSecret)
                    try:
                        channel = client.post('/channel/create.xml', {
                            'login': login,
                            'password': password,
                            'birthday': '1980-01-01',
                            'email': DEFAULT_JUSTINTV_EMAIL,
                            'category': 'None',
                            'title': form.name.lower(), 
                        }).read()
                    except OAuthError:
                        channel = ""                    

                    # Process returned channel credentials here 
                    # Parse xml clips into episodes
                    p = SimpleParserDict()
                    try:
                        p.feed(channel, ['access_token', 'access_token_secret'])
                    except(AttributeError):
                        pass 
                    if 'access_token' in p.data and 'access_token_secret' in p.data:
                        form.jtv_token = p.data['access_token']
                        form.jtv_secret = p.data['access_token_secret']
                    else:
                        result = "There was an error creating the new show. Please try again and make sure that the name is appropriate." 

                # Else if old show, check if timeslot changed. If so, reset votes
                else:
                    show = Show.objects.get(pk=form.pk)
                    if form.time_slot != show.time_slot:
                        form.votes = 0
                        Vote.objects.filter(show=show).delete()                   
                if not result:
                    form.owner = user
                    url = form.name.lower().replace(" ", "_")
                    form.relative_url = url
                    form.save()
 
            if not result:
                result = "Shows updated successfully"
                # Reset formset to display new one to user
                formset = ShowFormSet(instance=user)
    else: 
        formset = ShowFormSet(instance=user)
    return render_to_response('demTV/manageShow.html', {
        'baseUser': getAuthUser(request),
        'formset': formset,
        'result_message': result,
    })

@login_required
def timeslot(request, day, timeslot):

    result = None
    if request.method == 'POST':
        user = request.user

        show = None
        try:
            show = Show.objects.get(pk=request.POST['choice'])
        except (KeyError, Show.DoesNotExist):
            result = 'You must make a choice to vote.'
     
        # If a choice was made, continue
        if not result:
            timeslotObject = None
            try:    
                timeslotObject = TimeSlot.objects.get(military_time=timeslot, day=day)
            except(TimeSlot.DoesNotExist):
                pass

            # Check if user already voted for this timeslot
            try:
                vote = Vote.objects.get(timeslot=timeslotObject, user=user)
            except (Vote.DoesNotExist):
                vote = Vote()
                vote.user = user
                vote.timeslot = timeslotObject
                vote.show = show
                show.votes += 1
                show.save()
                vote.save()
                result = "Your vote has been registered"
            else:
                # Check if trying to vote for same show again
                if vote.show == show:
                    result = "You can't vote for a show twice."
                else:
                    # Subtract a vote from the old show
                    oldShow = vote.show
                    oldShow.votes -= 1
                    oldShow.save()

                    # Change vote's show and add a vote
                    vote.show = show
                    show.votes += 1
                    show.save()
                    vote.save()
                    result = "Your vote has been switched"

    timeslotObject = get_object_or_404(TimeSlot, military_time=timeslot, day=day)
    shows = Show.objects.filter(time_slot=timeslotObject).order_by('-votes')

    selected = -1
    try:
        selected = Vote.objects.get(timeslot=timeslotObject, user=request.user).show.pk
    except(Vote.DoesNotExist):
        pass

    return render_to_response('demTV/timeslot.html', {
        'baseUser': getAuthUser(request),
        'tabSelected': 'vote',
        'result': result,
        'dayPK': day,
        'timeslotPK': timeslot,
        'shows': shows,
        'selected': selected,
    })

def day(request, day):
    theDay = get_object_or_404(Day, pk=day)
    times = TimeSlot.objects.filter(day=theDay, enabled=1).order_by('military_time')
    return render_to_response('demTV/day.html', {
        'baseUser': getAuthUser(request),
        'tabSelected': 'vote',
        'day': theDay, 
        'times': times,
    })

def time(request):
    days = Day.objects.filter(enabled=1)
    return render_to_response('demTV/time.html', {
        'baseUser': getAuthUser(request),
        'tabSelected': 'vote',
        'days': days,
    })

def shows(request):
    shows = Show.objects.all().order_by('name')
    return render_to_response('demTV/shows.html', {
        'baseUser': getAuthUser(request),
        'tabSelected': 'shows',
        'shows': shows,
    })
    

def lineup(request):
    lineup = []
    timeSlots = TimeSlot.objects.filter(enabled=1).order_by('day', 'military_time')
    for timeSlot in timeSlots:
        winner = timeSlot.last_week_winner
        lineup.append({
            'timeslot': str(timeSlot),
            'show': winner,
        })
    
    return render_to_response('demTV/lineup.html', {
        'baseUser': getAuthUser(request),
        'tabSelected': 'lineup',
        'lineup': lineup,
    })

def live(request):
    timeslot = currentTimeSlot()
    embedCode = None
    
    if timeslot is not None:
        show = timeslot.last_week_winner
        client = JtvClient(JTVKey, JTVSecret)
        try:
            embedCode = client.get('/channel/embed/' + show.jtv_login + '?consumer_key=' + JTVKey + '&auto_play=true').read() 
        except OAuthError:
            embedCode = None

    return render_to_response('demTV/live.html', {
        'baseUser': getAuthUser(request),
        'tabSelected': 'live',
        'timeslot': timeslot,
        'minutes': getMinutes(),
        'seconds': getSeconds(),
        'embedCode': embedCode,
    })

def home(request):
    currTimeSlot = currentTimeSlot()
    currShow = None
    if currTimeSlot:
        currShow = currTimeSlot.last_week_winner

    topShows = Show.objects.all().order_by('-votes')[:5]

    return render_to_response('demTV/home.html', {
        'baseUser': getAuthUser(request),
        'tabSelected': 'home',
        'currShow': currShow,
        'topShows': topShows,
    }, context_instance=RequestContext(request))

# Static-y pages
def about(request):
   return render_to_response('demTV/about.html', {
        'baseUser': getAuthUser(request),
    }) 

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
	    subject = form.cleaned_data['subject']
	    message = form.cleaned_data['message']
	    your_email = form.cleaned_data['your_email']
	    recipients = [DEFAULT_CONTACT_EMAIL]
            body = "sender: " + your_email + "\n" + \
		   "subject: " + subject + "\n" + \
                   "message: " + message + "\n"

	    send_mail("Contact form", body, your_email, recipients)
	    return render_to_response("demTV/contact.html", {
		'baseUser': getAuthUser(request),
		'form': None,
                'result': "Your message has been sent. We will be in contact with you shortly.",
	    })
    else:
        form = ContactForm()
    return render_to_response("demTV/contact.html", {
        'baseUser': getAuthUser(request),
        'form': form,
    })

def jobs(request):
   return render_to_response('demTV/jobs.html', {
        'baseUser': getAuthUser(request),
    }) 

def press(request):
   return render_to_response('demTV/press.html', {
        'baseUser': getAuthUser(request),
    }) 

def privacy(request):
   return render_to_response('demTV/privacy.html', {
        'baseUser': getAuthUser(request),
    }) 

def xd_receiver(request):
    return render_to_response('xd_receiver.html')

# General functions for views
def currentTimeSlot():
    day = Day.objects.get(name=strftime("%A", localtime()))
    
    timeslot = None
    try:
        timeslot = TimeSlot.objects.get(day=day, military_time=strftime("%H", localtime()))
    except(TimeSlot.DoesNotExist):
        pass

    return timeslot

def getMinutes():
    return strftime("%M", localtime())

def getSeconds():
    return strftime("%S", localtime())

#Returns the authed user or none
def getAuthUser(request):
    if request.user.is_authenticated():
        # Check if facebook user
        try:
            if request.user.facebook_profile:
                return request.user.facebook_profile
        except (FacebookProfile.DoesNotExist, AttributeError):
            pass
        return request.user
    return None

# Returns random string for passwords, etc.
def randomString(length=16, chars=string.letters):
    return ''.join(Random().sample(chars, length))

