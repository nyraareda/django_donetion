from django.contrib import admin
from Home.models import Picture, Project, Comment, Reply, Tag, Category
from .forms import ProjectForm

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    form = ProjectForm

admin.site.register(Picture)
admin.site.register(Comment)
admin.site.register(Reply)
admin.site.register(Tag)
admin.site.register(Category)