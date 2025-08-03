from django.core.management.base import BaseCommand
class Command(BaseCommand):
    help="Test command"
    def handle(self,*args,**options):
        print("Test command works!")
