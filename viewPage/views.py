from django.shortcuts import render, get_object_or_404, redirect
from Home.models import Project, Comment, Report,Rating
from .forms import ProjectForm, CommentForm,ReportForm,ReplyForm
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.db.models import Avg
from Home.models import Project, Comment, Rating , Donation, Picture,Tag,User
from .forms import CommentForm, ReplyForm, ReportForm ,DonationForm
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .forms import ProjectForm, PictureForm, TagForm , CommentForm , ReportForm
from django.http import JsonResponse
from django.contrib import messages
from django.http import HttpResponseRedirect
# @transaction.atomic

def create_project(request, user_id ):
    user = get_object_or_404(User, pk=user_id)
    if user.is_active:
        if request.method == 'POST':
            form = ProjectForm(request.POST)
            picture_form = PictureForm(request.POST, request.FILES)
            if form.is_valid() and picture_form.is_valid():
                project = form.save(commit=False)
                project.created_by = user
                project.save()
                
                # Assign tags to the project
                tags = request.POST.getlist('tags')
                project.tags.set(tags) 
                
                # Save images associated with the project
                images = request.FILES.getlist('images')
                for image in images:
                    Picture.objects.create(project=project, image=image)
                    
                return HttpResponseRedirect(reverse('dashboard_user', kwargs={'project_id': project.pk, 'user_id': user_id}))

        else:
            form = ProjectForm()
            picture_form = PictureForm()
        return render(request, 'viewPage/create_project.html', {'form': form, 'picture_form': picture_form, 'user_id': user_id})
    else:
        return redirect('login')




@transaction.atomic

def update_project(request, pk, user_id):
    project = get_object_or_404(Project, pk=pk)
    user = get_object_or_404(User, pk=user_id)
    
    if user.is_active:
        if request.method == 'POST':
            form = ProjectForm(request.POST, instance=project)
            picture_form = PictureForm(request.POST, request.FILES, instance=project)
            
            if form.is_valid() and picture_form.is_valid():
                if request.FILES.getlist('new_images'):
                    project.images.all().delete()
                    for image in request.FILES.getlist('new_images'):
                        Picture.objects.create(project=project, image=image)
                
                form.save()
                picture_form.save()
                
                tags = request.POST.getlist('tags')
                project.tags.set(tags)
                project.category = form.cleaned_data['category']
                project.save()
                
                return HttpResponseRedirect(reverse('project_detail', kwargs={'project_id': pk, 'user_id': user_id}))
        else:
            form = ProjectForm(instance=project)
            picture_form = PictureForm(instance=project)

            all_tags = Tag.objects.all() 
            project_tags = project.tags.all()  
            project_images = project.images.all()
            
            return render(request, 'viewPage/update_project.html', {'form': form, 'picture_form': picture_form, 'project': project, 'all_tags': all_tags, 'project_tags': project_tags, 'project_images': project_images})
    else:
        return redirect('login')

@transaction.atomic
def add_picture(request):
    if request.method == 'POST':
        project_id = request.POST.get('project_id')
        project = get_object_or_404(Project, pk=project_id)
        
        # Get the list of uploaded files
        uploaded_files = request.FILES.getlist('images')
        
        # Iterate over the uploaded files
        for uploaded_file in uploaded_files:
            picture = Picture(project=project, image=uploaded_file)
            picture.save()
        
        # return redirect('/Crowdfund/create_tag/')
    else:
        picture_form = PictureForm()
    
    projects = Project.objects.all()  
    return render(request, 'viewPage/create_picture.html', {'picture_form': picture_form, 'projects': projects})



def create_tag(request):
    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            form.save()
            # return redirect('viewPage:home')  # Redirect to the home page after successful tag creation
    else:
        form = TagForm()
    return render(request, 'viewPage/tag_form.html', {'form': form})






def home(request):
    projects = Project.objects.all().prefetch_related('images')
    return render(request, 'viewPage/home.html', {'projects': projects})




def project_detail(request, project_id ,user_id ):
    project = get_object_or_404(Project, pk=project_id)
    user = get_object_or_404(User, pk=user_id)
    comments = project.comments.all().prefetch_related('replies')
    comment_form = CommentForm()
    reply_form = ReplyForm()
    
    return render(request, 'viewPage/project_detail.html', {
        'project': project,
        'comments': comments,
        'comment_form': comment_form,
        'reply_form': reply_form,
        'average_rating': project.calculate_average_rating(),
        'user_id':user.id

    })


@login_required
def render_comment_form(request, project_id):
    project = Project.objects.get(pk=project_id)
    return render(request, 'project_detail.html', {'project': project, 'user': request.user})

