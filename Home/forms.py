from django import forms
from Home.models import Category , Project



class CategoryForm(forms.ModelForm):
  
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_name(self):
        name = self.cleaned_data['name']
        if not name:
            raise forms.ValidationError("Category name cannot be empty.")
        if Category.objects.filter(name=name).exists():
            raise forms.ValidationError("Category name must be unique.")
        if name and len(name) > 50:  
            raise forms.ValidationError("Category name must be less than 50 characters.")
        if any(char.isdigit() for char in name):
            raise forms.ValidationError("Category name cannot contain numbers.")
        if Category.objects.filter(name=name).exists():
                forms.ValidationError('name', 'Category with this name already exists.')
        return name

   

class SelectedProjectForm(forms.Form):
    selected_projects = forms.ModelMultipleChoiceField(
        queryset=Project.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )   