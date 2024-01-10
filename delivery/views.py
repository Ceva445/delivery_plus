from django.shortcuts import render, redirect
from .models import Delivery
from django.views import View


def delivery_create(request):
    # if request.method == 'POST':
    #     # Extract data from the request
    #     supplier_company_id = request.POST.get('supplier_company')
    #     nr_order = request.POST.get('nr_order')
    #     ssc_barcode = request.POST.get('ssc_barcode')
    #     images_url = request.FILES.get('images_url')
    #     comment = request.POST.get('comment')
    #     recive_location_id = request.POST.get('recive_location')
    #     location_id = request.POST.get('location')
 
    #     # Create a new Delivery instance
    #     # delivery = Delivery.objects.create(
    #     #     supplier_company_id=supplier_company_id,
    #     #     nr_order=nr_order,
    #     #     ssc_barcode=ssc_barcode,
    #     #     images_url=images_url,
    #     #     comment=comment,
    #     #     recive_location_id=recive_location_id,
    #     #     location_id=location_id,
    #     #     user=request.user  # Assuming you have a logged-in user
    #     # )

    #     # Redirect to a success page or do something else
    #     return redirect('delivery/create_delivery.html')
    # else:
    #     # Render the initial form
    #     return render(request, 'delivery/create_delivery.html')
    
    
    
    return render(request, 'delivery/create_delivery.html')


class DeliveryCreateView(View):
    template_name = 'delivery/create_delivery.html'

    def get_context_data(self, **kwargs):
        # Dummy data for testing
        suppliers = [
            {'id': 1, 'name': 'Supplier A'},
            {'id': 2, 'name': 'Supplier B'},
            {'id': 3, 'name': 'Supplier C'},
        ]

        reasones = [
            {'id': 1, 'name': 'Reasone 1'},
            {'id': 2, 'name': 'Reasone 2'},
            {'id': 3, 'name': 'Reasone 3'},
        ]
        return {
            'suppliers': suppliers, 
            "reasones": reasones
            }

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)