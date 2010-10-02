from django import forms
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    bio = models.CharField(max_length=200)
    display_email = models.BooleanField()
    email_lineup = models.BooleanField("Email weekly lineup")
    
    def __unicode__(self):
        return self.user.username + " profile"

class Show(models.Model):
    name = models.CharField(max_length=20, unique=True)
    # The relative url used for the show. Not the full url.
    relative_url = models.CharField(max_length=20, unique=True)
    owner = models.ForeignKey(User)
    description = models.CharField(max_length=200)
    time_slot = models.ForeignKey('TimeSlot')
    votes = models.IntegerField()

    # JustinTV data
    jtv_login = models.CharField(max_length=50)
    jtv_password = models.CharField(max_length=50)
    jtv_token = models.CharField(max_length=50)
    jtv_secret = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

class Day(models.Model):
    name = models.CharField(max_length=20)
    enabled = models.BooleanField()

    def __unicode__(self):
        return self.name

class TimeSlot(models.Model):
    day = models.ForeignKey(Day)
    military_time = models.DecimalField(max_digits=3, decimal_places=1)
    last_week_winner = models.ForeignKey('Show')
    last_week_winner.null = True
    last_week_winner.blank = True

    # This is in now way dependent on the day enabled bit 
    enabled = models.BooleanField()

    def getTime(self):
	newTime = self.military_time
        ext = "AM"
        if self.military_time >= 13:
            newTime -= 12
            ext = "PM"

        if self.military_time != self.military_time.to_integral_value():
            ext = ":30" + ext
        else:
            ext = ":00" + ext

        return str(newTime.to_integral_value()) + ext
    
    def delete(self):
        """
        Override default model method so day, shows don't get deleted.
        """
        self.day.clear()
        self.last_week_winner.clear()
        super(TimeSlot, self).delete()
    
    def __unicode__(self):
        return self.day.name + "@" + self.getTime() + " CST"
   
 
class Vote(models.Model):
    timeslot = models.ForeignKey(TimeSlot)
    user = models.ForeignKey(User)
    show = models.ForeignKey(Show)

    def delete(self):
        """
        Override default model method so shows, users, timeslots don't get deleted.
        """
        self.timeslot.clear()
        self.user.clear()
        self.show.clear()
        super(Vote, self).delete()

    def __unicode__(self):
        return self.user.username + " voted for " + self.show.name
