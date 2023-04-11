from django.core.paginator import Paginator
from django.shortcuts import render
from django.views import View

from .models import Workorder


class WorkorderListView(View):
    """View for listing items"""

    def get(self, request):
        """Create form on GET request and list items"""

        workorder = Workorder.objects.all()

        paginator = Paginator(workorder, 25)  # Show 25 items per page.
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        return render(request, "workorders/workorder_list.html", {"page_obj": page_obj})
