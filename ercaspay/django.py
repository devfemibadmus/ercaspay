import datetime, uuid
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from .models import Transaction
from django.conf import settings
from .main import Ercaspay

DEFAULTS = {
    "ENV": None,
    "TOKEN": None,
    "RSA_KEY": None,
    "CURRENCY": "NGN",
    "ADMIN_SITE": "/",
    "REDIRECT_URL": "/",
    "AUTH_REDIRECT_URL": "auth",
    "PAYMENT_PAGE_NAME": "",
    "PAYMENT_PAGE_DESC": "",
    "NO_PHONE": True
}

ERCASPAY_SETTINGS = {**DEFAULTS, **getattr(settings, "ERCASPAY", {})}
ercaspay = Ercaspay(ERCASPAY_SETTINGS['RSA_KEY'], ERCASPAY_SETTINGS['ENV'], ERCASPAY_SETTINGS['TOKEN'])
website = {'name': ERCASPAY_SETTINGS['PAYMENT_PAGE_NAME'], 'description': ERCASPAY_SETTINGS['PAYMENT_PAGE_DESC'], 'no_phone': ERCASPAY_SETTINGS['NO_PHONE']}

def payment_page(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        full_name = f'{first_name} {last_name}'
        email = request.POST.get('email')
        amount = request.POST.get('amount')
        required_fields = ['first_name', 'last_name', 'email', 'amount']
        phone_number = request.POST.get('phone_number', None)
        if not website['no_phone']:
            required_fields.append('phone_number')
        if not all(request.POST.get(field) for field in required_fields):
            return HttpResponse("Missing fields", status=400)
        auth_url = f'{request.build_absolute_uri()}{ERCASPAY_SETTINGS['AUTH_REDIRECT_URL']}'
        paymentReference = f"{uuid.uuid4().hex}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        response = ercaspay.initiate(amount, full_name, email, paymentReference, None, phone_number, auth_url, currency=ERCASPAY_SETTINGS['CURRENCY'])
        # print(phone_number)
        checkoutUrl = response.get('responseBody', {}).get('checkoutUrl')
        ercaspay_reference = response.get('responseBody', {}).get('transactionReference')
        transaction = Transaction(full_name=full_name, email=email, amount=amount, phone_number=phone_number, payment_reference=paymentReference, ercaspay_reference=ercaspay_reference, currency=ERCASPAY_SETTINGS['CURRENCY'])
        if checkoutUrl is not None:
            transaction.save()
            return redirect(checkoutUrl)
        return HttpResponse(response['explanation'], response['errorCode'])
    return render(request, "payment.html", {'website':website, 'dj': 'dj'})

def auth_page(request):
    trans_ref = request.GET.get('transRef')
    if not trans_ref:
        raise Http404("Transaction not found")
    response = ercaspay.verify(trans_ref)
    if response.get('errorCode'):
        HttpResponse(response['explanation'], status=response['errorCode'])
    status = response.get('responseBody', {}).get('status')
    if status:
        try:
            transaction = Transaction.objects.get(ercaspay_reference=trans_ref)
            transaction.status = status
            transaction.save()
        except Transaction.DoesNotExist:
            raise Http404(f"Transaction not found. status: {status},  ref: {trans_ref}")
        
    return redirect(ERCASPAY_SETTINGS['REDIRECT_URL'])

def redirect_admin(request):
    return redirect(ERCASPAY_SETTINGS['ADMIN_SITE'])
