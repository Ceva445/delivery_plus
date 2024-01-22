from django.shortcuts import render, redirect
from .models import Delivery, Supplier, ReasoneComment, Location, ImageModel
from django.views import View
from .forms import DeliveryForm
from django.contrib.auth.mixins import LoginRequiredMixin
from .utils import gen_comment
from django.db import transaction


class HomeView(LoginRequiredMixin, View):
    template_name = "index.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

class SelectReceptionView(LoginRequiredMixin, View):
    template_name = "delivery/select_reception.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

class DeliveryCreateView(LoginRequiredMixin, View):
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
        selected_supplier_id = int(request.POST.get('selected_supplier_id'))
        order_nr = int(request.POST.get('order_nr'))
        sscc_barcode = request.POST.get('sscc_barcode')
        shop_nr = int(request.POST.get("shop"))
        reasones = request.POST.get('reasones')
        comment = request.POST.get("comment", None)

        if comment is None:
            recive_loc = Location.objects.get(name="2R")
            comment = gen_comment(request)
        else:
            recive_loc =  Location.objects.get(name="1R")

        if request.FILES:
                # Extract all files dynamically based on the pattern 'images_url_{{index}}'
                index = 0
                images = []
                while f'images_url_{index}' in request.FILES:
                    image_file = request.FILES[f'images_url_{index}']
                    images.append(ImageModel(custom_prefix=order_nr, image_data=image_file))
                    index += 1

                # Bulk create the images
                image_instances = ImageModel.objects.bulk_create(images)
        else:
            image_instances = []


        with transaction.atomic():
            if request.FILES:
                # Extract all files dynamically based on the pattern 'images_url_{{index}}'
                index = 1
                images = []
                while f'images_url_{index}' in request.FILES:
                    image_file = request.FILES[f'images_url_{index}']
                    images.append(ImageModel(custom_prefix=order_nr, image_data=image_file))
                    index += 1

                # Bulk create the images
                image_instances = ImageModel.objects.bulk_create(images)
                print(image_instances)
                # Create the delivery instance after bulk creation of image instances
                delivery = Delivery.objects.create(
                    supplier_company=Supplier.objects.get(id=selected_supplier_id),
                    nr_order=order_nr,
                    sscc_barcode=sscc_barcode,
                    user=self.request.user,
                    comment=comment,
                    recive_location=recive_loc,
                    location=recive_loc
                )
                
                # Save the delivery instance
                delivery.save()
                delivery.images_url.add(*image_instances)
                delivery.save()


        return render(request, "delivery/select_reception.html")