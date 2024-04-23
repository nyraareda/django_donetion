from django import forms
from Home.models import  Picture, Project, Comment,Report,Reply , Donation,Category,Tag
from django.contrib.admin.widgets import FilteredSelectMultiple
from Home.models import Project
from django.contrib.admin.widgets import FilteredSelectMultiple
from Home.models import Project,Picture,Tag,Category
from django.forms.models import inlineformset_factory


class ProjectForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label=None, widget=forms.RadioSelect)
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.all(), widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Project
        fields = ['title', 'details', 'current_fund', 'total_target', 'start_date', 'end_date', 'category', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter project title'}),
            'details': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter project details'}),
            'current_fund': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter current fund'}),
            'total_target': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter total target'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def clean_current_fund(self):
        current_fund = self.cleaned_data['current_fund']
        if current_fund < 0:
            raise forms.ValidationError("Current fund cannot be negative.")
        return current_fund

    def clean_total_target(self):
        total_target = self.cleaned_data['total_target']
        if total_target < 0:
            raise forms.ValidationError("Total target cannot be negative.")
        return total_target

class PictureForm(forms.ModelForm):
    class Meta:
        model = Picture
        fields = ['image', 'caption']
        widgets = {
            'image': forms.ClearableFileInput(),
        }
PictureFormSet = inlineformset_factory(Project, Picture, fields=('image', 'caption'), extra=1, max_num=5, widgets={'image': forms.ClearableFileInput()})


        
class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name']


class Meta:
        model = Project
        fields = '__all__'
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ['content']
        widgets = {
            'comment': forms.HiddenInput(),
        }
        
class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['reported_item_id', 'report_type', 'reason']




class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ['amount']