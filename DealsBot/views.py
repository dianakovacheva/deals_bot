import json

from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from DealsBot.tasks import check_for_deals_and_notify
from .db_utils.db_functions import create_deal
from .models import Profile, BotUser, DealSubscription


# Create your views here.
def index(request):
    check_for_deals_and_notify()

    return HttpResponse("Function called.")


@csrf_exempt  # Disable CSRF for testing, ensure proper security measures later
def create_deal_endpoint(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Extract and validate required parameters
            profile_id = data.get('profile_id')
            bot_user_id = data.get('bot_user_id')
            product = data.get('product')
            zipcode = data.get('zipcode')
            communication_channels = data.get('communication_channels')

            if not (profile_id or bot_user_id):
                return JsonResponse({'error': "Either 'profile_id' or 'bot_user_id' must be provided."}, status=400)

            if not product or not zipcode or not communication_channels:
                return JsonResponse({'error': "Missing required fields."}, status=400)

            # Fetch related objects
            profile = Profile.objects.get(id=profile_id) if profile_id else None
            bot_user = BotUser.objects.get(telegram_user_id=bot_user_id) if bot_user_id else None

            # Call the `create_deal` function
            created_deal = create_deal(
                profile=profile,
                bot_user=bot_user,
                product=product,
                zipcode=zipcode,
                communication_channels=communication_channels,
            )

            return JsonResponse({
                'message': 'Deal created successfully.',
                'deal_id': created_deal.id
            }, status=201)

        except Profile.DoesNotExist:
            return JsonResponse({'error': 'Profile not found.'}, status=404)
        except BotUser.DoesNotExist:
            return JsonResponse({'error': 'BotUser not found.'}, status=404)
        except DealSubscription.DoesNotExist:
            return JsonResponse({'error': 'Product not found.'}, status=404)
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'An unexpected error occurred.', 'details': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method. Use POST.'}, status=405)
