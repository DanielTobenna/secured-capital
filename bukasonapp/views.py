from django.shortcuts import render, redirect, reverse

from django.core.mail import BadHeaderError, send_mail

from django.http import HttpResponse,HttpResponseRedirect

from django.contrib import messages

from django.contrib.auth import login, authenticate, logout

from django.contrib.auth.forms import UserCreationForm

from django.core.mail import EmailMessage

from django.conf import settings

from django.template.loader import render_to_string

from .models import *

from .forms import *

from django.contrib.admin.views.decorators import staff_member_required

from django.contrib.auth.decorators import login_required

from django.utils.html import strip_tags

import datetime
import json
import requests
import uuid
import os

# Create your views here.

def home(request):
	return render(request, 'bukasonapp/index.html')

def about(request):
	return render(request, 'bukasonapp/about.html')

def contact(request):
	if request.method == 'GET':
		form= ContactForm()
	else:
		form = ContactForm(request.POST)
		if form.is_valid():
			name= form.cleaned_data['name']
			email= form.cleaned_data['email']
			message = form.cleaned_data['message']

			try:
				send_mail(name, "Investor {} has sent a message saying: {}".format(email, message),email, ['support@Securedcapital-network.com'])
			except BadHeaderError:
				return HttpResponse('Invalid header found.')

			return HttpResponse('Your message has been sent successfully')
	context={'form': form}
	return render(request, 'bukasonapp/contact.html', context)

def services(request):
	return render(request, 'bukasonapp/investment-services.html')

def signin(request):
	if request.user.is_authenticated:
		return redirect('dashboard')

	else:
		if request.method == "POST":
			username= request.POST.get('username')
			password= request.POST.get('password')

			user= authenticate(request, username=username, password=password)

			if user is not None:
				email= User.objects.get(username=username).email
				print(email)
				template= render_to_string('bukasonapp/loginAlert.html', {'name':username})
				email_message= EmailMessage(
					'Login alert on your account!',
					template,
					settings.EMAIL_HOST_USER,
					[email]

					)
				email_message.fail_silently= False
				email_message.send()
				login(request, user)
				return redirect('dashboard')

			else:
				messages.error(request, "username or password is incorrect")

	context={}
	return render(request, 'bukasonapp/login.html')


def main_view(request, *args, **kwargs):
	code= str(kwargs.get('ref_code'))

	try:  
		client = Client.objects.get(code=code)
		request.session['ref_client'] = client.id
		print('id', client.id)
	except:
		pass
	print(request.session.get_expiry_age())

	return render(request, 'bukasonapp/main.html')


def signup(request):
	user_check = request.user.is_authenticated
	if user_check:
		return redirect('dashboard')
	client_id= request.session.get('ref_client')
	print('client_id', client_id)
	form = CreateUserForm(request.POST or None)
	if form.is_valid():
		if client_id is not None:
			recommended_by_client= Client.objects.get(id=client_id)

			instance= form.save()
			registered_user= User.objects.get(id=instance.id)
			registered_client= Client.objects.get(user=registered_user)
			registered_client.recommended_by= recommended_by_client.user
			registered_client.save()

		else:
			form.save()

		username=form.cleaned_data.get('username')
		password= form.cleaned_data.get('password1')
		email= form.cleaned_data.get('email')
		template= render_to_string('bukasonapp/welcomeEmail.html', {'name':username})
		email_message= EmailMessage(
			'Welcome on board to Securedcapital-network!',
			template,
			settings.EMAIL_HOST_USER,
			[email],

			)
		email_message.fail_silently=False
		email_message.send()
		user= authenticate(username=username, password=password)
		login(request, user)
		return redirect('dashboard')
	context={'form':form}
	return render(request, 'bukasonapp/signup.html', context)


def faq(request):
	return render(request, 'bukasonapp/faq.html')

def affiliate(request):
	return render(request, 'empireInvestApp/affiliate.html')

def pricing(request):
	return render(request, 'bukasonapp/pricing.html')


def bounty(request):
	return HttpResponse('bounty')

def terms(request):
	return render(request, 'bukasonapp/terms.html')

def privacy(request):
	return render(request, 'empireInvestApp/privacy.html')


@login_required(login_url='signin')
def dashboard(request):
	client= request.user.client
	client_firstname= request.user.username
	client_email= request.user.email
	client_pk= client.pk
	client_deposit= client.deposit
	client_profit= client.profit
	client_bal= float(client_deposit) + float(client_profit)
	client_withdrawal= client.withdrawal
	client_date_joined= client.created
	client_code= client.code
	client.save()
	context={'client': client, 'client_deposit':client_deposit, 'client_bal':client_bal,'client_profit':client_profit, 'client_date_joined':client_date_joined,
	'client_withdrawal':client_withdrawal, 'client_code':client_code }
	return render(request, 'bukasonapp/dashboard.html', context)

