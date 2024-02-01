from django.shortcuts import render, redirect
from .models import (Delivery, 
                     Supplier, 
                     ReasoneComment, 
                     Location, 
                     ImageModel,
                     Shop,
                     )
from django.views import View
from .forms import DeliveryForm
from django.contrib.auth.mixins import LoginRequiredMixin
from .utils import gen_comment
from django.db import transaction
from django.shortcuts import get_object_or_404
from datetime import date
from deliveryplus.settings import GS_BUCKET_NAME



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
        selected_supplier_id = request.POST.get('selected_supplier_id')
        order_nr = int(request.POST.get('order_nr'))
        sscc_barcode = request.POST.get('sscc_barcode')
        shop_nr = int(request.POST.get("shop"))
        comment = request.POST.get("comment", None)
        date_recive = request.POST.get("date_recive", date.today())
        if comment is None:
            recive_loc = Location.objects.get(name="2R")
            comment = gen_comment(request)
        else:
            recive_loc =  Location.objects.get(name="1R")
        with transaction.atomic():   
            delivery = Delivery.objects.create(
                supplier_company=get_object_or_404(Supplier,id=selected_supplier_id),
                nr_order=order_nr,
                sscc_barcode=sscc_barcode,
                user=self.request.user,
                comment=comment,
                recive_location=recive_loc,
                shop=Shop.objects.get(position_nr=int(shop_nr)),
                location=recive_loc,
                date_recive=date_recive
            )
            if request.FILES:
                index = 1
                images = []
                while f'images_url_{index}' in request.FILES:
                    image_file = request.FILES[f'images_url_{index}']
                    images.append(ImageModel(custom_prefix=order_nr, image_data=image_file))
                    index += 1
                image_instances = ImageModel.objects.bulk_create(images)
                delivery.images_url.add(*image_instances)
            delivery.save()
        return render(request, "delivery/select_reception.html")

class DeleveryDetailView(LoginRequiredMixin, View):
    def get_context_data(self, delivery_id):
        context = {}
        delivery = get_object_or_404(Delivery, id=delivery_id)
        date_recive = delivery.date_recive.strftime("%d.%m.%Y")
        context["date_recive"] = date_recive

        if delivery.images_url.all():
            context["image_urls"] = []
            for url in delivery.images_url.all():
                image_path = f"https://storage.googleapis.com/{GS_BUCKET_NAME}/{url.image_data}"
                context["image_urls"].append(image_path)
        context["delivery"] = delivery
        
        
        return context
    

    def get(self, request, *args, **kwargs):
        delivery_id = self.kwargs.get("pk")
        context = self.get_context_data(delivery_id=delivery_id)
        
        return render(request, "delivery/delivery_detail.html",context)


class DeliveryStorageView(LoginRequiredMixin, View):
    template_name = "delivery/storeg_filter_page.html"
    
    def get_context_data(self, **kwargs):
        context = {}
        return context
    
    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)
       
    def post(self, request, *args, **kwargs):
        context = {}
        identifier = request.POST.get("identifier")
        nr_order = request.POST.get("nr_order")
        sscc_barcode = request.POST.get("sscc_barcode")
        date_recive = request.POST.get("date_recive")
        shop = request.POST.get("shop")
        location = request.POST.get("location")

        queryset = Delivery.objects.all().select_related("supplier_company", "recive_location", "shop", "location")
        if identifier:
            queryset = queryset.filter(identifier__icontains=identifier)
        if nr_order:
            queryset = queryset.filter(nr_order__icontain=nr_order)
        if sscc_barcode:
            queryset = queryset.filter(sscc_barcode=sscc_barcode)
        if date_recive:
            queryset = queryset.filter(date_recive=date_recive)
        if shop:
            queryset = queryset.filter(shop=shop)
        if location:
            queryset = queryset.filter(location__name__icontains=location)
        context["delivery_list"] = queryset
        return render(request, "delivery/delivery_list.html", context) 


class RlocationView(LoginRequiredMixin, View):
    template_name = "delivery/relocation.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    
    def post(self, request, *args, **kwargs):
        identifier = request.POST.get("identifier")
        to_location = request.POST.get("to_location")
        
        context = self.relocate_or_get_error(identifier, to_location)
        if context["status"]:
            return render(request, self.template_name,)
        else:
            return render(request, self.template_name, context)
        

    def relocate_or_get_error(self, identifier, to_location):
        error_message = ""
        status = True
        auto_in_val = {"identifier":identifier, "to_location": to_location}
        try:
            location = Location.objects.get(name__iexact=to_location)
        except Location.DoesNotExist:
            error_message = "Nieprawidłowa lokalizacja"
            del auto_in_val["to_location"]
            status = False 
        try:
            delivery = Delivery.objects.get(identifier=identifier)
        except Delivery.DoesNotExist:
            if error_message:
                error_message += "i identyfikator."
            else:
                error_message = "Nieprawidłowy identyfikator."
            del auto_in_val["identifier"]
            status = False

        if status:
            delivery.location = location
            delivery.save()
            return {"status": status}
        return {"status": status, "error_message": error_message} | auto_in_val