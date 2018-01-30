from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from analytics.models import Champion
from analytics.api import RiotAPI


class Command(BaseCommand):
    help = 'Update champions'

    def add_arguments(self, parser):
        parser.add_argument('--region', nargs='?', type=str, default='euw1')

    def handle(self, *args, **options):
        api = RiotAPI(options['region'])
        res = api.get_champions().json()

        if 'data' not in res:
            raise CommandError('Error: %s' % res)

        updated = 0
        created = 0

        for champ in res['data'].values():
            self.stdout.write(champ['name'], ending='\r')
            try:
                champion = Champion.objects.get(name=champ['name'])
                champion.name = champ['name']
                champion.champion_id = champ['id']
                champion.title = champ['title']
                champion.save()
                updated += 1
            except ObjectDoesNotExist as e:
                Champion.objects.create(
                    name=champ['name'],
                    champion_id=champ['id'],
                    title=champ['title']
                )
                created += 1

        self.stdout.write(self.style.SUCCESS('Successfully imported. %d updated; %d created' % (updated, created)))