@login_required(login_url='signin')
def deposit(request):
	if request.method=='POST':
		client= request.user.client
		client_username= request.user.username
		client_email= client.email_address
		#post data to create invoice for payment
		price_amount= request.POST.get('price_amount')
		price_currency= "usd"
		pay_currency= request.POST.get('pay_currency')
		order_id= 'assetfussion'
		order_description= "This is a plan subscription"
		if price_amount and pay_currency:
			# Api's url link
			url= 'https://api.nowpayments.io/v1/invoice'
			payload=json.dumps({
				"price_amount": price_amount,
				"price_currency": price_currency,
				"pay_currency": pay_currency,
				"order_id": order_id,
				"order_description": order_description,
				"ipn_callback_url": "https://nowpayments.io",
				"success_url": "https://www.assetfussion.org/",
				#our success url will direct us to the get_payment_status view for balance top ups
				"cancel_url": "https://www.assetfussion.org/dashboard"
			})
			headers={'x-api-key':'8PQRGKC-R7RMZ12-PNSC3P3-2BZTF28', 'Content-Type': 'application/json'}
			response= requests.request('POST', url, headers=headers, data=payload)
			res= response.json()
			generated_link= res["invoice_url"]
			generated_payment_id= res["id"]
			#Now get the user and add the payment ID to the database as we will be using it to know their payment status
			Payment_id.objects.create(
				client=client,
				payment_id= generated_payment_id,
				price_amount= price_amount,
				)
			try:
				send_mail(client_username, "A client with username: {} wants to make a deposit of {}".format(client_username, price_amount),client_email, ['support@Securedcapital-network.com'])
			except BadHeaderError:
				pass
			return redirect(generated_link)
	context={}
	return render(request, 'bukasonapp/deposit.html')

def carddeposit(request):
	return HttpResponse('Currently not available at the moment, please try again later.')

@login_required(login_url='signin')
def withdrawal(request):
	client= request.user.client
	client_id= client.id
	client_username= request.user.username
	client_email= client.email_address
	client_deposit= client.deposit
	client_withdrawal= client.withdrawal
	print(client_deposit)
	client_profit= client.profit
	client_info= Client.objects.filter(id=client_id)
	if request.method =='POST':
		withdrawal_option = request.POST.get('withdrawal_category')
		amount= request.POST.get('amount')
		withdrawal_address= request.POST.get('withdrawal_address')
		crypto= request.POST.get('crypto')
		if withdrawal_option == 'deposit' and float(client_deposit)>10:
			client_deposit_balance= float(client_deposit) - float(amount)
			client_withdrawal_balance= float(client_withdrawal) + float(amount)
			if client_deposit_balance < 0:
				messages.error(request, "Amount requested is greater than deposit")
			else:
				client_update= client_info.update(deposit=client_deposit_balance, withdrawal=client_withdrawal_balance)
				Withdrawal_request.objects.create(
					client= client,
					client_username= client_username,
					client_email= client_email,
					crypto_used_for_requesting_withdrawal= crypto,
					withdrawal_address= withdrawal_address,
					amount= amount
					)
				try:
					send_mail(client_username, "A client with username: {} has requested a withdrawal of {}".format(client_username, amount),client_email, ['support@Securedcapital-network.com'])

				except BadHeaderError:
					return HttpResponse('Something went wrong, please try again later')
				

		if withdrawal_option == 'deposit' and float(client_deposit)<=10:
			messages.error(request, "Your deposit is too low for this withdrawal.")
			
		if withdrawal_option == 'profit' and float(client_profit) > 10:
			client_profit_balance= float(client_profit) - float(amount)
			client_withdrawal_balance= float(client_withdrawal) + float(amount)
			if client_profit_balance < 0:
				messages.error(request, "Amount requested is greater than profit")
			else:
				client_update= client_info.update(profit= client_profit_balance, withdrawal=client_withdrawal_balance)
				Withdrawal_request.objects.create(
					client= client,
					client_username= client_username,
					client_email= client_email,
					crypto_used_for_requesting_withdrawal= crypto,
					withdrawal_address= withdrawal_address,
					amount= amount
					)
				try:
					send_mail(client_username, "A client with username: {} has requested a withdrawal of {}".format(client_username, amount),client_email, ['support@Securedcapital-network.com'])
				except BadHeaderError:
					return HttpResponse('Something went wrong, please try again later')

		if withdrawal_option == 'profit' and float(client_profit) <=10:
			messages.error(request, "Your profit is too low for this withdrawal" )
	context={}
	return render(request, 'bukasonapp/withdrawal.html', context)

def history(request):
	return HttpResponse('history')

def myreferals(request):
	return HttpResponse('my referals')

