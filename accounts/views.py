from datetime import datetime, timezone
from django.contrib import auth, messages
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.utils.crypto import get_random_string
from django.core.mail import send_mail

from .decorators import redirect_autheticated_user
from .models import PendingUser, Token, TokenType, User



# accounts/views.py
def home(request):
    return render(request, "home.html")



# -------------------- Login -------------------- #
@redirect_autheticated_user
def login(request: HttpRequest):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = auth.authenticate(request, email=email, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, "You are now logged in.")
            return redirect("browse_jobs")
        else:
            messages.error(request, "Invalid credentials.")
            return redirect("login")

    return render(request, "login.html")


# -------------------- Logout -------------------- #
def logout(request: HttpRequest):
    auth.logout(request)
    messages.success(request, "You are now logged out.")
    return redirect("home")


# -------------------- Register -------------------- #
@redirect_autheticated_user
def register(request: HttpRequest):
    if request.method == "POST":
        email = request.POST["email"].lower()
        password = request.POST["password"]

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect("register")

        verification_code = get_random_string(10)

        # Save pending user with hashed password
        PendingUser.objects.update_or_create(
            email=email,
            defaults={
                "password": make_password(password),
                "verification_code": verification_code,
                "created_at": datetime.now(timezone.utc),
            },
        )

        # Send verification email (to console backend)
        send_mail(
            subject="Verify Your Account",
            message=f"Your verification code is: {verification_code}",
            from_email="noreply@example.com",
            recipient_list=[email],
        )

        messages.success(request, f"Verification code sent to {email}")
        return render(request, "verify_account.html", {"email": email})

    return render(request, "register.html")


# -------------------- Verify Account -------------------- #
def verify_account(request: HttpRequest):
    if request.method == "POST":
        code = request.POST["code"]
        email = request.POST["email"]

        pending_user = PendingUser.objects.filter(
            verification_code=code, email=email
        ).first()

        if pending_user and pending_user.is_valid():
            # ✅ Create actual user with existing hashed password
            user = User.objects.create(email=pending_user.email)
            user.password = pending_user.password  # keep hashed password
            user.save()

            pending_user.delete()
            auth.login(request, user)
            messages.success(request, "Account verified. You are now logged in.")
            return redirect("home")

        else:
            messages.error(request, "Invalid or expired verification code.")
            return render(request, "verify_account.html", {"email": email}, status=400)

    return redirect("register")


# -------------------- Forgot Password -------------------- #
def send_password_reset_link(request: HttpRequest):
    if request.method == "POST":
        email = request.POST.get("email", "").lower()
        user = get_user_model().objects.filter(email=email).first()

        if not user:
            messages.error(request, "Email not found.")
            return redirect("reset_password_via_email")

        # Create or update token
        token, _ = Token.objects.update_or_create(
            user=user,
            token_type=TokenType.PASSWORD_RESET,
            defaults={
                "token": get_random_string(20),
                "created_at": datetime.now(timezone.utc),
            },
        )

        reset_link = f"http://127.0.0.1:8000/auth/reset-password-confirm/?email={email}&token={token.token}"

        send_mail(
            subject="Your Password Reset Link",
            message=f"Click the link below to reset your password:\n{reset_link}",
            from_email="noreply@example.com",
            recipient_list=[email],
        )

        messages.success(request, "Reset link sent to your email (check terminal).")
        return redirect("reset_password_via_email")

    return render(request, "forgot_password.html")


# -------------------- Verify Password Reset Link -------------------- #
def verify_password_reset_link(request: HttpRequest):
    email = request.GET.get("email")
    reset_token = request.GET.get("token")

    token = Token.objects.filter(
        user__email=email,
        token=reset_token,
        token_type=TokenType.PASSWORD_RESET,
    ).first()

    if not token or not token.is_valid():
        messages.error(request, "Invalid or expired reset link.")
        return redirect("reset_password_via_email")

    return render(
        request,
        "set_new_password_using_reset_token.html",
        {"email": email, "token": reset_token},
    )


def set_new_password(request: HttpRequest):
    """
    Accepts POST from the reset form (password1, password2, email, token).
    Verifies token, compares passwords, sets hashed password and deletes token.
    """

    if request.method == "POST":
        email = request.POST.get("email")
        token_value = request.POST.get("token")
        password1 = request.POST.get("password1")  # matches template fields
        password2 = request.POST.get("password2")

        # Basic validations
        if not (email and token_value):
            messages.error(request, "Invalid request. Missing email or token.")
            return redirect("reset_password_via_email")

        if not password1 or not password2:
            messages.error(request, "Both password fields are required.")
            return render(
                request,
                "set_new_password_using_reset_token.html",
                {"email": email, "token": token_value},
                status=400,
            )

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(
                request,
                "set_new_password_using_reset_token.html",
                {"email": email, "token": token_value},
                status=400,
            )

        # Find token and user
        try:
            t = Token.objects.get(
                token=token_value,
                user__email=email,
                token_type=TokenType.PASSWORD_RESET,
            )
        except Token.DoesNotExist:
            messages.error(request, "Invalid or expired link.")
            return redirect("reset_password_via_email")

        if not t.is_valid():
            messages.error(request, "Link expired.")
            return redirect("reset_password_via_email")

        # Set the hashed password correctly
        user = t.user
        user.set_password(password1)
        user.save()

        # Delete token to prevent re-use
        t.delete()

        messages.success(request, "Password reset successfully. Please log in.")
        return redirect("login")

    # If someone accesses set-new-password via GET directly, redirect to forgot page
    return redirect("reset_password_via_email")


# -------------------- Helper Function -------------------- #
def send_verification_email(email, code):
    subject = "Your Verification Code"
    message = f"Your verification code is: {code}"
    from_email = "noreply@example.com"
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)
