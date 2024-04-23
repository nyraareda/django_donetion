from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse, get_object_or_404
from django.db.models import Avg
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils import timezone
class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True)  
    email = models.EmailField(unique=True)  
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='users/images', null=True, blank=True)
    facebook_profile = models.URLField(max_length=200, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    is_activated = models.BooleanField(default=False)
    activation_key = models.CharField(max_length=64, blank=True)
    reset_token = models.CharField(max_length=100, blank=True, null=True)

    # Add related_name attributes to resolve clashes
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='user_groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='user_permissions_set'
    )

    def save(self, *args, **kwargs):
        if not self.username:
            raise ValidationError("Username cannot be empty.")
        if not self.email:
            raise ValidationError("Email cannot be empty.")
        super().save(*args, **kwargs)

    @property
    def profile_picture_url(self):
        if self.profile_picture:
            return self.profile_picture.url
        return '/path/to/default/profile/picture.jpg'


class Picture(models.Model):
    image = models.ImageField(upload_to='media/project_images/', default='default_image.jpg')
    caption = models.CharField(max_length=255, blank=True, null=True)
    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='images')

    def __str__(self):
        return self.caption or str(self.id)

    class Meta:
        app_label = 'Home'

    def str(self):
        return self.image.name
    

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.title}'
    @property
    def update_url(self):
        url = reverse('categoru.update', args=[self.id])
        return url
    @property
    def delete_url(self):
        url = reverse('category.delete', args=[self.id])
        return url

class Tag(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name

class Project(models.Model):
    title = models.CharField(max_length=255)
    details = models.TextField()
    current_fund = models.BigIntegerField(null=True, default=0)
    total_target = models.BigIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, default=None)
    tags = models.ManyToManyField(Tag, blank=True, related_name="projects")
    is_deleted = models.BooleanField(default=False)
    selected_by_admin = models.BooleanField(default=False)  
    created_at = models.DateTimeField(default=timezone.now) 
    def __str__(self):
        return self.title
    

    def get_image_urls(self):
        return [image.image.url for image in self.images.all()]

    @classmethod
    def get_project_by_id(cls, id):
        return get_object_or_404(cls, id=id)

    @property
    def image_url(self):
        picture = self.images.first()
        if picture:
            return picture.image.url

    def calculate_average_rating(self):
        ratings = Rating.objects.filter(project=self)
        if ratings.exists():
            return ratings.aggregate(Avg("value"))["value__avg"]
        else:
            return 0

    def get_user_rating(self, user):
        try:
            rating = Rating.objects.get(project=self, user=user)
            return rating.value
        except Rating.DoesNotExist:
            return None

    def cancel_project(self):
        if self.current_fund <= 0.25 * self.total_target:
            self.is_deleted = True
            self.save()
            
class Comment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Reply(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Report(models.Model):
    PROJECT = 'PR'
    COMMENT = 'CM'
    REPORT_CHOICES = [
        (PROJECT, 'Project'),
        (COMMENT, 'Comment')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reported_item_id = models.PositiveIntegerField()
    report_type = models.CharField(max_length=2, choices=REPORT_CHOICES)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)  
    value = models.IntegerField()
    rate_date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(default=timezone.now) 



    class Meta:
        unique_together = ('project', 'user')

    def __str__(self):
        return f"{self.project.title}: {self.value}"

class Donation(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, default=None)
    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='donations')
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Amount of the donation

    def __str__(self):
        return f"Donation #{self.id}"
