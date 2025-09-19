from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from .relocate_or_get_error import relocate_or_get_error
from .models import (
    Delivery,
    Supplier,
    ReasoneComment,
    Location,
    ImageModel,
    Shop,
)
from django.views import View
from .forms import DeliveryForm
from django.contrib.auth.mixins import LoginRequiredMixin
from .utils import gen_comment, gen_pdf_damage_repor, generate_deliveries_excel
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
from django.utils import timezone
from deliveryplus.settings import GS_BUCKET_NAME
from .print_server import send_label_to_cups
from .utils import create_transaction
from .reclocation import relocate_delivery
from transaction.models import Transaction
from .reports import (
    write_ready_to_ship,
    write_summary_report_of_goods,
    write_total_action_count,
    write_irregularity_of_type
    )

from django.db.models import F, ExpressionWrapper, Func, DateTimeField
from django.db.models.functions import Now
from django.db.models import Count
from deliveryplus.settings import COMPLETED_ORDERS_AFTER_DAYS



class HomeView(LoginRequiredMixin, View):
    template_name = "index.html"

    # write_report_gs()
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


def admin_panel(request):
    return render(request, "delivery/admin_panel.html")


class SelectReceptionView(LoginRequiredMixin, View):
    template_name = "delivery/select_reception.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class DeliveryCreateView(LoginRequiredMixin, View):
    template_name = "delivery/delivery_create.html"

    def get_context_data(self, rec_loc, **kwargs):

        supliers_list = Supplier.objects.all()
        suppliers = [
            {"id": sup.id, "name": f"{sup.name} - {sup.supplier_wms_id}"}
            for sup in supliers_list
        ]
        if rec_loc == "second":
            reasones_list = ReasoneComment.objects.filter(name__icontains="Podczas kontroli")
        else:
            reasones_list = ReasoneComment.objects.filter(name__icontains="Podczas rozładunku") 
        reasones = [{"id": reas.id, "name": reas.name} for reas in reasones_list]

        return {"suppliers": suppliers, "reasones": reasones}

    def get(self, request, *args, **kwargs):
        reception = self.request.GET.get("reception", None)
        context = self.get_context_data(rec_loc=reception)
        context["reception"] = reception
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        selected_supplier_id = request.POST.get("selected_supplier_id")
        order_nr = int(request.POST.get("order_nr"))
        sscc_barcode = request.POST.get("sscc_barcode")
        shop_nr = int(request.POST.get("shop"))
        comment = request.POST.get("comment", None)
        extra_comment = request.POST.get("extra_comment", "")
        date_recive = request.POST.get("date_recive", None)
        recive_location = request.POST.get("recive_location")
        context = self.get_context_data(rec_loc = recive_location)
  
        if date_recive:
            date_recive = datetime.strptime(date_recive, "%Y-%m-%d") + timedelta(hours=5)
        else:
            date_recive = datetime.now()

        if not selected_supplier_id:
            context["reception"] = recive_location
            context["error_message"] = "Wprowadzono nieprawidłowego dostawcę"
            return render(request, self.template_name, context)

        if recive_location == "second":
            recive_loc = Location.objects.get(name="2R")
        else:
            recive_loc = Location.objects.get(name="1R")
        comment = gen_comment(request)
        label_comment = comment
        with transaction.atomic():
            delivery = Delivery.objects.create(
                supplier_company=get_object_or_404(Supplier, id=selected_supplier_id),
                nr_order=order_nr,
                sscc_barcode=sscc_barcode,
                user=self.request.user,
                comment=comment,
                recive_location=recive_loc,
                shop=Shop.objects.get(position_nr=int(shop_nr)),
                location=recive_loc,
                date_recive=date_recive,
                extra_comment=extra_comment,
            )
            delivery.transaction = f"\n{datetime.now().strftime('%m/%d/%Y, %H:%M')} {self.request.user.username} przyjął dostawę \n"
            delivery.save()
            create_transaction(
                user=self.request.user, delivery=delivery, transaction_type="Recive"
            )
        # Made it Celery  Task
        send_label_to_cups(delivery, label_comment)
        return render(
            request, "delivery/delivery_image_add.html", {"delivery_id": delivery.id}
        )
