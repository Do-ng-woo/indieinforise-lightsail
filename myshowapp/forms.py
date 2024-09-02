from django import forms
from myshowapp.models import MyShow_illust

class MyShow_illust_Form(forms.ModelForm):
    class Meta:
        model = MyShow_illust
        fields = ['background', 'singer', 'guitarist', 'bassist', 'drummer', 'keyboardist', 'audience', 'lighting', 'positions', 'sizes', 'z_indices']
        widgets = {
            'positions': forms.HiddenInput(attrs={'id': 'id_positions'}),
            'sizes': forms.HiddenInput(attrs={'id': 'id_sizes'}),
            'z_indices': forms.HiddenInput(attrs={'id': 'id_z_indices'}),
        }