from django.urls import path

from . import views

urlpatterns=[
	path('', views.home, name='home'),
	path('about/', views.about, name='about'),
	path('contact/', views.contact, name='contact'),
	path('services/', views.services, name='services'),
	path('signin/', views.signin, name='signin'),
	path('main-view/', views.main_view, name='main-view'),
	path('main-view/<str:ref_code>/', views.main_view, name='main-view'),
	path('signup/', views.signup, name='signup'),
	path('faq/', views.faq, name='faq'),
	path('affiliate/', views.affiliate, name='affiliate'),
	path('pricing/', views.pricing, name='pricing'),
	path('bounty/', views.bounty, name='bounty'),
	path('terms/', views.terms, name='terms'),
	path('privacy/', views.privacy, name='privacy'),
	path('dashboard/', views.dashboard, name='dashboard'),
	path('deposit/', views.deposit, name='deposit'),
	path('carddeposit/', views.carddeposit, name='carddeposit'),
	path('withdrawal/', views.withdrawal, name='withdrawal'),
	path('history/', views.history, name='history'),
	path('myreferals/', views.myreferals, name='myreferals'),
	path('confirm_withdrawal/', views.confirm_withdrawal, name='confirm_withdrawal' ),
	path('update_withdrawal/<str:pk>/', views.update_withdrawal, name='update_withdrawal' ),
	path('decline_wihdrawal/<str:pk>/', views.decline_wihdrawal, name='decline_wihdrawal'),
	path('confirm_deposit/', views.confirm_deposit, name='confirm_deposit' ),
	path('update_payment/<str:pk>/', views.update_payment, name='update_payment' ),
	path('account_settings/', views.account_settings, name='account_settings'),
	path('logout/', views.logoutuser, name='logout')
]