class DeliveryFirsrRecCreateView(LoginRequiredMixin, View):
    template_name = "delivery/delivery_first_rec_create.html"

    def get_context_data(self, **kwargs):

        supliers_list = Supplier.objects.all()
        suppliers = [
            {"id": sup.id, "name": f"{sup.name} - {sup.supplier_wms_id}"}
            for sup in supliers_list
        ]
        reasones_list = ReasoneComment.objects.filter(name__icontains="Podcas rozładunku") 
        reasones = [{"id": reas.id, "name": reas.name} for reas in reasones_list]

        return {"suppliers": suppliers, "reasones": reasones}

    def get(self, request, *args, **kwargs):
        reception = self.request.GET.get("reception", None)
        context = self.get_context_data()
        context["reception"] = reception
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        selected_supplier_id = request.POST.get("selected_supplier_id")
        order_nr = request.POST.get("order_nr")
        sscc_barcode = request.POST.get("sscc_barcode")
        shop_id = request.POST.get("shop", None)
        comment = request.POST.get("comment", None)
        extra_comment = request.POST.get("extra_comment", "")
        date_recive = request.POST.get("date_recive", None)
        recive_location = request.POST.get("recive_location")
        if date_recive:
            date_recive = datetime.strptime(date_recive, "%Y-%m-%d") + timedelta(hours=5)
        else:
            date_recive = datetime.now()
        if not selected_supplier_id:
            context = self.get_context_data()
            context["reception"] = recive_location
            context["error_message"] = "Wprowadzono nieprawidłowego dostawcę"
            return render(request, self.template_name, context)
        if shop_id:
            shop = Shop.objects.get(position_nr=int(shop_id))
        else:
            shop = None
        recive_loc = Location.objects.get(name="1R")
        print("!!!!!!!")
        comment = gen_comment(request)
        label_comment = str(request.POST.get("reasones","")).replace("Podcas rozładunku wykryto", "")
        print(label_comment)
        with transaction.atomic():
            delivery = Delivery.objects.create(
                supplier_company=get_object_or_404(Supplier, id=selected_supplier_id),
                nr_order=order_nr,
                sscc_barcode=sscc_barcode,
                user=self.request.user,
                comment=comment,
                recive_location=recive_loc,
                shop=shop,
                location=recive_loc,
                date_recive=date_recive,
                extra_comment=extra_comment,
            )
            delivery.transaction = f"\n{datetime.now().strftime('%m/%d/%Y, %H:%M')} {self.request.user.username} przyjął dostawę \n"
            delivery.save()
            create_transaction(
                user=self.request.user, delivery=delivery, transaction_type="Recive"
            )
        # Made it Celery  Task
        send_label_to_cups(delivery, label_comment)
        return render(
            request, "delivery/delivery_image_add.html", {"delivery_id": delivery.id}
        )


class DeliverySecondRecCreateView(LoginRequiredMixin, View):
    template_name = "delivery/delivery_second_rec_create.html"

    def get_context_data(self, **kwargs):

        supliers_list = Supplier.objects.all()
        suppliers = [
            {"id": sup.id, "name": f"{sup.name} - {sup.supplier_wms_id}"}
            for sup in supliers_list
        ]
        reasones_list = ReasoneComment.objects.filter(name__icontains="Podczas kontroli")
        reasones = [{"id": reas.id, "name": reas.name} for reas in reasones_list]
        return {"suppliers": suppliers, "reasones": reasones}

    def get(self, request, *args, **kwargs):
        reception = self.request.GET.get("reception", None)
        context = self.get_context_data()
        context["reception"] = reception
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        selected_supplier_id = request.POST.get("selected_supplier_id")
        order_nr = int(request.POST.get("order_nr"))
        sscc_barcode = request.POST.get("sscc_barcode")
        shop_nr = int(request.POST.get("shop"))
        comment = request.POST.get("comment", None)
        extra_comment = request.POST.get("extra_comment", "")
        date_recive = request.POST.get("date_recive", None)
        recive_location = request.POST.get("recive_location")
        context = self.get_context_data()
  
        if date_recive:
            date_recive = datetime.strptime(date_recive, "%Y-%m-%d") + timedelta(hours=5)
        else:
            date_recive = datetime.now()

        if not selected_supplier_id:
            context["reception"] = recive_location
            context["error_message"] = "Wprowadzono nieprawidłowego dostawcę"
            return render(request, self.template_name, context)
    
        recive_loc = Location.objects.get(name="2R")
        
        comment = gen_comment(request)
        label_comment = str(request.POST.get("reasones","")).replace("Podczas kontroli wykryto", "")
        with transaction.atomic():
            delivery = Delivery.objects.create(
                supplier_company=get_object_or_404(Supplier, id=selected_supplier_id),
                nr_order=order_nr,
                sscc_barcode=sscc_barcode,
                user=self.request.user,
                comment=comment,
                recive_location=recive_loc,
                shop=Shop.objects.get(position_nr=int(shop_nr)),
                location=recive_loc,
                date_recive=date_recive,
                extra_comment=extra_comment,
            )
            delivery.transaction = f"\n{datetime.now().strftime('%m/%d/%Y, %H:%M')} {self.request.user.username} przyjął dostawę \n"
            delivery.save()
            create_transaction(
                user=self.request.user, delivery=delivery, transaction_type="Recive"
            )
        # Made it Celery  Task
        send_label_to_cups(delivery, label_comment)
        return render(
            request, "delivery/delivery_image_add.html", {"delivery_id": delivery.id}
        )