def submit_comment(request, project_id, user_id):
    project = get_object_or_404(Project, pk=project_id)
    user = get_object_or_404(User, pk=user_id) 

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.project = project
            new_comment.user = user 
            new_comment.save()
            return redirect('project_detail', project_id=project_id , user_id = user.id)
    else:
        comment_form = CommentForm()

    return redirect('project_detail', project_id=project_id ,user_id = user.id )


def submit_reply(request, project_id ,user_id):
    project = get_object_or_404(Project, pk=project_id)
    user = get_object_or_404(User, pk=user_id) 

    if request.method == 'POST':
        reply_form = ReplyForm(request.POST)
        
        if reply_form.is_valid():
            new_reply = reply_form.save(commit=False)
            comment_id = request.POST.get('comment_id')  
            new_reply.comment = get_object_or_404(Comment, pk=comment_id, project=project)
            new_reply.user = user
            new_reply.save()
            
    return redirect('submit_comment', project_id=project_id ,user_id =user.id)

# @login_required
def report_page(request, project_id, user_id):
    user = get_object_or_404(User, pk=user_id)
    project = get_object_or_404(Project, pk=project_id)
    report_form = ReportForm()

    if request.method == 'post':
        report_form = ReportForm(request.POST)
        if report_form.is_valid():
            new_report = report_form.save(commit=False)
            new_report.reported_item_id = request.POST.get('reported_item_id')  
            new_report.project = project
            new_report.user = user
            new_report.save()
            return HttpResponse("hhhhhhhhhhhhhh")  

    return render(request, 'viewPage/report_page.html', {'project_id': project_id, 'user_id': user.id, 'report_form': report_form})


def rate(request, rating, project_id, user_id):
    user = get_object_or_404(User, pk=user_id)
    project = get_object_or_404(Project, id=project_id)
    Rating.objects.update_or_create(project=project, user=user, value = rating, defaults={'value': rating})
    return JsonResponse({'success': True})

def index(request):
    projects = Project.objects.all()
    for project in projects:
        project.average_rating = project.calculate_average_rating()
        project.user_rating = project.get_user_rating(request.user)
    return render(request, "viewPage/home.html", {"projects": projects})



def dashboard_user(request, project_id, user_id):
    user = get_object_or_404(User, pk=user_id)
    project = get_object_or_404(Project, id=project_id)
    is_less_than_25_percent = project.current_fund <= 0.25 * project.total_target
    return render(request, 'viewPage/dashboard_user.html', { 'project_id': project_id, 'user_id': user.id, 'is_less_than_25_percent': is_less_than_25_percent})


def cancel_project(request, project_id ,user_id):
    project = get_object_or_404(Project, id=project_id)
    user = get_object_or_404(User, pk=user_id)
    if project.current_fund <= 0.25 * project.total_target:
        project.delete()  
        return redirect('viewPage:home')  
    else:
        return redirect('viewPage:project_detail', {'project_id':project_id, 'user_id': user.id})


def add_donation(request, project_id, user_id):
    project = get_object_or_404(Project, id=project_id)
    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            with transaction.atomic():
                donation = form.save(commit=False)
                donation.project = project

                remaining_amount = max(0, project.total_target - project.current_fund)

                if amount > remaining_amount:
                    excess_amount = amount - remaining_amount
                    donation.amount = remaining_amount
                    donation.save()

                    project.current_fund += remaining_amount
                    project.save()

                    messages.success(request, f'Great!! We Reached the goal. Excess amount of {excess_amount} will be returned to your wallet.')
                else:
                    project.current_fund += amount
                    project.save()

                    if project.current_fund >= project.total_target:
                        project.current_fund = project.total_target
                        return redirect('project_detail', project_id=project_id, user_id=user.id)
                    else:
                        messages.success(request, f'Donation of {amount} added successfully! Current fund: {project.current_fund}')

                donation.save()

            return redirect('add_donation', project_id=project_id, user_id=user.id)
    else:
        form = DonationForm()
    
    return render(request, 'viewPage/add_donation.html', {'form': form, 'project': project, 'project_id': project_id, 'user_id': user.id})



def similar_projects(request, project_id, user_id, tag_id):
    user = get_object_or_404(User, pk=user_id)
    current_project = get_object_or_404(Project, pk=project_id)
    tag = get_object_or_404(Tag, pk=tag_id)
    
    if current_project.tags.exists():
        tag_ids = current_project.tags.values_list('id', flat=True)
        similar_projects = Project.objects.filter(tags__id=tag_id).exclude(id=current_project.id).distinct()[:4]
    else:
        similar_projects = []
    return render(request, 'viewPage/similar_projects.html', {'similar_projects': similar_projects ,'project_id': project_id, 'user_id': user})