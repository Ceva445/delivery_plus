from django import forms

class DeliveryForm(forms.Form):
    supplier_company = forms.CharField()
    nr_order = forms.IntegerField()
    ssc_barcode = forms.CharField()
    images_url = forms.FileField(required=False)
    reasones = forms.CharField()
    ean = forms.IntegerField()
    qty = forms.IntegerField()


    def clean_images_url(self):
        data = self.cleaned_data['images_url']
        # Perform any validation or processing on the images_url field if needed
        return data