from django.urls import path
from Home.views import  *
urlpatterns = [
    path('', admin_view, name='admin'),
    path('create_category/' , CreateCategory , name='create.category'),
    path('selected_project/', AdminSelectedProjects, name='select_project'),
    path('updateCategory/<int:id>' , Updatecategory , name='update.category'),
    path('deleteCategory/<int:id>', DeleteCategory, name='delete.category'),
    


]