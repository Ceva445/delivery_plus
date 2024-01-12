from django.shortcuts import render, redirect
from .models import Delivery, Supplier, ReasoneComment
from django.views import View
from .forms import DeliveryForm


def home(request):
    return render(request, "index.html")

def select_reception(request):
    return render(request, "delivery/select_reception.html")

class SecondRecivCreateView(View):
    template_name = "delivery/delivery_create.html"

    def get_context_data(self, **kwargs):
        # Dummy data for testing
        
        supliers_list = Supplier.objects.all()
        suppliers = [{"id": sup.id, "name": sup.name, "supplier_wms_id":sup.supplier_wms_id} for sup in supliers_list]
        reasones_list = ReasoneComment.objects.all()
        reasones = [{"id": reas.id, "name": reas.name} for reas in reasones_list]

        return {
            "suppliers": suppliers, 
            "reasones": reasones
            }

    def get(self, request, *args, **kwargs):
        reception = (self.request.GET.get('reception', None))
        context = self.get_context_data()
        context["reception"] = reception
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # Process the form submission
        form = DeliveryForm(request.POST, request.FILES)
        # Retrieve values from the form
        supplier_company = request.POST.get('supplier_company')
        nr_order = request.POST.get('nr_order')
        ssc_barcode = request.POST.get('ssc_barcode')
        images_url = request.FILES.get('images_url')
        reasones = request.POST.get('reasones')
        selected_supplier_id = request.POST.get('selected_supplier_id')

        print(request.FILES)
        
        # field_count = 0
        # while True:
        #     print(field_count)
        #     ean = request.POST.get(f'ean_{field_count}')
        #     qty = request.POST.get(f'qty_{field_count}')

        #     if ean is None or qty is None:
        #         break
        #     print(ean)
        #     print(qty)

        #     field_count += 1

     
        return render(request, self.template_name)