class DeliveryImageAdd(LoginRequiredMixin, View):
    template_name = "delivery/delivery_image_add.html"

    def get_context_data(self, **kwargs):
        context = {}
        return context

    def get(self, request, *args, **kwargs):
        delivery_id = int(self.request.GET.get("delivery_id"))
        back_to_detail = self.request.GET.get("back_to_detail")
        context = self.get_context_data()
        context["delivery_id"] = delivery_id
        context["back_to_detail"] = back_to_detail
        print("!!!!!!!!!!",back_to_detail)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        delivery_id = self.request.POST.get("delivery_id")
        back_to_detail = self.request.POST.get("back_to_detail")
        print(back_to_detail)
        if request.FILES:
            delivery = Delivery.objects.get(id=delivery_id)
            index = 1
            images = []
            while f"images_url_{index}" in request.FILES:
                image_file = request.FILES[f"images_url_{index}"]
                images.append(
                    ImageModel(custom_prefix=delivery.nr_order, image_data=image_file)
                )
                index += 1
            image_instances = ImageModel.objects.bulk_create(images)
            delivery.images_url.add(*image_instances)
            delivery.save()
        if back_to_detail:
            return redirect("delivery:delivery_detail", pk=delivery_id) 
        return render(request, "delivery/select_reception.html")


