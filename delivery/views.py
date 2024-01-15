from django.shortcuts import render, redirect
from .models import Delivery, Supplier, ReasoneComment
from django.views import View
from .forms import DeliveryForm


def home(request):
    return render(request, "index.html")

def select_reception(request):
    return render(request, "delivery/select_reception.html")

class DeliveryCreateView(View):
    template_name = "delivery/delivery_create.html"

    def get_context_data(self, **kwargs):

        supliers_list = Supplier.objects.all()
        suppliers = [{"id": sup.id, "name":f"{sup.name} - {sup.supplier_wms_id}"} for sup in supliers_list]
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

        form = DeliveryForm(request.POST, request.FILES)

        supplier_company = request.POST.get('supplier_company')
        selected_supplier_id = request.POST.get('selected_supplier_id')
        order_nr = request.POST.get('order_nr')
        sscc_barcode = request.POST.get('sscc_barcode')
        shop_nr = request.POST.get("shop")
        reasones = request.POST.get('reasones')
        comment = request.POST.get("comment", None)


        print(f"Supplier Company: {supplier_company}")
        print(f"Selected Supplier ID: {selected_supplier_id}")
        print(f"Order Number: {order_nr}")
        print(f"SSCC Barcode: {sscc_barcode}")
        print(f"Shop Number: {shop_nr}")
        print(f"Reasones: {reasones}")
        print(f"Comment: {comment}")

        if request.FILES:
            for _ in request.FILES.items():
                print(_)
        
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

     
        return render(request, "delivery/select_reception.html")