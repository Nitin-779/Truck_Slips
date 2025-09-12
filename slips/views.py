from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User
from .models import Slips
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth import logout as logout_auth
from django.contrib.auth import login,authenticate
from django.contrib import messages
from django.http import HttpResponseForbidden
from collections import defaultdict
from django.db.models import Count
# Create your views here.


from django.core.files.storage import default_storage
from django.http import JsonResponse

def test_storage(request):
    return JsonResponse({
        "storage_backend": str(default_storage.__class__),
    })


def index_view(request):
    return render(request,"index.html")

def login_view(request):
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        role=request.POST.get('role')
                
        user=authenticate(request,username=username,password=password)
        if user:
            login(request,user)
            return redirect('index_view')
        else:
            messages.error(request,'Invalid username or password')
    return render(request, 'login.html')


def signup(request):
    if request.method=='POST':
        username = request.POST.get('username')
        email=request.POST.get('email')
        password=request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password!=confirm_password:
            messages.error(request,"Passwords do not match")
            # return redirect('signup')

        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            # return redirect('signup')

        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            # return redirect('signup')

        else:
            try:
                validate_password(password)
                user=User.objects.create_user(
                    username=username,email=email,password=password)
                messages.success(
                    request, 'Registration successful! You can now login.')
                return redirect('login')
            
            except ValidationError as e:
                for error in e:
                    messages.error(request,error)

    return render(request, 'signup.html')


@login_required
def logout(request):
    logout_auth(request)
    messages.success(request,"You have been logged out successfully.")
    return redirect('index_view')


@login_required
def admin_dashboard_view(request):
    total_users=User.objects.all().count()

    context={
        'total_users':total_users,
    }
    return render(request,'admin_dashboard.html',context)


@login_required
def manage_users_view(request):
    if not request.user.is_superuser:
        messages.error(request,"Access denied. Admin privileges required.")
        return redirect('index_view')
    
    users=User.objects.all()
    if not users:
        messages.info(request,"No users found in the system.")
    return render(request,'manageUsers.html',{'users':users})

@login_required
def delete_user_view(request,user_id):
    if not request.user.is_superuser:
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('index_view')
    
    try:
        user = User.objects.get(pk=user_id)
        if user.is_superuser:
            messages.error(request, "Cannot delete a superuser.")
        else:
            user.delete()
            messages.success(request, "User deleted successfully.")
    except User.DoesNotExist:
        messages.error(request, "User does not exist.")

    return redirect('manage_users')



from django.contrib.auth.decorators import login_required

@login_required
def upload_slip(request):
    if request.method == 'POST' and request.FILES.get('slip'):
        slip_file = request.FILES['slip']
        location = request.POST.get('location')

        if location:
            # Create Slip record including location
            slip = Slips.objects.create(
                user=request.user,
                file=slip_file,
                file_name=slip_file.name,
                location=location
            )

            is_image = slip.file.name.lower().endswith(('.jpg', '.jpeg', '.png'))

            return render(request, 'index.html', {
                'uploaded_file_url': slip.file.url,
                'is_image': is_image,
                'message': 'File uploaded successfully!'
            })

        else:
            # Handle missing location
            return render(request, 'index.html', {
                'error': 'Please select a location.'
            })

    return render(request, 'index.html')



@login_required
def user_slips(request):
    """Show slips uploaded by the logged-in user"""
    slips = Slips.objects.filter(user=request.user).order_by('-uploaded_at')
    return render(request, 'user_slips.html', {'slips': slips})


@login_required
@user_passes_test(lambda u: u.is_staff)  # restrict to staff/admin
def admin_slips_view(request):
    """Show all slips for admin view"""
    slips = Slips.objects.all().order_by('-uploaded_at')
    return render(request, 'admin_slips.html', {'slips': slips})

@login_required
@user_passes_test(lambda u: u.is_staff)
def approve_slip(request, slip_id):
    slip = get_object_or_404(Slips, id=slip_id)
    slip.status = 'approved'
    slip.save()
    return redirect('admin_slips_locations')  # Redirect back to the dashboard


@login_required
@user_passes_test(lambda u: u.is_staff)
def reject_slip(request, slip_id):
    slip = get_object_or_404(Slips, id=slip_id)
    slip.status = 'rejected'
    slip.save()
    return redirect('admin_slips_locations')  # Redirect back to the dashboard


@login_required
def delete_slip(request, slip_id):
    slip = get_object_or_404(Slips, id=slip_id)

    # Admin can delete any slip, user can delete their own slip
    if request.user.is_staff or slip.user == request.user:
        slip.delete()
    else:
        return HttpResponseForbidden("You are not allowed to delete this slip.")

    # Redirect appropriately
    if request.user.is_staff:
        return redirect('admin_slips_locations')  # Admin dashboard
    else:
        return redirect('user_slips')  # User dashboard
    
    
#  View: Show all Locations
@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_location_view(request):
    # Get unique locations with slip counts
    locations = Slips.objects.values('location').annotate(slips_count=Count('id'))
    
    return render(request, 'admin_slips_locations.html', {'locations': locations})



# View: Show Slips for a Specific Location
@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_slips_by_location_view(request, location):
    slips = Slips.objects.filter(location=location).order_by('-uploaded_at')
    return render(request, 'admin_slips_by_location.html', {
        'location': location,
        'slips': slips
    })