class DeleveryDetailView(LoginRequiredMixin, View):
    def get_context_data(self, delivery_id):
        context = {}
        delivery = get_object_or_404(Delivery, id=delivery_id)
        date_recive = delivery.date_recive.strftime("%d.%m.%Y")
        context["comment"] = delivery.comment.replace("szt.", "szt.\n").replace(":", ":\n")
        context["date_recive"] = date_recive

        if delivery.images_url.all():
            context["image_urls"] = []
            for url in delivery.images_url.all():
                image_path = (
                    f"https://storage.googleapis.com/{GS_BUCKET_NAME}/{url.image_data}"
                )
                context["image_urls"].append(image_path)
        context["delivery"] = delivery

        return context

    def get(self, request, *args, **kwargs):
        delivery_id = self.kwargs.get("pk")
        context = self.get_context_data(delivery_id=delivery_id)

        return render(request, "delivery/delivery_detail.html", context)

    def post(self, request, *args, **kwargs):
        delivery_id = self.kwargs.get("pk")
        reverse_chek_status = self.request.POST.get("reverse_check_status")
        devivery_shiped = self.request.POST.get("shiped")
        delivery_utilize = self.request.POST.get("utilize")
        delivery_cancel = self.request.POST.get("cancel")
        delivery_reprint_label = self.request.POST.get("reprint")
        delivery_transfer = self.request.POST.get("transfer")
        delivery = Delivery.objects.get(id=delivery_id)
        
        context = self.get_context_data(delivery_id=delivery_id)
        lovo = self.request.POST.get("lovo")
        if lovo:
            print(lovo)
            lovo_url = self.request.POST.get("lovo_url")
            lovo_name = self.request.POST.get("lovo_name")
            delivery.lovo_link = lovo_url
            delivery.lovo_name = lovo_name

            delivery.transaction += f"\
                {datetime.now().strftime('%m/%d/%Y, %H:%M')} \
                     {self.request.user.username} dodał link Lovo"
            delivery.office_chek = True

            delivery.save()
            return redirect("delivery:delivery_detail", pk=delivery_id)


        if reverse_chek_status:
            if delivery.office_chek:
                status, new = "", "nie "
            else:
                status, new = "nie ", ""
            delivery.transaction += f"\
                {datetime.now().strftime('%m/%d/%Y, %H:%M')} \
                     {self.request.user.username} \
                        zmienił status dostawy z {status}sprawdzony przez biuro \
                            na {new}sprawdzony przez biuro\n"
            delivery.office_chek = not delivery.office_chek
            delivery.save()
            return redirect("delivery:delivery_detail", pk=delivery_id)
        if devivery_shiped or delivery_utilize or delivery_transfer:
            if devivery_shiped:
                to_location = Location.objects.get(name__iexact="Shiped")
            elif delivery_transfer:
                to_location = Location.objects.get(name__iexact="Transfer")
            else:
                to_location = Location.objects.get(name__iexact="Utulizacja")
            relocate_delivery(
                user=self.request.user, delivery=delivery, to_location=to_location
            )
            delivery.save()
            return redirect("delivery:delivery_detail", pk=delivery_id)
        # relocate to location ANULACJA and delete all pictures
        if delivery_cancel:
            to_location = Location.objects.get(name__iexact="ANULACJA")
            relocate_delivery(
                user=self.request.user, delivery=delivery, to_location=to_location
            )
            if delivery.images_url.values():
                delivery.delete_images()
                delivery.images_url.clear()
            delivery.save()
            return redirect("delivery:delivery_detail", pk=delivery_id)

        if delivery_reprint_label:
            send_label_to_cups(delivery=delivery, reprint_status=True)
            return redirect("delivery:delivery_detail", pk=delivery_id)
        delivery.save()

        return render(request, "delivery/delivery_detail.html", context)
class DeliveryArchivatorView(LoginRequiredMixin, View):
    template_name = "delivery/delivery_archivator.html"

    def get(self, request, *args, **kwargs):
        complite_deliveries = Delivery.objects.filter(
            complite_status=True,
            date_recive__lte=timezone.now() - timedelta(days=COMPLETED_ORDERS_AFTER_DAYS)
        ).select_related(
                "supplier_company", "recive_location", "shop", "location", "user"
            ).count()
        return render(request, self.template_name, {"complite_deliveries": complite_deliveries, "completed_orders_after_days": COMPLETED_ORDERS_AFTER_DAYS})

    def post(self, request, *args, **kwargs):
        recive_loc = request.POST.get("recive_loc")
        record_qty_raw = request.POST.get("record_qty")
        delete_record = request.POST.get("delete_record")
        completed_orders_after_days_raw = int(request.POST.get("completed_orders_after_days", COMPLETED_ORDERS_AFTER_DAYS))
        record_qty = int(record_qty_raw) if record_qty_raw and record_qty_raw.isdigit() else None

        deliveries = Delivery.objects.filter(complite_status=True,
                date_recive__lte=timezone.now() - timedelta(days=completed_orders_after_days_raw))\
            .select_related(
                "supplier_company", "recive_location", "shop", "location", "user"
            ).order_by("date_recive")

        if recive_loc and recive_loc != 'None':
            deliveries = deliveries.filter(recive_location__name=recive_loc)
        if record_qty and record_qty > 0:
            deliveries = deliveries[:record_qty]
        # Генерація Excel
        wb = generate_deliveries_excel(deliveries)

        # Віддаємо файл
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = 'attachment; filename="completed_deliveries.xlsx"'
        wb.save(response)
         # Видалення записів
        if delete_record:
            Delivery.objects.filter(id__in=[d.id for d in deliveries]).delete()

        return response

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
        status = request.POST.get("status")
        recive_loc = request.POST.get("recive_loc")
        office_chek = request.POST.get("office_chek")

        queryset = Delivery.objects.all().select_related(
            "supplier_company", "recive_location", "shop", "location"
        )
        if status and status != 'None':
            queryset = queryset.filter(location__work_zone=status)
        if identifier and identifier != 'None':
            queryset = queryset.filter(identifier__icontains=identifier)
        if nr_order and nr_order != 'None':
            queryset = queryset.filter(nr_order=nr_order)
        if sscc_barcode and sscc_barcode != 'None':
            queryset = queryset.filter(sscc_barcode__icontains=sscc_barcode)
        if date_recive and date_recive and date_recive != 'None':
            date_recive_dt = datetime.strptime(date_recive, "%Y-%m-%d")
            queryset = queryset.filter(date_recive__date=date_recive_dt)
        if shop and shop != 'None':
            queryset = queryset.filter(shop=shop)
        if location and location != 'None':
            queryset = queryset.filter(location__name__icontains=location)
        if recive_loc and recive_loc != 'None':
            queryset = queryset.filter(recive_location__name=recive_loc)
        if office_chek and office_chek != 'None':
            queryset = queryset.filter(office_chek=office_chek)


        page = request.POST.get('page', 1)
        paginator = Paginator(queryset.order_by("-date_recive"), 300)
        try:
            deliveries = paginator.page(page)
        except PageNotAnInteger:
            deliveries = paginator.page(1)
        except EmptyPage:
            deliveries = paginator.page(paginator.num_pages)

        context["delivery_list"] = deliveries
        context["filters"] = {
            "identifier": identifier,
            "nr_order": nr_order,
            "sscc_barcode": sscc_barcode,
            "date_recive": date_recive,
            "shop": shop,
            "location": location,
            "status": status,
            "recive_loc": recive_loc,
            "office_chek": office_chek,
        }

        return render(request, "delivery/delivery_list.html", context)

