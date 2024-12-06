from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Event
from .forms import EventForm
from .mpesa_utils import lipa_na_mpesa

from django.core.paginator import Paginator
from django.shortcuts import render
from.models import Event

def event_list(request):
    events = Event.objects.all().order_by('-date')
    paginator = Paginator(events, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'event_list.html', {'page_obj': page_obj})

@csrf_exempt
def mpesa_callback(request):


    if request.method == 'POST':
        data = request.body
        return JsonResponse({"status": "success"})


def process_payment(request):

    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        amount = request.POST.get('amount')
        response = lipa_na_mpesa(phone_number, amount)
        return JsonResponse(response)
    return render(request, 'process_payment.html')


def redirect_to_event_new(request):
    return redirect('event_create')
def register(request):

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful. You can now log in.")
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


@login_required(login_url='login')
def event_list(request):

    query = request.GET.get('q', '')
    if query:
             events = Event.objects.filter(name__icontains=query) | Event.objects.filter(description__icontains=query) if query else Event.objects.all()
    else:
         events = Event.objects.all()
    paginator = Paginator(events, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'event_list.html', {'page_obj': page_obj, 'query': query,'events':events})


@login_required
def event_detail(request, pk):

    event = get_object_or_404(Event, pk=pk)
    return render(request, 'event_detail.html', {'event': event})


@login_required
def event_create(request):

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            form.instance.created_by = request.user
            form.save()
            messages.success(request, 'Event created successfully!')
            return redirect('event_list')
    else:
        form = EventForm()
    return render(request, 'event_form.html', {'form': form})


@login_required
def event_update(request, pk):

    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully!')
            return redirect('event_list')
    else:
        form = EventForm(instance=event)
    return render(request, 'event_form.html', {'form': form})


@login_required
def event_delete(request, pk):


    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted successfully!')
        return redirect('event_list')
    return render(request, 'event_confirm_delete.html', {'event': event})
