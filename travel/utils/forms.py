# forms.py
from django import forms
from formtools.wizard.views import SessionWizardView


class TravelProfileForm(forms.Form):
    # Profile choice (Page 1)
    profile = forms.ChoiceField(
        choices=[], widget=forms.RadioSelect, label="Select your profile", initial=""
    )


class TravelProfileFormPage2(forms.Form):
    # Adults and children (Page 2)
    adult_amount = forms.IntegerField(min_value=1, label="Adults", initial=1)
    children_amount = forms.IntegerField(min_value=0, label="Children", initial=0)


class TravelProfileFormPage3(forms.Form):
    # Vacation type (Page 3)
    vacation_type = forms.MultipleChoiceField(
        choices=[],
        widget=forms.RadioSelect,
        label="Vacation type",
    )


class TravelProfileFormPage4(forms.Form):
    # Location input (Page 4)
    location = forms.CharField(max_length=100, label="Your location")
    longitude = forms.HiddenInput()
    latitude = forms.HiddenInput()


class TravelProfileFormPage5(forms.Form):
    # Preferred airports (Page 5)
    airport_select = forms.MultipleChoiceField(
        choices=[],
        widget=forms.SelectMultiple(attrs={"class": "form-select"}),
        label="Preferred airports",
    )


class TravelProfileWizard(SessionWizardView):
    form_list = [
        TravelProfileForm,
        TravelProfileFormPage2,
        TravelProfileFormPage3,
        TravelProfileFormPage4,
        TravelProfileFormPage5,
    ]

    def done(self, form_list, **kwargs):
        # Process the submitted data here
        pass