class RelocationView(LoginRequiredMixin, View):
    template_name = "delivery/relocation.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        identifier = request.POST.get("identifier")
        to_location = request.POST.get("to_location")

        context = relocate_or_get_error(
            identifier=identifier, 
            to_location=to_location, 
            request=request
            )
        if context["status"]:
            return render(
                request,
                self.template_name,
            )
        else:
            return render(request, self.template_name, context)

class UncompliteView(LoginRequiredMixin, View):
    template_name = "delivery/uncomplit.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        identifier = request.POST.get("identifier")
        to_location = request.POST.get("to_location")

        context = relocate_or_get_error(
            identifier=identifier, 
            to_location=to_location, 
            request=request,
            uncomplit=True
            )
        if context["status"]:
            return render(
                request,
                self.template_name,
            )
        else:
            return render(request, self.template_name, context)


class LocationListView(LoginRequiredMixin, View):
    template_name = "delivery/location_list.html"
    def get_context_data(self, **kwargs):
        context = {}
        locations = Location.objects.all()
        context["location_list"] = locations
        return context
    
    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context=context)


class LocationUpdateView(LoginRequiredMixin, View):
    template_name = "delivery/location_update.html"

    def get_context_data(self, locatio_id):
        context = {}
        location = Location.objects.get(id=locatio_id)
        context["location"] = location
        return context 

    def get(self, request, *args, **kwargs):
        location_id = self.kwargs.get("pk")
        context = self.get_context_data(locatio_id=location_id)
        return render(request, self.template_name, context=context) 
    
    def post(self, request, *args, **kwargs):
        location_id = self.kwargs.get("pk")
        location_name = self.request.POST.get("location_name")
        work_zone = self.request.POST.get("work_zone")
        delete_status = self.request.POST.get("delete")
        context = self.get_context_data(locatio_id=location_id)
        context["error_message"] = ""
        
        location = Location.objects.get(id=location_id)

        if location.name in ["1R", "2R", "Shiped", "Utulizacja"]:
            context["error_message"] = "Ta lokalizacja jest ważna, nie można jej usunąć ani zmienić"
            return render(request, self.template_name, context)

        if delete_status:
            if len(Delivery.objects.filter(location=location))>0:
                context["error_message"] ="Ta lokalizacja nie jest pusta, wykonaj relokację"
                return render(request, self.template_name, context)
            location.delete()
            return redirect(reverse("delivery:location_list"))

        if location_name and location_name != location.name:
            location.name = location_name
        
        if work_zone and work_zone != location.work_zone:
            location.work_zone = work_zone
        location.save()
        return redirect(reverse("delivery:location_list"))


