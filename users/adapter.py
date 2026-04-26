from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.utils.text import slugify
import uuid

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        """
        Hook that can be used to further populate the user instance.
        
        For Google Auth users, we need to ensure they have a unique nickname
        since 'nickname' is a required field in our custom User model.
        """
        user = super().populate_user(request, sociallogin, data)
        
        # If user.nickname is already set (e.g. by form input or previous logic), skip
        if user.nickname:
            return user
            
        # Try to use 'name' or 'first_name' from Google data
        first_name = data.get('first_name') or data.get('name', '').split(' ')[0]
        email = data.get('email', '')
        
        if first_name:
            base_nickname = first_name
        elif email:
            base_nickname = email.split('@')[0]
        else:
            base_nickname = "User"
            
        # Ensure nickname is unique
        current_nickname = slugify(base_nickname)
        
        # Check if nickname exists and modify if needed
        # Note: We can't check database easily here without importing User model which might cause issues inside populate_user if used early.
        # But populate_user usually runs before save.
        # Let's try to make it reasonably unique by appending 4 random chars if needed later or just rely on slugify for now.
        
        # Better approach: Append random string to ensure uniqueness for social logins
        # Since we don't have a registration form step where user picks it.
        random_suffix = str(uuid.uuid4())[:4]
        user.nickname = f"{current_nickname}_{random_suffix}"
            
        return user

from allauth.account.adapter import DefaultAccountAdapter
from core.services.email_service import EmailService
from django.contrib.auth import get_user_model

class CustomAccountAdapter(DefaultAccountAdapter):
    def send_mail(self, template_prefix, email, context):
        User = get_user_model()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = context.get('user')
            if not user:
                return super().send_mail(template_prefix, email, context)

        if template_prefix == 'account/email/password_reset_key':
            reset_url = context.get('password_reset_url')
            EmailService.send_password_reset_email(user, reset_url)
            return

        return super().send_mail(template_prefix, email, context)
