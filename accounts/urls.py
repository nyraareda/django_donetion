from django.urls import path
from .views import *
from Home.views import *
from viewPage.views import *
urlpatterns = [
    path('verify/<str:key>/', verify, name='verify'),
    path('register/', user_create_form, name='user_create_form'),
    path('profile/<int:user_id>/', profile, name='profile'),
    path('add_additional_info/', add_additional_info, name='add_additional_info'),
    path('delete/<int:user_id>/', delete_account, name='delete_account'),
    path('edit/<int:user_id>/', edit_profile, name='edit_profile'),
    path('login/', login_view, name='login'),
   
    path('logout/<int:user_id>/', custom_logout, name='custom_logout'),
    path('password_reset/', request_password_reset, name='password_reset'),  # Password reset request view
    path('password_reset_confirm/<str:token>/', password_reset_confirm, name='password_reset_confirm'),  # Password reset confirmation view
    path('home/<int:user_id>/', home_profile, name='home_profile'),

    path('home/<int:user_id>/createproject/', create_project, name='create_project'),
    path('home/<int:user_id>/update/<int:pk>/', update_project, name='update_project'),

    path('home/<int:user_id>/project_detail/<int:project_id>/', project_detail, name='project_detail'),
    path('home/project/<int:project_id>/submit_comment/<int:user_id>/', submit_comment, name='submit_comment'),
    path('home/project/<int:project_id>/submit_reply/<int:user_id>/', submit_reply, name='submit_reply'),
    path('home/<int:user_id>/report_page/<int:project_id>/', report_page, name='report_page'),
    path('home/<int:user_id>/details/<int:project_id>' , ProjectDetails, name='project.detail'),
    # path('home/details/<int:project_id>' , ProjectDetail, name='project.details'),

    path('home/<int:user_id>/project/<int:project_id>/cancel_project/', cancel_project, name='cancel_project'),

    path('home/<int:user_id>/project/<int:project_id>/rate/<int:rating>/', rate, name='rate'),
    path('home/<int:user_id>/dashboard_user/project/<int:project_id>/', dashboard_user, name='dashboard_user'),
    path('home/<int:user_id>/project/<int:project_id>/add_donation/', add_donation, name='add_donation'),
    path('admin/login', login_view , name='login'),
    path('<int:user_id>/admin_dashboard/', admin_view, name='admin_view'),
    path('reset_pass_sent/', reset_pass_sent, name='reset_pass_sent'),
    path('admin/<int:user_id>/selected_project' , AdminSelectedProjects , name="select_project"),
    path('admin/<int:user_id>/delete_project/<int:project_id>/delete/', delete_project, name="delete_project"),

    path('admin/<int:user_id>/delete_category/<int:category_id>/delete/', DeleteCategory, name="category_delete"),
    path('admin/<int:user_id>/update_category/<int:category_id>/update/', Updatecategory, name="categroy_update"),
    path('home/<int:user_id>/createcategory/', CreateCategory, name='create_category'),
    path('home/<int:user_id>/similar-projects/<int:project_id>/<int:tag_id>',similar_projects, name='similar_projects'),

]
