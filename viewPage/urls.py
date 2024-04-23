from django.urls import path
from .views import home, project_detail, report_page, submit_comment, submit_reply,rate,dashboard_user,add_donation,create_project, update_project,add_picture,create_tag

app_name = 'viewPage'

urlpatterns = [
    # path('', home, name='home'),
    # path('project/<int:project_id>/', project_detail, name='project_detail'),
    # path('project/<int:project_id>/submit_comment/', submit_comment, name='submit_comment'),
    # path('project/<int:project_id>/submit_reply/', submit_reply, name='submit_reply'),
    # path('report/', report_page, name='report_page'),
    # path('project/<int:project_id>/rate/<int:rating>/', rate, name='rate'),
    # path('dashboard_user/project/<int:project_id>/', dashboard_user, name='dashboard_user'),
    # path('project/<int:project_id>/add_donation/', add_donation, name='add_donation'),
    # path('create/', create_project, name='create_project'),  
    # path('update/<int:pk>/', update_project, name='update_project'),
    # path('add_picture/', add_picture, name='add_picture'),
    # path('create_tag/', create_tag, name='create_tag'),
    # path('create_project/<int:user_id>/', create_project, name='create_project'),


]
