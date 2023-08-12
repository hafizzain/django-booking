from django.core.management.base import BaseCommand, CommandError



from Authentication.models import User
from Tenants.models import Tenant, Domain

class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):

        user = User.objects.create_superuser(
            email = 'admin@gmail.com',
            username = 'admin',
            password = 'admin'
        )

        public_schema, created = Tenant.objects.get_or_create(
            schema_name = 'public',
        )
        public_schema.user = user
        public_schema.domain = 'localhost'
        public_schema.name = 'admin'
        public_schema.business_id = 'Nothing'
        public_schema.is_active = True
        public_schema.is_ready = True
        public_schema.save()

        Domain.objects.create(
            user = user,
            domain = 'localhost',
            tenant = public_schema,
            schema_name = 'public',
            is_active = True
        )

        self.stdout.write(self.style.SUCCESS('Completed'))