class LocationCreateView(LoginRequiredMixin, View):
    template_name = "delivery/location_create.html"

    def get_context_data(self):
        context = {}
        context["WORKZON_CHOICES"] = Location.WORKZON_CHOICES
        return context 

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context=context) 

    def post(self, request, *args, **kwargs):
        location_name = self.request.POST.get("location_name")
        work_zone = self.request.POST.get("work_zone")
        context = self.get_context_data()
        try:
            Location.objects.create(
                name=location_name,
                work_zone=work_zone
            )
        except IntegrityError as e:
                context["error_message"] = (
                    "ta lokalizacja już istnieje"
                )
                return render(request, self.template_name, context=context) 

        return redirect(reverse("delivery:location_list"))

class SupplierListView(LoginRequiredMixin, View):
    template_name = "delivery/supplier_list.html"

    def get_context_data(self, **kwargs):
        context = {}
        suppliers = Supplier.objects.all()
        context["supplier_list"] = suppliers
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context=context)


class SupplierUpdateView(LoginRequiredMixin, View):
    template_name = "delivery/supplier_update.html"

    def get_context_data(self, supplier_id):
        context = {}
        supplier = Supplier.objects.get(id=supplier_id)
        context["supplier"] = supplier
        return context

    def get(self, request, *args, **kwargs):
        supplier_id = self.kwargs.get("pk")
        context = self.get_context_data(supplier_id=supplier_id)
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        supplier_id = self.kwargs.get("pk")
        wms_id = self.request.POST.get("wms_id")
        name = self.request.POST.get("sup_name")
        supplier = Supplier.objects.get(id=supplier_id)
        context = self.get_context_data(supplier_id=supplier_id)
        with transaction.atomic():
            try:
                if wms_id:
                    supplier.supplier_wms_id = wms_id
                if name:
                    supplier.name = name
                supplier.save()
            except IntegrityError as e:
                if "unique_supplier_wms_id" in str(e):
                    context["error_message"] = (
                        "Supplier with this WMS ID already exists"
                    )
                else:
                    context["error_message"] = (
                        "An error occurred while saving the supplier"
                    )
                return render(request, self.template_name, context)

        return redirect(reverse("delivery:supplier_list"))


class SupplierCreateView(LoginRequiredMixin, View):
    template_name = "delivery/supplier_create.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        wms_id = self.request.POST.get("wms_id")
        name = self.request.POST.get("sup_name")
        context = {"error_message": ""}
        with transaction.atomic():
            try:
                supplier = Supplier(name=name, supplier_wms_id=wms_id)
                supplier.save()
            except IntegrityError as e:
                if "unique_supplier_wms_id" in str(e):
                    context["error_message"] = (
                        "Supplier with this WMS ID already exists"
                    )
                else:
                    context["error_message"] = (
                        "An error occurred while saving the supplier"
                    )
                return render(request, self.template_name, context)

        return redirect(reverse("delivery:supplier_list"))


class ReportListView(LoginRequiredMixin, View):
    template_name = "delivery/report_list.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class SummaryReportOfGoodsView(LoginRequiredMixin, View):
    template_name = "delivery/report_sum_of_goods.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        start_day = self.request.POST.get("start_day")
        finish_day = self.request.POST.get("finish_day")
        recive_location = self.request.POST.get("recive_loc")

        queryset = Delivery.objects.all().select_related(
            "supplier_company", "recive_location", "shop", "location"
        ).filter(complite_status=False)
        if start_day:
            start_day_dt = datetime.strptime(start_day, "%Y-%m-%d")
            queryset = queryset.filter(
                date_recive__date__gte=start_day_dt
                )
        if finish_day:
            finish_day_dt = datetime.strptime(finish_day, "%Y-%m-%d")
            queryset = queryset.filter(
                date_recive__date__lte=finish_day_dt
            )
        if recive_location:
            queryset = queryset.filter(
                recive_location__name = recive_location
                )

        queryset = queryset.annotate(
            days_since_received=ExpressionWrapper(
                    Func(Now(), F('date_recive'), function='AGE'),
                output_field=DateTimeField()
                )
            )
        queryset = queryset.order_by("date_recive")
        write_summary_report_of_goods(queryset)
        return redirect(reverse("delivery:report_list"))


