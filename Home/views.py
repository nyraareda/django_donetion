from django.shortcuts import render, redirect
from .models import Category , Project  ,Rating 
from .forms import CategoryForm , SelectedProjectForm
from django.db.models import Q
from django.db.models import Max , F
from django.shortcuts import get_object_or_404 ,render
from Home.models import User
from django.utils import timezone
    # five_latest_project = Project.objects.order_by('-created_at')[:5]
# def home_profile(request , id):
#     user = get_object_or_404(User, id=id)
#     return render(request, 'home/index.html', {'user': user})

def home_profile(request, user_id):
    projects = Project.objects.filter(is_deleted=False, created_at__lte=timezone.now()).order_by('-created_at')[:5]
    projects = projects.prefetch_related('tags')
    categories = Category.objects.all()
    category_id = request.GET.get('category')
    search_query = request.GET.get('search')
    allProject = Project.objects.all()
    allProject = allProject.prefetch_related('tags')

    top_rated_project_ids = (
        Rating.objects
        .values('project_id')
        .annotate(max_value=Max('value'))
        .order_by('-max_value')[:5]
    )

    latest_created_at_dict = {}
    for item in top_rated_project_ids:
        latest_created_at_dict[item['project_id']] = Rating.objects.filter(project_id=item['project_id']).aggregate(latest_created_at=Max('created_at'))['latest_created_at']

    top_rated_projects_ids = [project_id for project_id, latest_created_at in latest_created_at_dict.items()]
    top_rated_projects = Project.objects.filter(id__in=top_rated_projects_ids)

    if category_id:
        allProject = allProject.filter(category_id=category_id)
    if search_query:
        allProject = allProject.filter(
            Q(title__icontains=search_query) | 
            Q(tags__name__icontains=search_query)  
        ).distinct()

    for project in projects:
        if project.total_target != 0:
            project.progress_percentage = int((project.current_fund / project.total_target) * 100)
        else:
            project.progress_percentage = 0

    selected_projects = Project.objects.filter(selected_by_admin=True)

    if user_id:
        user_name = get_object_or_404(User, id=user_id)
        if user_name.is_activated:
            for project in top_rated_projects:
                try:
                    project.creator_username = User.objects.get(id=project.created_by_id).first_name 
                except User.DoesNotExist:
                    project.creator_username = "Unknown"
            return render(request, 'home/index.html', {'user_name': user_name ,'user_id':user_id,'projects' :projects , 'categories':categories , 'selected_projects':selected_projects, 'search_query':search_query,'allProject': allProject ,"top_rated_projects":top_rated_projects})
        else:
            return render(request, 'accounts/not_activated.html')



def Home(request):
    projects = Project.objects.filter(is_deleted=False, created_at__lte=timezone.now()).order_by('-created_at')[:5]
    projects = projects.prefetch_related('tags')
    categories = Category.objects.all()
    category_id = request.GET.get('category')
    search_query = request.GET.get('search')
    allProject = Project.objects.all()
    allProject = allProject.prefetch_related('tags')

    top_rated_project_ids = (
        Rating.objects
        .values('project_id')
        .annotate(max_value=Max('value'))
        .order_by('-max_value')[:5]
    )

    latest_created_at_dict = {}
    for item in top_rated_project_ids:
        latest_created_at_dict[item['project_id']] = Rating.objects.filter(project_id=item['project_id']).aggregate(latest_created_at=Max('created_at'))['latest_created_at']

    top_rated_projects_ids = [project_id for project_id, latest_created_at in latest_created_at_dict.items()]
    top_rated_projects = Project.objects.filter(id__in=top_rated_projects_ids)

    if category_id:
        allProject = allProject.filter(category_id=category_id)
    if search_query:
        allProject = allProject.filter(
            Q(title__icontains=search_query) | 
            Q(tags__name__icontains=search_query)  
        ).distinct()

    for project in projects:
        if project.total_target != 0:
            project.progress_percentage = int((project.current_fund / project.total_target) * 100)
        else:
            project.progress_percentage = 0

    selected_projects = Project.objects.filter(selected_by_admin=True)

    return render(request, 'home/index.html' ,{'projects' :projects , 'categories':categories , 'selected_projects':selected_projects, 'search_query':search_query,'allProject': allProject,"top_rated_projects":top_rated_projects})


def admin_view(request,user_id):
    projects = Project.objects.all()
    categories = Category.objects.all()
    user = get_object_or_404(User, id=user_id)
    return render(request, 'home/admin.html', {'projects': projects, 'categories': categories ,'user':user})

def CreateCategory(request ,user_id):
    categories = Category.objects.all()
    form = CategoryForm(request.POST or None)
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST' and request.POST.get('view_type') == 'add_category':
        if form.is_valid():
            form.save()
            return redirect('admin_view', user_id=user_id)
           
    return render(request, 'home/createcategory.html', {'categories': categories, 'form': form ,'user':user})


def AdminSelectedProjects(request ,user_id ):
    projects = Project.objects.all()
    form = SelectedProjectForm(request.POST or None)

    if request.method == 'POST' and request.POST.get('view_type') == 'select_projects':
        if form.is_valid():
            Project.objects.update(selected_by_admin=False)
            selected_projects = form.cleaned_data['selected_projects'][:5]
            for project in selected_projects:
                project.selected_by_admin = True
                project.save()
            return redirect('admin_view' ,user_id=user_id)  

    return render(request, 'home/selectproject.html', {'projects': projects, 'form': form ,'user_id':user_id})

def ProjectDetails(request, project_id ,user_id):
    project = get_object_or_404(Project, id=project_id)
    user = get_object_or_404(User, id=user_id)

    if project.total_target != 0:
            project.progress_percentage = int((project.current_fund / project.total_target) * 100)
    else:
            project.progress_percentage = 0
    return render(request, 'home/show.html', {'project': project, 'user_id':user_id, "project_id": project_id })


# def ProjectDetail(request, project_id ):
#     project = get_object_or_404(Project, id=project_id)
    
#     if project.total_target != 0:
#             project.progress_percentage = int((project.current_fund / project.total_target) * 100)
#     else:
#             project.progress_percentage = 0
#     return render(request, 'home/show.html', {'project': project,  "project_id": project_id})

def delete_project(request, project_id, user_id):
    project = get_object_or_404(Project, pk=project_id)
    project.delete()
    return redirect('admin_view', user_id=user_id)


def Updatecategory(request, user_id , category_id ):
    category_item = get_object_or_404(Category, id=category_id)
    form = CategoryForm(instance=category_item)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category_item)
        if form.is_valid():
            form.save()
            return redirect('admin_view', user_id=user_id)
    return render(request, 'home/categoryUpdate.html', {'form': form})

def DeleteCategory(request, user_id , category_id):
    category_item = get_object_or_404(Category, id=category_id)
    category_item.delete()
    return redirect('admin_view', user_id=user_id)