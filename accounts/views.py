from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def profile_view(request):
    """
    Eenvoudige profielpagina voor de ingelogde gebruiker.
    """
    user = request.user
    # Je kan dit later uitbreiden met statistieken, aantal notes, enz.
    return render(
        request,
        "accounts/profile.html",
        {
            "user_obj": user,
        },
    )