@login_required(login_url='signin')
@staff_member_required
def confirm_withdrawal(request):
	withdrawalInfo= Withdrawal_request.objects.all()
	context={'withdrawalInfo': withdrawalInfo}
	return render(request, 'bukasonapp/confirmWithdrawal.html', context)

@login_required(login_url='signin')
@staff_member_required
def update_withdrawal(request, pk):
	withdrawalInfo= Withdrawal_request.objects.get(id=pk)
	withdrawalInfo_id= withdrawalInfo.id
	withdrawalInfo_amount= withdrawalInfo.amount
	withdrawal_address= withdrawalInfo.withdrawal_address
	client_id= withdrawalInfo.client.id
	client= Client.objects.get(id=client_id)
	client_bal= client.deposit
	client_name= client.first_name
	client_email= client.email_address
	client_withdrawal= client.withdrawal
	template= render_to_string('bukasonapp/withdrawalEmail.html', {'name': client_name, 'amount':withdrawalInfo_amount, 'wallet_address':withdrawal_address})
	emailmessage= EmailMessage(
		'Congratulations, Your withdrawal request has been approved!',
		template,
		settings.EMAIL_HOST_USER,
		[client_email],
		)
	emailmessage.fail_silently=False
	emailmessage.send()
	delete_withdrawal= withdrawalInfo.delete()
	return HttpResponse('Update withdrawal')

@login_required(login_url='signin')
@staff_member_required
def decline_wihdrawal(request, pk):
	withdrawalInfo= Withdrawal_request.objects.get(id=pk)
	withdrawalInfo_id= withdrawalInfo.id
	withdrawalInfo_amount= withdrawalInfo.amount
	withdrawal_address= withdrawalInfo.withdrawal_address
	client_id= withdrawalInfo.client.id
	client= Client.objects.get(id=client_id)
	client_info= Client.objects.filter(id=client_id)
	client_bal= client.deposit
	client_name= client.first_name
	client_email= client.email_address
	client_withdrawal= client.withdrawal
	client_balance_reup= float(withdrawalInfo_amount) + float(client_bal)
	client_withdrawal_reup= float(client_withdrawal) - float(withdrawalInfo_amount)
	client_info_update= client_info.update(deposit=client_balance_reup, withdrawal=client_withdrawal_reup)
	template= render_to_string('bukasonapp/declineWithdrawalEmail.html', {'name': client_name, 'amount':withdrawalInfo_amount, 'wallet_address':withdrawal_address})
	emailmessage= EmailMessage(
		'Withdrawal request declined!',
		template,
		settings.EMAIL_HOST_USER,
		[client_email],
		)
	emailmessage.fail_silently=False
	emailmessage.send()
	Transaction.objects.create(
		client=client,
		transaction_type='Withdrawal',
		amount= withdrawalInfo_amount,
		status= 'Declined'
		)
	delete_withdrawal= withdrawalInfo.delete()
	return HttpResponse('Withdrawal request declined')


@login_required(login_url='signin')
@staff_member_required
def confirm_deposit(request):
	paymentInfo= Payment_id.objects.all()
	context={'paymentInfo': paymentInfo}
	return render(request, 'bukasonapp/confirmdeposit.html', context)


@login_required(login_url='signin')
@staff_member_required
def update_payment(request, pk):
	payment_info= Payment_id.objects.get(id=pk)
	payment_info_id= payment_info.id
	payment_info_amount= payment_info.price_amount
	client_id= payment_info.client.id
	client= Client.objects.get(id=client_id)
	client_deposit= client.deposit
	client_pk= client.id
	print(client_deposit)
	client_info= Client.objects.filter(id=client_pk)
	newClientbal= float(payment_info_amount) + float(client_deposit)
	update_payment= client_info.update(deposit=newClientbal)
	template= render_to_string('bukasonapp/confirmDepositEmail.html', {'name':client_name, 'amount':payment_info_amount})
	emailmessage= EmailMessage(
		'Congratulations, Your deposit was successful!',
		template,
		settings.EMAIL_HOST_USER,
		[client_email],

		)
	emailmessage.fail_silently=False
	emailmessage.send()

	Transaction.objects.create(
		client=client,
		transaction_type='Deposit',
		amount= payment_info_amount,
		status= 'Approved'
		)
	delete_payment_info= payment_info.delete()
	if update_payment:
		return HttpResponse('Account Updated successfully')
	return HttpResponse('Update payment')

@login_required(login_url='signin')
def account_settings(request):

	client= request.user.client

	form=ClientForm(instance=client)

	if request.method=='POST':
		form= ClientForm(request.POST, request.FILES, instance=client)
		if form.is_valid():
			form.save()

	context= {"form":form}
	return render(request, 'bukasonapp/account_settings.html', context)

def logoutuser(request):
	logout(request)
	return redirect('signin')