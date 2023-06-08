from django import forms
from django.apps import apps
from __poll.constants import StatusChoices, FormMessages
from django.utils.translation import gettext_lazy as _

from __poll.utils.utils import get_zone_ct
from __people.models import Party
from __poll.models import Position
from django.forms import ImageField
from __poll.widgets import ImagePreviewWidget


class AgentForm(forms.Form):
    content_types = ['nation', 'region', 'constituency', 'station']
    content_type_choices = []
    content_type_dict = {}
    for ct in content_types:
        ct_instance = None
        ct_instance = get_zone_ct(apps.get_model('__geo', ct), False)
        if ct_instance is not None:
            ct_instance = ct_instance.pk
            if ct_instance > 0:
                content_type_choices.append((ct_instance, ct.capitalize()))
        content_type_dict[ct] = ct_instance

    first_name = forms.CharField(required=True,
                                 widget=forms.TextInput(attrs={
                                                            'class': 'form-control',
                                                            'placeholder': 'enter agent first name',
                                                           }))
    last_name = forms.CharField(required=True,
                                widget=forms.TextInput(attrs={
                                                            'class': 'form-control',
                                                            'placeholder': 'enter agent last name',
                                                           }))
    email = forms.CharField(required=True,
                            widget=forms.TextInput(attrs={
                                                        'class': 'form-control',
                                                        'placeholder': 'enter agent email address',
                                                       }))
    phone = forms.CharField(required=True,
                            widget=forms.TextInput(attrs={
                                                        'class': 'form-control',
                                                        'placeholder': 'enter agent phone number',
                                                       }))
    zone_ct_id = forms.ChoiceField(label=_("Level"),
                                   choices=content_type_choices,
                                   widget=forms.Select(attrs={
                                                            'class':'form-control',
                                                            'onchange': 'fetchZonesByLevel(this, \'id_zone_id\')',
                                                            }))
    zone_id_filter = forms.CharField(label=_('Search Zone'),
                                  widget=forms.TextInput(attrs={
                                                                'parent_class': 'col-6',
                                                                'class': 'form-control',
                                                                'placeholder': 'enter search keyword',
                                                                'onkeyup': 'filterZonesOnForm(this)',
                                                                'data-src': 'id_zone_id',
                                                              }),
                                  required=False)
    zone_id = forms.ModelChoiceField(label=_("Zone"),
                                     queryset=apps.get_model('__geo', 'nation').objects.none(),
                                     widget=forms.Select(attrs={
                                                                'parent_class': 'col-6',
                                                                'class':'form-control',
                                                                }))
    description = forms.CharField(label=_('Details (Optional)'),
                                  widget=forms.Textarea(attrs={
                                                               'class': 'form-control',
                                                               'placeholder': 'enter notes on agent',
                                                               'rows': '3',
                                                              }),
                                  required=False)
    status = forms.ChoiceField(label="Status",
                               choices=StatusChoices.choices,
                               required=False,
                               widget=forms.Select(attrs={'class':'form-control', 'placeholder': 'select status'}))
    
    def __init__(self, *args, **kwargs):
        super(AgentForm, self).__init__(*args, **kwargs)
        initial = kwargs.get('initial', {})
        intial_zone_ct = initial.get('zone_ct_id', None)
        intial_zone_id = initial.get('zone_ct_id', None)

        self.fields['zone_id'].widget.attrs['data-value'] = intial_zone_id
        for ct in self.content_types:
            if intial_zone_ct == self.content_type_dict[ct]:
                self.fields['zone_id'].queryset = apps.get_model('__geo', ct) \
                                                      .objects.all()
                break


class CandidateForm(forms.Form):
    photo = forms.ImageField(label="Candidate Headshot",
                             required=False,
                             widget=ImagePreviewWidget(label="Photo:"),)
    # photo = forms.FileField(label="Candidate Headshot", required=False,
    #                         widget=forms.FileInput(attrs={'class':'form-control',
    #                                                       'placeholder': 'upload photo image (jpg, gif)'}))
    prefix = forms.CharField(label="Prefix", required=False,
                             widget=forms.TextInput(attrs={'class':'form-control',
                                                          'placeholder': FormMessages.ENTRY_HELP.format('prefix')}),
                             )
    first_name = forms.CharField(label="First Name", required=True,
                                 widget=forms.TextInput(attrs={'class':'form-control',
                                                                'placeholder': FormMessages.ENTRY_HELP.format('first name')}),
                                 error_messages={'required': FormMessages.INVALID_REQUIRED.format('First name'),
                                                'invalid': FormMessages.INVALID_ENTRY.format('First name'),}
                                 )
    last_name = forms.CharField(label="Last Name", required=True,
                                widget=forms.TextInput(attrs={'class':'form-control',
                                                              'placeholder': FormMessages.ENTRY_HELP.format('last name')}),
                                error_messages={'required': FormMessages.INVALID_REQUIRED.format('Last name'),
                                                'invalid': FormMessages.INVALID_ENTRY.format('Last name'),}
                                )
    other_names = forms.CharField(label="Other Names", required=False,
                                  widget=forms.TextInput(attrs={'class':'form-control',
                                                            'placeholder': FormMessages.ENTRY_HELP.format('other names')}),
                                  )
    position = forms.ModelChoiceField(label="Position", required=True,
                                      queryset=Position.objects.all(),
                                      widget=forms.Select(attrs={'class':'form-control',
                                                          'placeholder': FormMessages.SELECT_HELP.format('position')}),
                                      error_messages={'required': FormMessages.INVALID_REQUIRED.format('Position'),
                                                      'invalid_choice': FormMessages.INVALID_CHOICE.format('Position'),}
                                     )
    party = forms.ModelChoiceField(label="Party", required=True,
                                   queryset=Party.objects.all(),
                                   widget=forms.Select(attrs={'class':'form-control',
                                                              'placeholder': FormMessages.SELECT_HELP.format('party')}),
                                   error_messages={'required': FormMessages.INVALID_REQUIRED.format('Party'),
                                                   'invalid_choice': FormMessages.INVALID_CHOICE.format('Party'),}
                                  )
    description = forms.CharField(required=False,
                                  widget=forms.Textarea(attrs={'class':'form-control',
                                                               'placeholder': FormMessages.ENTRY_HELP.format('party'),
                                                               'rows': '3',
                                                        }))
    status = forms.ChoiceField(label="Status",
                               choices=StatusChoices.choices,
                               required=False,
                               widget=forms.Select(attrs={'class':'form-control'}))

    def __init__(self, *args, **kwargs):
        super(CandidateForm, self).__init__(*args, **kwargs)


class PartyForm(forms.Form):
    code = forms.CharField(required=True)
    title = forms.CharField(required=True)
    agent = forms.CharField(required=True)
    details = forms.CharField(widget=forms.Textarea(attrs={
                "placeholder": "enter detials",
                "class": "form-control",
                'rows': '3',
            }), required=True)
    status = forms.ChoiceField(label="Status", choices=StatusChoices.choices,
                               widget=forms.Select(attrs={'class':'form-control'}))

    def __init__(self, *args, **kwargs):
        super(PartyForm, self).__init__(*args, **kwargs)
        text_attrs={
            "placeholder": "enter party name",
            "class": "form-control",
        }
        self.fields['title'].widget=forms.TextInput(attrs=text_attrs)
        text_attrs["placeholder"] = "enter party name"
        self.fields['code'].widget=forms.TextInput(attrs=text_attrs)
        text_attrs["placeholder"] = "select party agent"
        self.fields['agent'].widget=forms.TextInput(attrs=text_attrs)
