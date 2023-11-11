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
        fields = 'leavetype','start_date','end_date','start_work_date'  # You can specify the fields you want to include if needed
        exclude = ['contract','hashed']

    def __init__(self, *args, **kwargs):
        super(RequestLeaveForm, self).__init__(*args, **kwargs)

        # Create a form helper and specify the layout
        self.helper = FormHelper()
        self.helper.layout = Layout(

            Row(
                Column('leavetype', css_class='col-md-6'),

            ),

            Row(
                Column('start_date', css_class='col-md-4'),
                Column('end_date', css_class='col-md-4'),
                Column('start_work_date', css_class='col-md-4'),

         
            ),

            Div(
                Button('cancel', 'Kansela', css_class='btn-secondary btn-sm', onclick="window.history.back();"),
                Submit('post', 'Submete', css_class='btn-primary btn-sm'),
            
                css_class='text-right',
            ),
        )

        # Add CSS classes to form fields if needed
        self.fields['leavetype'].widget.attrs['class'] = 'form-control'
        self.fields['start_date'].widget.input_type = 'date'
        self.fields['end_date'].widget.input_type = 'date'
        self.fields['start_work_date'].widget.input_type = 'date'
