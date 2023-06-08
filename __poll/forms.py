from django import forms
from django.utils.translation import gettext_lazy as _
from __poll.constants import StatusChoices
from __geo.models import Station, Constituency, Nation
from __people.models import Candidate
from __poll.utils.utils import get_zone_ct


class EventForm(forms.Form):
    code = forms.CharField(required=True)
    title = forms.CharField(required=True)
    agent = forms.CharField(required=True)

class OfficeForm(forms.Form):
    nation_ct = None
    nation_ct = get_zone_ct(Nation, False)
    if nation_ct is not None:
        nation_ct = nation_ct.pk
    constituency_ct = None
    constituency_ct = get_zone_ct(Constituency, False)
    if constituency_ct is not None:
        constituency_ct = constituency_ct.pk
    title = forms.CharField(required=True,
                            widget=forms.TextInput(attrs={
                                'class':'form-control',
                            }))
    level = forms.ChoiceField(label=_("Position Level"),
                                    choices=[
                                            (nation_ct, 'Nation'),
                                            (constituency_ct, 'Constituency')
                                    ],
                                    widget=forms.Select(attrs={
                                            'class':'form-control',
                                    }))
    # agent = forms.CharField(required=True)
    # nation = forms.CharField(required=True)
    # details = forms.CharField(widget=forms.Textarea, required=True)
    # status = forms.CharField(required=True)
    
class PositionForm(forms.Form):
    nation_ct = None
    nation_ct = get_zone_ct(Nation, False)
    if nation_ct is not None:
        nation_ct = nation_ct.pk

    constituency_ct = None
    constituency_ct = get_zone_ct(Constituency, False)
    if constituency_ct is not None:
        constituency_ct = constituency_ct.pk

    content_types = []
    if nation_ct is not None and constituency_ct is not None:
        if nation_ct > 0 and constituency_ct > 0:
            content_types = [
                (nation_ct, 'Nation'),
                (constituency_ct, 'Constituency')
            ]

    title_label = forms.CharField(label=_('Position Title'), required=True)
    title = forms.CharField(label=_(''), required=True)
    nation = forms.ModelChoiceField(label=_(""),
                                    queryset=Nation.objects.all(),
                                    widget=forms.Select(attrs={
                                        'class':'form-control',
                                        'hidden':'true',
                                        'id': f'zone_{nation_ct}',
                                    }))
    constituency = forms.ModelChoiceField(label=_(""),
                                          queryset=Constituency.objects.all(),
                                          widget=forms.Select(attrs={
                                            'class':'form-control',
                                            'hidden':'true',
                                            'id': f'zone_{constituency_ct}',
                                          }))
    zone_ct_id = forms.ChoiceField(label=_("Position Level"),
                                   choices=content_types,
                                   widget=forms.Select(attrs={
                                        'class':'form-control',
                                        'onchange':'selectZoneID(this);setPositionTitle()',
                                   }))
    zone_id = forms.ModelChoiceField(label=_("Position Location"),
                                     queryset=Nation.objects.none(),
                                     widget=forms.Select(attrs={
                                                            'class':'form-control',
                                                            'onchange':'setPositionTitle()',
                                                        }))
    details = forms.CharField(label=_('Position Details (Optional)'),
                              widget=forms.Textarea(attrs={
                                                        "placeholder": "enter position detials",
                                                        "class": "form-control",
                                                    }),
                             required=True)
    def __init__(self, *args, **kwargs):
        super(PositionForm, self).__init__(*args, **kwargs)
        initial = kwargs.get('initial', {})
        self.fields['title_label'].widget=forms.TextInput(attrs={
            "value": initial.get('title', ''),
            "class": "form-control",
            'disabled': 'true',
        })
        self.fields['title'].widget=forms.TextInput(attrs={
            "placeholder": "enter position title",
            "class": "form-control",
            'hidden': 'true',
        })
        intial_zone = initial.get('zone_ct_id', None)
        self.fields['zone_id'].queryset=Constituency.objects.all()
        zone_ct = get_zone_ct(Nation)
        if zone_ct is not None:
            if intial_zone == zone_ct.pk:
                self.fields['zone_id'].queryset=Nation.objects.all()


class ResultForm(forms.Form):
    station = forms.ModelChoiceField(label=_('Station'), 
                                      queryset=Station.objects.filter(pk=1),
                                      widget=forms.Select(attrs={
                                        'class':'form-control',
                                        'placeholder': 'select position'
                                      }),
                                      required=True)
    candidate = forms.ModelChoiceField(label=_('Candidate'), 
                                      queryset=Candidate.objects.all(),
                                      widget=forms.Select(attrs={
                                        'class':'form-control',
                                        'placeholder': 'select party'
                                      }),
                                      required=True)
    votes = forms.CharField(label=_('Total Votes'), required=True)
    constituency_agent = forms.CharField(label=_('Agent'), required=True)
    details = forms.CharField(widget=forms.Textarea(attrs={
                                                           'class':'form-control',
                                                           'placeholder': 'enter details'
                                                   }), required=True)
    status = forms.CharField(required=True)
    result_sheet = forms.FileField(label=_('Upload result sheet'),
                                   help_text=_('Max. 4 kilobytes'))
    status = forms.ChoiceField(label=_("Status"), choices=StatusChoices.choices,
                               widget=forms.Select(attrs={'class':'form-control'}))

    def __init__(self, *args, **kwargs):
        super(ResultForm, self).__init__(*args, **kwargs)
        text_attrs={
            "placeholder": "enter nation Name",
            "class": "form-control",
        }
        text_attrs["placeholder"] = "select constituency agent"
        self.fields['constituency_agent'].widget=forms.TextInput(attrs=text_attrs)
        text_attrs["placeholder"] = "enter number of votes"
        self.fields['votes'].widget=forms.TextInput(attrs=text_attrs)
        text_attrs["placeholder"] = "enter details"
        self.fields['details'].widget=forms.TextInput(attrs=text_attrs)

    
class ResultApprovalForm(forms.Form):
    title = forms.CharField(required=True)
    agent = forms.CharField(required=True)
    details = forms.CharField(widget=forms.Textarea, required=True)
    status = forms.CharField(required=True)
