from django import forms


class OTPVerifyForm(forms.Form):
    # One field: the 6-digit code the user types back in.
    code = forms.CharField(max_length=6, min_length=6, label='Verification Code')
