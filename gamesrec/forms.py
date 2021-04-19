from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import *
from django.contrib.auth.models import auth
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
import re

from django.contrib.auth.hashers import check_password

from crispy_forms.bootstrap import Field, InlineRadios, TabHolder, Tab
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, Fieldset, Row, Column

from django.core.exceptions import ValidationError


class RegistrationForm(UserCreationForm):
    username = forms.CharField(required=True, label='Username: ',widget= forms.TextInput(attrs={'autofocus': True,'placeholder':'Username'}))
    email = forms.EmailField(required=True, label='E-mail Address: ',widget= forms.EmailInput(attrs={'placeholder':'E.g email@example.com'}))
    password1 = forms.CharField(required=True, label='Password: ', strip=False,widget=forms.PasswordInput(attrs={'placeholder':'At least 8 characters'}))
    password2 = forms.CharField(required=True, label='Confirm password: ', strip=False,widget=forms.PasswordInput(attrs={'placeholder':'Re-type password'}))
    terms = forms.BooleanField(required=True, label=' <small>I agree to the <a href="#" class="text-primary">Terms of Service</a> and <a href="#" class="text-primary">Privacy Policy</a></small> ',widget=forms.CheckboxInput())

    class Meta:
        model = User
        fields = ('username','email','password1','password2')


    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = User.objects.filter(email=email)
        if qs.exists():
            raise forms.ValidationError("That email is taken. Please try another.")
        return email

    def max_occ_in_a_row(self, s, chr, counts=None,c=0,i=0):
        if counts is None:
            counts = []
        if i == len(s):
            return max(counts)
        for i in range(i,len(s)):
            if s[i] != chr:
                counts.append(c)
                c = 0
                return self.max_occ_in_a_row(s,chr,counts,c, i+1)
            c+=1

    def clean_username(self):
        username = self.cleaned_data.get('username')
        qs = User.objects.filter(username__iexact=username)
        if len(username) <= 3:
            raise forms.ValidationError("Your username must have more than 3 characters.")
        if len(username) > 64:
            raise forms.ValidationError("Your username must have more than 3 and fewer than 64 characters")
        if username.startswith('.') or username.endswith('.'):
            raise forms.ValidationError("Usernames may not begin or end with full stops (.). ")
        if self.max_occ_in_a_row(username,'.') > 1 or self.max_occ_in_a_row(username,'-') > 1 or self.max_occ_in_a_row(username,'_') > 1:
            raise forms.ValidationError("Usernames may not contain more than one dash (-), underscore (_) or full stop (.) in a row")
        is_alnum_fullstop = re.match('^[\w.-]+$', username) is not None
        if not is_alnum_fullstop:
            raise forms.ValidationError("Usernames may contain letters (a-z), numbers (0-9), dashes (-), underscores (_) and full stops (.).")
        if qs.exists():
            raise forms.ValidationError("That username is taken. Please try another.")
        return username

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2
#


class LoginForm(forms.ModelForm):
    email = forms.EmailField(required=True, label='',widget= forms.EmailInput(attrs={'autofocus': True,'placeholder':'Your E-mail Address *'}))
    password = forms.CharField(required=True, label='', strip=False,widget=forms.PasswordInput(attrs={'autocomplete': 'current-password','placeholder':'Your Password *'}))
    remember_me = forms.BooleanField(required=False, widget=forms.CheckboxInput())

    class Meta:
        model = User
        fields = ('email',)

    error_messages = {
        'invalid_login':(
            "Please enter a correct %(email)s and password. Note that both "
            "fields may be case-sensitive."
        ),
        'inactive': ("This account is inactive."),
    }

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        self.email_field = User._meta.get_field(User.USERNAME_FIELD)
        super().__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if self.cleaned_data.get('remember_me',None):
            self.request.session.set_expiry(3.154e+9) #100 years
        # else:
        #     self.request.session.set_expiry(20)

        if email is not None and password:
            self.user_cache = auth.authenticate(self.request, email=email, password=password)
            try:
                us = User.objects.get(email=email)
                if check_password(password, us.password):
                    self.user_cache = us
            except Exception as e:
                pass
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )

    def get_user(self):
        return self.user_cache

    def get_invalid_login_error(self):
        return forms.ValidationError(
            self.error_messages['invalid_login'],
            code='invalid_login',
            params={'email': self.email_field.verbose_name},
        )

class UserAdminCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email',)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserAdminCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserAdminChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField(label= ("Password"),
        help_text= ("Raw passwords are not stored, so there is no way to see "
                    "this user's password, but you can change the password "
                    "using <a href=\"../password/\">this form</a>."))

    class Meta:
        model = User
        fields = ('email', 'password', 'is_active', 'is_admin')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class AccountSettingsForm_Profile(forms.ModelForm):
    display_name = forms.CharField(required=True, label='Display Name',widget= forms.TextInput(attrs={'placeholder':'','class':'el-input__inner'}))
    dob_privacy = forms.BooleanField(required=False,label='Private',widget= forms.CheckboxInput())
    dark_mode = forms.BooleanField(required=False,label='Dark Theme',widget= forms.CheckboxInput(attrs={'class':'mdl-switch__input'}))
    picture = forms.ImageField(required=False)

    class Meta:
        model = Profile
        fields = ['display_name','picture','dob_privacy','dark_mode']


class AccountSettingsForm_User(forms.ModelForm):
    username = forms.CharField(required=False,label='Username',widget= forms.TextInput(attrs={'placeholder':'','disabled':'disabled','class':'el-input__inner'}))
    email = forms.CharField(required=False, label='E-mail',widget= forms.EmailInput(attrs={'placeholder':'','disabled':'disabled','class':'el-input__inner'}))
    gender = forms.ChoiceField(required=False,label='Gender',widget=forms.Select(attrs={'class':'browser-default custom-select el-input__inner'}),choices=User.gender_choices)
    date_of_birth = forms.DateField(required=False,label='Date of Birth', widget=forms.TextInput(attrs={'placeholder':'Pick a date', 'class':'datepicker el-input__inner'}))
    dob = date_of_birth

    class Meta:
        model = User
        fields = ['username','email','gender','dob']


class GameListItemForm(forms.ModelForm):
    status = forms.ChoiceField(required=True,label='Status',widget=forms.Select(attrs={'class':'browser-default custom-select'}),choices=GameListItem.status_choices)
    rating = forms.ChoiceField(required=False,label='Overall Rating',widget=forms.Select(attrs={'class':'browser-default custom-select'}),choices=GameListItem.rating_choices)
    # notes = models.TextField(forms.Textarea())

    class Meta:
        model = GameListItem
        fields = ['status','rating','notes', 'user','game']

class ReviewForm(forms.ModelForm):
    spoiler = forms.ChoiceField(required=True, label='', choices=[(True, 'Yes'),(False, 'No')], widget=forms.RadioSelect(attrs={'required':''}))
    completed = forms.ChoiceField(required=True, label='', choices=[(True, 'Yes'),(False, 'No')], widget=forms.RadioSelect(attrs={'required':''}))
    dropped = forms.ChoiceField(required=False, label='', choices=[(True, 'Yes'),(False, 'No')], widget=forms.RadioSelect)
    review_text = forms.CharField(required=True, label='Write review',widget= forms.Textarea)

    def __init__(self, *args, **kwargs):
       super(ReviewForm, self).__init__(*args, **kwargs)
       # self.helper = FormHelper()
       # # self.helper.form_id = 'id-personal-data-form'
       # # self.helper.form_method = 'post'
       # # self.helper.form_action = reverse('submit_form')
       # # self.helper.add_input(Submit('submit', 'Submit', css_class='btn-success'))
       # # self.helper.form_class = 'form-horizontal'
       # self.helper.form_class = 'form-horizontal'
       # self.helper.layout = Layout(
       #                      InlineRadios('spoiler', style='margin-left:3rem;'),
       #                      InlineRadios('completed', style='margin-left:1.9rem;'),
       #                      InlineRadios('dropped', style='margin-left:5.8rem;'),
       #                      Row('review_text',
       #                      ),)

    class Meta:
        model = Review
        fields = ['review_text', 'spoiler', 'completed', 'dropped','user','game'] + [i['h_name'] for i in Review.r]



def min_length(value):
    if len(value.strip()) < 100:
        raise ValidationError(f'Your review must be at least 100 characters in length.')

class RecForm(forms.ModelForm):
    rec_text = forms.CharField(required=True, validators=[min_length], label='',widget= forms.Textarea)

    class Meta:
        model = Rec
        fields = ['rec_text','user','game', 'similar_game']

class CommentForm(forms.ModelForm):
    text = forms.CharField(widget= forms.Textarea)

    class Meta:
        model = Comment
        fields = ['text']
