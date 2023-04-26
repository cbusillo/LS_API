"""backend for datatable of customers""" ""
from ajax_datatable.views import AjaxDatatableView
from django.urls import reverse
from django.db.models.functions import Lower
from django.db import models

from .models import Customer


class CustomerTable(AjaxDatatableView):
    """backend for datatable of customers"""

    model = Customer
    initial_order = [["update_time", "desc"]]
    length_menu = [[10, 20, 50, 100, -1], [10, 20, 50, 100, "all"]]
    show_column_filters = True
    column_defs = [
        AjaxDatatableView.render_row_tools_column_def(),
        {"name": "id", "visible": False, "searchable": False},
        {"name": "last_name", "visible": True},
        {"name": "first_name", "visible": True},
        # {"name": "mobile_number", "title": "Cell", "visible": True, "searchable": False},
        {"name": "number", "m2m_foreign_field": "phones__number", "title": "Phone Numbers", "visible": True, "searchable": True},
        {
            "name": "serial_number",
            "m2m_foreign_field": "serials__serial_number",
            "title": "Serial",
            "visible": False,
            "searchable": True,
        },
        {"name": "address", "m2m_foreign_field": "emails__address", "title": "Email Addresses", "visible": True, "searchable": True},
        {"name": "update_time", "visible": False, "searchable": False, "orderable": True},
        {
            "name": "create_workorder_button",
            "title": "Workorder",
            "placeholder": True,
            "visible": True,
            "searchable": False,
            "orderable": False,
        },
    ]

    def sort_queryset(self, params, qs):
        if len(params["orders"]):
            order_modes = []
            for order in params["orders"]:
                order_mode = order.get_order_mode()
                if isinstance(order.column_link._model_column.model_field, models.CharField):  # pylint: disable=protected-access
                    if order_mode[:1] == "-":
                        order_modes.append(Lower(order_mode[1:]).desc())
                    else:
                        order_modes.append(Lower(order_mode))
                else:
                    order_modes.append(order_mode)
            qs = qs.order_by(*order_modes)
        return qs

    def get_initial_queryset(self, request=None):
        queryset = self.model.objects.filter(archived=False)

        queryset = queryset.distinct()
        return queryset

    # def render_row_details(self, pk, request=None):
    #     workorders = [workorder for workorder in self.model.objects.get(pk=pk).workorders.all()]
    #     return render_to_string("ajax_datatable/customers/render_row_details.html", {"workorders": workorders})

    def customize_row(self, row, obj):
        create_workorder_url = reverse("workorders:create_workorder")
        button = (
            f'<button class="btn btn-secondary btn-xs create-workorder-btn" '
            f'data-customer-id="{obj.id}" '
            f'data-url="{create_workorder_url}">New</button>'
        )
        row["create_workorder_button"] = button
        return row
