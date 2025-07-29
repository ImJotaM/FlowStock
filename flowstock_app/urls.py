from django.urls import path
from . import views

urlpatterns = [
    path('', views.root_redirect),
    path('home/', views.stock_list, name='home'),
    path('stock/create/', views.create_stock, name='stock-create'),
    path('stock/update/<int:stock_id>/', views.update_stock, name='stock-update'),
    path('stock/delete/<int:stock_id>/', views.delete_stock, name='stock-delete'),
    path('faqs/', views.faqs, name='faqs'),
    path('estoque/<int:stock_id>/', views.stock_detail, name='stock_detail'),
    path('stock/<int:stock_id>/generate-pdf-stock/', views.generate_pdf_stock, name='generate-pdf-stock'),
    path('stock/<int:stock_id>/share/', views.share_stock, name='share-stock'),
    path('groups/create/', views.create_group, name='group-create'),
    path('groups/<int:group_id>/delete/', views.delete_group, name='group-delete'),
    path('groups/<int:group_id>/member/add/', views.add_member_to_group, name='group-add-member'),
    path('groups/<int:group_id>/member/remove/<int:user_id>', views.remove_member_from_group, name='group-remove-member'),
    path('subgroup/<int:subgroup_id>/delete/', views.delete_subgroup, name='subgroup-delete'),
    path('groups/<int:group_id>/member/<int:member_id>/assign/', views.assign_subgroup_to_member, name='member-assign-subgroup'),
    path('groups/member/unassign/', views.unassign_subgroup_from_member, name='member-unassign-subgroup'),
]