from django.shortcuts import redirect

def redirect_to_detail_view(request):
    return redirect('homepageapp:main')