# create_superuser.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finance_pwa.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

if not User.objects.filter(username='admin').exists():
    print("Criando superusuário padrão...")
    User.objects.create_superuser(
        username='cashpilotadmin',
        email='b.hsantossdg@gmail.com',
        password=os.getenv('SUPERUSER_PASSWORD')
    )
else:
    print("Superusuário já existe.")