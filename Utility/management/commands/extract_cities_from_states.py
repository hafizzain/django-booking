from django.core.management.base import BaseCommand, CommandError



import csv

class Command(BaseCommand):
    # Handle method to handle out the process of creating the admin user
    def handle(self, *args, **options):

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


        self.stdout.write(self.style.SUCCESS(
            'Extracted!!'
        ))
