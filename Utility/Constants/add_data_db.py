

import csv, json
from Business.models import BusinessType
from Tenants.models import Tenant
from Utility.models import Country, Software, State, City, Currency, Language

from django_tenants.utils import tenant_context


def add_business_types(tenant=None):
    if tenant is None:
        tenant = Tenant.objects.get(schema_name='public')

    with tenant_context(tenant):
        with open('Utility/Files/business_types.json', 'r') as inp_file:
            file = json.load(inp_file)
            bs_types_objs = []
            for row in file:
                bd_type = BusinessType(
                    name = row['name'],
                    image_path = row['image'],
                    slug = row['slug']
                )
                bs_types_objs.append(bd_type)

            BusinessType.objects.bulk_create(bs_types_objs)

def add_software_types(tenant=None):
    if tenant is None:
        tenant = Tenant.objects.get(schema_name='public')

    with tenant_context(tenant):
        with open('Utility/Files/software_types.json', 'r') as inp_file:
            file = json.load(inp_file)
            softwares_objs = []
            for row in file:
                sf_type = Software(
                    name = row['name'],
                )
                softwares_objs.append(sf_type)
            
            Software.objects.bulk_create(softwares_objs)


def add_countries(tenant=None):
    if tenant is None:
        tenant = Tenant.objects.get(schema_name='public')

    with tenant_context(tenant):
        with open('Utility/Files/countries.csv', 'r') as inp_file:
            countries_objs = []
            for row in inp_file:
                unique_code = row.split(',')[0]
                code = row.split(',')[1]
                name = row.split(',')[2].replace('\n', '').strip()
                country_instance = Country(
                    name = name,
                    code = code,
                    unique_code = unique_code
                )
                countries_objs.append(country_instance)
                print(f'Added Country {name} ...')
            
            Country.objects.bulk_create(countries_objs)
    print('Countries Created')


def add_states(tenant=None):
    if tenant is None:
        tenant = Tenant.objects.get(schema_name='public')

    with tenant_context(tenant):
        with open('Utility/Files/states.csv', 'r') as inp_file:
            states_objects = []
            for row in inp_file:
                row = row.split(',')
                unique_code = row[0]
                name = row[1]
                country_unique_code = row[2].replace('\n', '').strip()
                country = Country.objects.get(
                    unique_code=country_unique_code
                )

                state_instance = State(
                    country = country,
                    name = name,
                    unique_code = unique_code,
                )
                states_objects.append(state_instance)
                print(f'Added State {name} ...')
            
            State.objects.bulk_create(states_objects)

    print('States Created')
    

def add_cities(tenant=None):
    if tenant is None:
        tenant = Tenant.objects.get(schema_name='public')

    with tenant_context(tenant):
        with open('Utility/Files/cities.csv', 'r') as inp_file:
            cities_objects = []
            for index, row in enumerate(inp_file):
                unique_code = row.split(',')[0]
                name = row.split(',')[1]
                state_unique_code = row.split(',')[2].replace('\n', '').strip()

                state = State.objects.get(
                    unique_code=state_unique_code
                )
                city_instance = City(
                    country = state.country,
                    state = state,
                    name = name,
                    unique_code = unique_code
                )
                cities_objects.append(city_instance)
                print(f'Added City {index} ...')
            
            City.objects.bulk_create(cities_objects)

    print('Cities Created')


def add_currencies(tenant=None):
    if tenant is None:
        tenant = Tenant.objects.get(schema_name='public')

    with tenant_context(tenant):

        with open('Utility/Files/Currencies.csv', 'r') as f:
            reader = csv.reader(f)
            header = next(reader)
            currencies_objs = []
            for i in reader:
                try:
                    Currency.objects.get(name=i[0])
                except:
                    crc_obj = Currency(
                            name=i[0],
                            code=i[1],
                            symbol=i[2]
                        )
                    currencies_objs.append(crc_obj)
            
            Currency.objects.bulk_create(currencies_objs)

def add_languages(tenant=None):
    if tenant is None:
        tenant = Tenant.objects.get(schema_name='public')

    with tenant_context(tenant):

        with open('Utility/Files/languages.csv', 'r') as f:
            reader = csv.reader(f)
            header = next(reader)
            langs_objs = []
            for i in reader:
                try:
                    language = Language.objects.get(
                            code = i[1],
                        )
                except:
                    language = Language(
                        code = i[1],
                        name = i[2]
                    )
                    langs_objs.append(language)

            Language.objects.bulk_create(langs_objs)