class IrregularityOfTypeView(LoginRequiredMixin, View):
    template_name = "delivery/report_type_of_irregularity.html"

    def get_context_data(self, **kwargs):
        reasones_list = ReasoneComment.objects.all()
        reasones = [{"id": reas.id, "name": reas.name} for reas in reasones_list]

        return {"reasones": reasones}

    def get(self, request, *args, **kwargs):
        reception = self.request.GET.get("reception", None)
        context = self.get_context_data()
        context["reception"] = reception
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        start_day = self.request.POST.get("start_day")
        finish_day = self.request.POST.get("finish_day")
        recive_location = self.request.POST.get("recive_loc")
        reasone = self.request.POST.get("reasones")

        queryset = Delivery.objects.all().select_related(
            "supplier_company", "recive_location", "shop", "location"
        ).filter(complite_status=False)
        if start_day:
            start_day_dt = datetime.strptime(start_day, "%Y-%m-%d")
            queryset = queryset.filter(
                date_recive__date__gte=start_day_dt
                )
        if finish_day:
            finish_day_dt = datetime.strptime(finish_day, "%Y-%m-%d")
            queryset = queryset.filter(
                date_recive__date__lte=finish_day_dt
            )
        if recive_location:
            queryset = queryset.filter(
                recive_location__name = recive_location
                )
        if reasone:
            queryset = queryset.filter(comment__icontains=reasone)
        queryset = queryset.order_by("-date_recive")
        write_irregularity_of_type(queryset)

        return redirect(reverse("delivery:report_list"))

class TotalTransactionReportView(LoginRequiredMixin, View):
    template_name = "delivery/report_total_transaction.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        start_day = self.request.POST.get("start_day")
        finish_day = self.request.POST.get("finish_day")
        transaction = Transaction.objects.all().select_related("delivery")
        if start_day:
            start_day_dt = datetime.strptime(start_day, "%Y-%m-%d")
            transaction = transaction.filter(
                transaction_datetime__date__gte=start_day_dt
            )
        if finish_day:
            finish_day_dt = datetime.strptime(finish_day, "%Y-%m-%d")
            transaction = transaction.filter(
                transaction_datetime__date__lte=finish_day_dt
            )
        write_total_action_count(transaction)

        return redirect(reverse("delivery:report_list"))


class ReadyToShipReportView(LoginRequiredMixin, View):
    template_name = "delivery/report_ready_to_ship.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    
    def post(self, request, *args, **kwargs):
        start_day = self.request.POST.get("start_day")
        finish_day = self.request.POST.get("finish_day")
        recive_location = self.request.POST.get("recive_loc")
        
        transaction = Transaction.objects.all().filter(name="Relocate")\
            .select_related("delivery").filter(delivery__location__work_zone=3)
        if start_day:
            start_day_dt = datetime.strptime(start_day, "%Y-%m-%d")
            transaction = transaction.filter(
                transaction_datetime__date__gte=start_day_dt
            )
        if finish_day:
            finish_day_dt = datetime.strptime(finish_day, "%Y-%m-%d")
            transaction = transaction.filter(
                transaction_datetime__date__lte=finish_day_dt
            )
        if recive_location:
            transaction = transaction.filter(
                delivery__recive_location__name = recive_location
                )
        transaction = transaction.annotate(
            days_since_received=ExpressionWrapper(
                    Func(Now(), F('transaction_datetime'), function='AGE'),
                output_field=DateTimeField()
                )
            ).order_by("-transaction_datetime")
        write_ready_to_ship(transaction)

        return redirect(reverse("delivery:report_list"))

def generate_damage_pdf_report(request):
    # delivery = Delivery.objects.get(id=delivery_id)
    delivery_id = request.POST.get("delivery_number")

    delivery = Delivery.objects.get(id=delivery_id)

    report = gen_pdf_damage_repor(delivery)

    response = FileResponse(report, as_attachment=False, filename="Protokół szkody.pdf")
    return response


def not_used_image_menager(request):
    return render(request, "delivery/not_used_image_menager.html")
