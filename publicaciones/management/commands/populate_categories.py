from django.core.management.base import BaseCommand
from publicaciones.models import Category

class Command(BaseCommand):
    help = 'Populate sample categories'

    def handle(self, *args, **options):
        categories = [
            {'name': 'Electrónicos', 'description': 'Dispositivos electrónicos'},
            {'name': 'Ropa', 'description': 'Ropa y accesorios'},
            {'name': 'Hogar', 'description': 'Artículos para el hogar'},
            {'name': 'Deportes', 'description': 'Artículos deportivos'},
        ]
        
        for cat_data in categories:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            if created:
                self.stdout.write(f'Created category: {category.name}')
            else:
                self.stdout.write(f'Category already exists: {category.name}')