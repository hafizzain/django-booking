

import csv
from Tenants.models import Tenant
from Utility.models import Country, State, City, Currency, Language

from django_tenants.utils import tenant_context

def add_countries(tenant=None):
    if tenant is None:
        tenant = Tenant.objects.get(schema_name='public')

    with tenant_context(tenant):
        with open('Utility/Files/countries.csv', 'r') as inp_file:
            for row in inp_file:
                unique_code = row.split(',')[0]
                code = row.split(',')[1]
                name = row.split(',')[2].replace('\n', '').strip()
                Country.objects.create(
                    name=name,
                    code=code,
                    unique_code=unique_code
                )
                print(f'Added Country {name} ...')
    print('Countries Created')


def add_states(tenant=None):
    if tenant is None:
        tenant = Tenant.objects.get(schema_name='public')

    with tenant_context(tenant):
        with open('Utility/Files/states.csv', 'r') as inp_file:
            for row in inp_file:
                row = row.split(',')
                unique_code = row[0]
                name = row[1]
                country_unique_code = row[2].replace('\n', '').strip()
                country = Country.objects.get(
                    unique_code=country_unique_code
                )

                State.objects.create(
                    country=country,
                    name=name,
                    unique_code=unique_code,
                )
                print(f'Added State {name} ...')

    print('States Created')
    

def add_cities(tenant=None):
    if tenant is None:
        tenant = Tenant.objects.get(schema_name='public')

    with tenant_context(tenant):
        with open('Utility/Files/cities.csv', 'r') as inp_file:
            for index, row in enumerate(inp_file):
                unique_code = row.split(',')[0]
                name = row.split(',')[1]
                state_unique_code = row.split(',')[2].replace('\n', '').strip()

                state = State.objects.get(
                    unique_code=state_unique_code
                )
                City.objects.create(
                    country=state.country,
                    state=state,
                    name=name,
                    unique_code=unique_code
                )
                print(f'Added City {index} ...')

    print('Cities Created')


def add_currencies(tenant=None):
    if tenant is None:
        tenant = Tenant.objects.get(schema_name='public')

    with tenant_context(tenant):

        with open('Utility/Files/Currencies.csv', 'r') as f:
            reader = csv.reader(f)
            header = next(reader)
            for i in reader:
                try:
                    Currency.objects.get(name=i[0])
                except:
                    crc_obj = Currency.objects.create(
                            name=i[0],
                            code=i[1]
                        )
                    print(crc_obj)

def add_languages(tenant=None):
    if tenant is None:
        tenant = Tenant.objects.get(schema_name='public')

    with tenant_context(tenant):

        with open('Utility/Files/languages.csv', 'r') as f:
            reader = csv.reader(f)
            header = next(reader)
            for i in reader:
                try:
                    language = Language.objects.get(
                            code = i[1],
                        )
                except:
                    language = Language.objects.create(
                        code = i[1],
                        name = i[2]
                    )
                    print(language)