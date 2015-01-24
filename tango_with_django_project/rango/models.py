from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    # unique cannot be set to true in the beginning otherwise migrations won't run
    # http://stackoverflow.com/questions/27788456/integrityerror-column-slug-is-not-unique
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name


class Page(models.Model):
    # There is also a DateField
    category = models.ForeignKey(Category)
    title = models.CharField(max_length=128)
    url = models.URLField()
    views = models.IntegerField(default=0)

    def __unicode__(self):
        return self.title


class UserProfile(models.Model):
    # Required to link a UserProfile to a User model (which comes with Django)
    # One to One relation instead of inheritance -> better this way
    user = models.OneToOneField(User)

    # Additional attributes we wish to include
    website = models.URLField(blank=True)
    picture = models.ImageField(upload_to='profile_images', blank=True)

    # Override unicode to return something useful
    def __unicode__(self):
        return self.user.username

