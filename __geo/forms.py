from django import forms
from __poll.constants import StatusChoices
from .models import Nation, Region, Constituency, Station


class NationForm(forms.Form):
    code = forms.CharField(required=True,
                           label="Two-Letter Code",
                           widget=forms.TextInput(attrs={
                                                          'class':'form-control',
                                                          'placeholder': 'enter nation two letter code',
                                                       })
                          )
    title = forms.CharField(required=True, label="Nation Name")

    def __init__(self, *args, **kwargs):
            super(NationForm, self).__init__(*args, **kwargs)
            text_attrs={
                "placeholder": "enter nation Name",
                "class": "form-control",
            }
            text_attrs["placeholder"] = "enter nation name"
            self.fields['title'].widget=forms.TextInput(attrs=text_attrs)


class RegionForm(forms.Form):
    title = forms.CharField(required=True, label="Region Name",
                            widget=forms.TextInput(attrs={
                                                          'class':'form-control',
                                                          'placeholder': 'enter region name',
                                                       })
                            )
    nation = forms.ModelChoiceField(label="Nation",
                                    queryset=Nation.objects.all(),
                                    widget=forms.Select(attrs={'class':'form-control'}))
    status = forms.ChoiceField(label="Status", choices=StatusChoices.choices,
                               widget=forms.Select(attrs={'class':'form-control'}))
    details = forms.CharField(required=False, label="Region Details",
                              widget=forms.Textarea(attrs={
                                                          'class':'form-control',
                                                          'placeholder': 'enter region details',
                                                       })
                              )


class ConstituencyForm(forms.Form):
    title = forms.CharField(required=True,
                            label="Constituency Title",
                              widget=forms.TextInput(attrs={
                                                            'class':'form-control',
                                                            'placeholder': 'enter constituency details',
                                                           }))
    region = forms.ModelChoiceField(label="Region",
                                    queryset=Region.objects.all(),
                                    widget=forms.Select(attrs={
                                        'class':'form-control',
                                        'placeholder': 'select region'
                                    }))
    status = forms.ChoiceField(label="Status", choices=StatusChoices.choices,
                               widget=forms.Select(attrs={'class':'form-control'}))
    details = forms.CharField(required=False,
                              label="Constituency Details",
                              widget=forms.Textarea(attrs={
                                                          'class':'form-control',
                                                          'placeholder': 'enter constituency details',
                                                       }))


class StationForm(forms.Form):
    code = forms.CharField(required=True,
                            label="Station Code",
                              widget=forms.TextInput(attrs={
                                                            'class':'form-control',
                                                            'placeholder': 'enter station code',
                                                           }))
    title = forms.CharField(required=True,
                            label="Station Title",
                            widget=forms.TextInput(attrs={
                                                            'class':'form-control',
                                                            'placeholder': 'enter station title',
                                                           }))
    constituency = forms.ModelChoiceField(required=False,
                                          label="Constituency",
                                          queryset=Constituency.objects.all(),
                                          widget=forms.Select(attrs={
                                            'class':'form-control',
                                            'placeholder': 'select constituency'
                                        }))
    status = forms.ChoiceField(required=False,
                               label="Status", choices=StatusChoices.choices,
                               widget=forms.Select(attrs={'class':'form-control'}))
    details = forms.CharField(required=False,
                              label="Station Details",
                              widget=forms.Textarea(attrs={
                                                          'class':'form-control',
                                                          'placeholder': 'enter station details',
                                                       }))
