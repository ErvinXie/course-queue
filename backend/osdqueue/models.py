from django.db import models
from django.forms.models import model_to_dict
from django.utils import timezone


# Create your models here.
class user(models.Model):
    id = models.AutoField(primary_key=True)

    name = models.CharField(max_length=20, null=True, blank=True)

    # gender 1=male 0=female 2=others
    gender = models.IntegerField(null=True, blank=True)

    school_id = models.CharField(max_length=20, null=True, blank=True)

    class_id = models.CharField(max_length=20,null=True,blank=True)

    city = models.CharField(max_length=20, null=True, blank=True)

    province = models.CharField(max_length=20, null=True, blank=True)

    country = models.CharField(max_length=20, null=True, blank=True)

    # unique id for mini program
    open_id = models.CharField(max_length=50)

    status = models.IntegerField(default=0)

    avatar_url = models.URLField(null=True, blank=True)

    def role(self):
        roles = [
            'tourist',
            'student',
            'teacher',
            'admin'
        ]
        return roles[self.status]

    def get_dict(self, restricted=False):
        re = model_to_dict(self).copy()
        re['role'] = self.role()
        re.pop('status')
        # print(re)
        if restricted is True:
            re.pop('city')
            re.pop('province')
            re.pop('country')
            re.pop('open_id')

        return re

    def can_join_queue(self):
        if self.role() != 'tourist':
            return True
        else:
            return False


class queue(models.Model):
    id = models.AutoField(primary_key=True)

    name = models.CharField(max_length=1024, null=True, blank=True)

    create_time = models.DateTimeField(default=timezone.now)

    status = models.IntegerField(default=0)

    creator = models.ForeignKey(user,on_delete=models.CASCADE,null=True)

    def get_status(self):
        states = [
            'pending',
            'finished',
            'operating'
        ]
        return states[self.status]

    def get_dict(self):
        re = model_to_dict(self).copy()
        re['status'] = self.get_status()
        return re

    def was_operating(self):
        if self.get_status() == 'operating':
            return True
        else:
            return False


class relation(models.Model):
    id = models.AutoField(primary_key=True)

    queue = models.ForeignKey(queue, on_delete=models.CASCADE, null=True)

    user = models.ForeignKey(user, on_delete=models.CASCADE, null=True)

    status = models.IntegerField(default=0)

    create_time = models.DateTimeField(default=timezone.now)

    def which(self):
        roles = [
            'not related',
            'creator',
            'follower',
            'finished'
        ]
        return roles[self.status]

    def get_dict(self):
        re = model_to_dict(self)
        re['which'] = self.which()
        return re
