from django.shortcuts import render, redirect
from .models import Delivery, Supplier, ReasoneComment
from django.views import View
from .forms import DeliveryForm


class DeliveryCreateView(View):
    template_name = 'delivery/create_delivery.html'

    def get_context_data(self, **kwargs):
        # Dummy data for testing
        supliers_list = Supplier.objects.all()
        suppliers = [{"id": sup.id, "name": sup.name} for sup in supliers_list]
        reasones_list = ReasoneComment.objects.all()
        reasones = [{"id": reas.id, "name": reas.name} for reas in reasones_list]

        # reasones = [
        #     {'id': 1, 'name': 'Reasone 1'},
        #     {'id': 2, 'name': 'Reasone 2'},
        #     {'id': 3, 'name': 'Reasone 3'},
        # ]
        return {
            'suppliers': suppliers, 
            "reasones": reasones
            }

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
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