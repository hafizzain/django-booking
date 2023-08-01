from django.core.management.base import BaseCommand, CommandError


from Utility.models import ExceptionRecord

import csv

import datetime
import time
class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):
        time_start = datetime.datetime.now()

        state_uni_codes = []

        with open('Utility/Files/states.csv', 'r') as inp_file_state:
            for r_ in inp_file_state:
                r_ = r_.split(',')
                unique_code = r_[0]
                state_uni_codes.append(unique_code)
        
        print(state_uni_codes)

        with open('Utility/Files/cities_copy.csv', 'r') as inp_file:
            with open('Utility/Files/cities.csv', 'w') as output_file:

                output_writer = csv.writer(output_file)

                for row in inp_file:
                    row = row.replace('\n', '').strip()
                    row = row.split(',')
                    state_unique_code = row[2]
                    if state_unique_code in state_uni_codes : 

                        output_writer.writerow(row)
                    
        
        time_end = datetime.datetime.now()
        time_diff = time_end - time_start

        total_seconds = time_diff.total_seconds()

        ExceptionRecord.objects.create(
            text = f'CREATE TENANT TIME DIFF . {total_seconds}'
        )
        self.stdout.write(self.style.SUCCESS(
            'Extracted!!'
        ))
