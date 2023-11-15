from django import forms
from rekrutamentu.models import UserApplication, UserAttachment
from django.forms import inlineformset_factory
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Button, Div, Field
from leave.models import *


class RequestLeaveForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = 'category','leavetype','start_date','is_afternoon','end_date','start_work_date'  # You can specify the fields you want to include if needed
        exclude = ['contract']

    def __init__(self, *args, **kwargs):
        super(RequestLeaveForm, self).__init__(*args, **kwargs)

        # Create a form helper and specify the layout
        self.helper = FormHelper()
        self.helper.layout = Layout(

            Row(
                Column('category', css_class='col-md-6'),

            ),

            Row(
                Column('leavetype', css_class='col-md-6'),

            ),

            Row(
                Column('start_date', css_class='col-md-4'),
                Column('end_date', css_class='col-md-4'),
            ),

            Row(
                Column('is_afternoon', css_class='col-md-4'),
            ),

            Row(
                Column('start_work_date', css_class='col-md-4'),
            ),

            Div(
                Button('cancel', 'Kansela', css_class='btn-secondary btn-sm', onclick="window.history.back();"),
                Submit('post', 'Submete', css_class='btn-primary btn-sm'),
            
                css_class='text-right',
            ),
        )

        # Menambahkan class CSS ke field form jika diperlukan
        for field_name in ['category','leavetype', 'start_date', 'is_afternoon', 'end_date', 'start_work_date']:
            self.fields[field_name].widget.attrs['class'] = 'form-control'
            if field_name != 'category':
                self.fields[field_name].widget.attrs['disabled'] = 'disabled'
            if 'date' in field_name:
                self.fields[field_name].widget.input_type = 'date'


class LeaveRequestAproveForm(forms.ModelForm):
    class Meta:
        model = RequestLeaveAprove
        fields = ['description']

    def __init__(self, *args, **kwargs):
        super(LeaveRequestAproveForm, self).__init__(*args, **kwargs)

        # Create a form helper and specify the layout
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('description', css_class='col-md-12'),
            ),
            
            Div(
                Button('cancel', 'Kansela', css_class='btn-secondary btn-sm', onclick="window.history.back();"),
                Submit('post', 'Submete', css_class='btn-primary btn-sm'),
                css_class='text-right',
            ),
        )


        self.fields['description'].widget.attrs['class'] = 'form-control'