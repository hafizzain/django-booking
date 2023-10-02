from itertools import islice
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
            csv_file = csv.DictReader(inp_file, delimiter=',')
            countries_objs = []
            for row in csv_file:
                country_instance = Country(
                    name = row['name'],
                    code = row['iso3'],
                    unique_code = row['numeric_code'],
                    unique_id = row['id']
                )
                countries_objs.append(country_instance)
            
            Country.objects.bulk_create(countries_objs)
    print('Countries Created')


def add_states(tenant=None):
    if tenant is None:
        tenant = Tenant.objects.get(schema_name='public')

    with tenant_context(tenant):
        with open('Utility/Files/states.csv', 'r') as inp_file:
            csv_reader = csv.DictReader(inp_file, delimiter=',')
            states_objects = []
            for row in csv_reader:
                state_instance = State(
                    name = row['name'],
                    unique_code = row['state_code'],
                    unique_id = row['id'],
                    country_unique_id = row['country_id']
                )
                states_objects.append(state_instance)
            State.objects.bulk_create(states_objects)

    print('States Created')
    

def add_cities(tenant=None):
    if tenant is None:
        tenant = Tenant.objects.get(schema_name='public')

    with tenant_context(tenant):

        item_count = 0
        batch_size = 1000
        with open('Utility/Files/cities.csv', 'r') as inp_file:
            csv_reader = csv.DictReader(inp_file, delimiter=',')
            cities_objects = []
            for row in csv_reader:
                city_instance = City(
                    country_unique_id = row['country_id'],
                    state_unique_id = row['state_id'],
                    name = row['name'],
                )
                cities_objects.append(city_instance)
                item_count += 1

            print('===> Objects Created')
            City.objects.bulk_create(cities_objects)
            print('Database created')
                
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
            # header = next(reader)
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