import json
from datetime import datetime, timedelta

from django.db.models import Count
from django.db.models.functions import Lower, TruncMonth, TruncTime
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from DealsBot.tasks import check_for_deals_and_notify
from .db_utils.db_functions import create_deal
from .models import Profile, TelegramUser, DealSubscription, SentDeal, UserSentDeal, DjangoUserProfile


# Create your views here.
def index(request):
    check_for_deals_and_notify()

    return HttpResponse("Function called.")


# Dashboard
def render_dashboard(request):
    # Get the Count of Sent Deals by Notification Method
    notification_counts = (
        UserSentDeal.objects
        .values_list(
            'notification_method__display_text',
        )
        .annotate(
            count=Count('notification_method')
        )
    )

    notification_counts = dict(notification_counts)

    pie_chart_data = {
        "data": notification_counts
    }

    context = get_context_data()
    context.update(pie_chart_data)

    return render(request, "DealsBot/dashboard/dashboard.html", context)


def get_context_data():
    context = dict()

    # 1. User Statistics
    django_users_count = DjangoUserProfile.objects.count()
    telegram_users_count = TelegramUser.objects.count()
    total_users = django_users_count + telegram_users_count

    # 1.1 User Engagement Over Time: (Line Chart)
    user_growth = (
        DealSubscription.objects
        .annotate(month=TruncMonth('created_on'))
        .values('month')
        .annotate(
            total_users=Count('profile', distinct=True)
        )
        .order_by('month')
    )

    # Format the Data for user_growth
    formatted_data_user_growth = [
        {
            'month': item['month'].strftime('%b %Y'),
            'total_users': item['total_users']
        }
        for item in user_growth
    ]

    # 1.2 Profile Type Distribution (Telegram User, WhatsApp User, Django User etc.)
    profile_type = (
        Profile.objects
        .values('profile_type__model')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    formatted_data_profile_type = [
        {
            'profile_type': ' '.join(word.capitalize() for word in item['profile_type__model'].split('user')),
            'count': item['count']
        }
        for item in profile_type
    ]

    # 2. Subscription and Deal Statistics
    # total_sent_deals = SentDeal.objects.count()
    active_subscriptions_count = DealSubscription.objects.filter(is_active=True).count()
    total_sent_notifications = UserSentDeal.objects.count()

    # 2.1 Prepare the Data for the Active Deals Table
    sent_deals = SentDeal.objects.values().order_by('-valid_from')

    for deal in sent_deals:
        deal['valid_from'] = deal['valid_from'].strftime('%-d %b %Y') if deal else 'No data'
        deal['valid_thru'] = deal['valid_thru'].strftime('%-d %b %Y') if deal else 'No data'
        # Change Display Text for Membership
        if deal['requires_loyalty_membership'] == 'True':
            deal['requires_loyalty_membership'] = 'Yes'
        deal['requires_loyalty_membership'] = 'No'

    # 2.2 Subscriptions By Product (Table)
    active_subscriptions = DealSubscription.objects.filter(is_active=True)

    # Prepare the Data for the Subscription by Product Table
    subscriptions_by_product = (
        active_subscriptions
        .annotate(product_lower=Lower('product'))
        .values('product_lower')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # 2.3 Monthly Sent Deals (Bar Chart)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30 * 5)  # 5: Number of Months to Look Back

    monthly_counts = (
        SentDeal.objects
        .filter(valid_from__gte=start_date)
        .annotate(month=TruncMonth('valid_from'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    # Format the Data for the Chart
    formatted_data_monthly_counts = [
        {
            'month': item['month'].strftime('%b %Y'),
            'count': item['count']
        }
        for item in monthly_counts
    ]

    # 2.4 Sent Deals by Category (Horizontal Line Chart)
    sent_deals_by_category = (
        SentDeal.objects
        .values('category')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # 2.5 Last Sent Deal (Paragraph in the Header)
    last_sent_deal = UserSentDeal.objects.values('date_sent').order_by('-date_sent').first()
    time_last_sent_deal_str = last_sent_deal['date_sent'].strftime(
        '%-d %b %Y at %H:%M:%S') if last_sent_deal else 'No deals sent yet'

    context.update({
        'user_stats': {
            'django_users': django_users_count,
            'telegram_users': telegram_users_count,
            'total_users': total_users,
            'user_growth': list(formatted_data_user_growth),
            'profile_types': list(formatted_data_profile_type)
        },
        'deal_stats': {
            'total_sent_notifications': total_sent_notifications,
            'active_subscriptions_count': active_subscriptions_count,
            'monthly_sent_deals': list(formatted_data_monthly_counts),
            'sent_deals_by_category': list(sent_deals_by_category),
            'time_last_sent_deal_str': time_last_sent_deal_str,
            'active_subscriptions': list(active_subscriptions),
        },
        'subscription_data': list(subscriptions_by_product),
        'sent_deals_data': list(sent_deals),
    })
    return context


@csrf_exempt
def create_deal_endpoint(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Extract and validate required parameters
            profile_id = data.get('profile_id')
            product = data.get('product')
            zipcode = data.get('zipcode')
            communication_channels = data.get('communication_channels')

            if not profile_id:
                return JsonResponse({'error': "'profile_id' must be provided."}, status=400)

            if not product or not zipcode or not communication_channels:
                return JsonResponse({'error': "Missing required fields."}, status=400)

            # Fetch related objects
            try:
                profile = Profile.objects.get(id=profile_id)
            except Profile.DoesNotExist:
                return JsonResponse({'error': 'Profile not found.'}, status=404)

            # Call the `create_deal` function
            created_deal = create_deal(
                profile=profile,
                product=product,
                zipcode=zipcode,
                communication_channels=communication_channels,
            )

            return JsonResponse({
                'message': 'Deal created successfully.',
                'deal_id': created_deal.id
            }, status=201)

        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'An unexpected error occurred.', 'details': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method. Use POST.'}, status=405)
