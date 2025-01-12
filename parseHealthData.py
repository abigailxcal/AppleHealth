import xml.etree.ElementTree as ET
import pprint
import matplotlib.pyplot as plt
from datetime import datetime
import re
import csv
import pandas as pd

# [('type', 'HKQuantityTypeIdentifierHeartRate'), ('sourceName', 'Abigail’s Apple\xa0Watch'), ('sourceVersion', '10.5'), ('device', '<<HKDevice: 0x3027f64e0>, name:Apple Watch, manufacturer:Apple Inc., model:Watch, hardware:Watch6,10, software:10.5, creation date:2024-07-05 09:25:20 +0000>'), ('unit', 'count/min'), ('creationDate', '2024-11-01 05:33:18 -0800'), ('startDate', '2024-11-01 05:25:46 -0800'), ('endDate', '2024-11-01 05:25:46 -0800'), ('value', '65')]
class Health_Parser:

    PATH_TO_XML = "/Users/abigailcalderon/Downloads/apple_health_export/export.xml"

    def __init__(self):
        self.tree = ET.parse(self.PATH_TO_XML)
        self.root = self.tree.getroot()
        self.get_all_types()

    # creates a seperate csv for each selected type
    def create_csv(self,selection):
        records = self.get_selected_type(selection)

        # using pandas just for this method right now. may integrate pandas into 
        # other methods later
        df = pd.DataFrame(records) 
        type_str = str(self.type_dict[selection])
        identifier = self.extract_identifier(type_str)
        csv_filename = "apple_health"+identifier+".csv"
        df.to_csv(csv_filename, index=False)
        print(f"{csv_filename} created")
        
        

    def extract_identifier(self,type_str):
        pattern = r"[\w]+Identifier(.*)"
        match = re.search(pattern,type_str)
        result = match.group(1)
        return result

        

    def get_all_types(self):
        self.type_values = set()
        for record in self.root.findall('.//Record'):
            type_attribute = record.get('type')
            if type_attribute:
                self.type_values.add(type_attribute)
        self.type_dict = {idx:type for idx,type in enumerate(sorted(self.type_values)) }
       
    def print_all_types(self):
        [print(f'{idx}: {type}') for idx,type in self.type_dict.items()]

    def get_selected_type(self,selection):
        print(f'Showing data for {self.type_dict[selection]}')
        records = []
        type_str = str(self.type_dict[selection])
        identifier = self.extract_identifier(type_str)
        selected_type = ".//Record[@type='"+self.type_dict[selection]+"']"
        for record in self.root.findall(selected_type):
            # print(record.items())
            records.append({
                'type':record.get('type'),
                'type_name':identifier,
                'start_date': record.get('startDate'),
                'end_date': record.get('endDate'),
                'value': record.get('value'),
                'unit': record.get('unit'),
            })
        print(len(records))
        pprint.pprint(records[:10])
        return records

    def graph_selected_type(self,selection):
        try:
            print(f'Graphing data for {self.type_dict[selection]}')
            type_str = str(self.type_dict[selection])
            pattern = r"HKQuantityTypeIdentifier(.*)"
            match = re.search(pattern,type_str)
            result = match.group(1)
            print("match: " ,result)
            unit = None
            records = []
            selected_type = ".//Record[@type='"+self.type_dict[selection]+"']"
            for record in self.root.findall(selected_type):
                start_date = record.get('startDate')
                value = float(record.get('value'))
                date_obj= datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S %z')
                records.append((date_obj, value))
                unit = record.get("unit")
            #print(records)
            #pprint.pprint(records[:10])
    
            records.sort(key=lambda x: x[0])
            #print("sorted ",records)
            dates = []
            cumulative_val = []
            total = []
            count = 1
            prev_date = None

            for record in records:
                date, vals = record
                total.append(vals)
                if prev_date == None:
                    pass
                elif date.date()!=prev_date:
                    dates.append(date)
                    average = sum(total)/(len(total)+1)
                    cumulative_val.append(average)
                    total = []
                total.append(vals)
                prev_date = date.date()
            plt.figure(figsize=(10,6))
            plt.plot(dates,cumulative_val, linestyle='-', color='blue')
            plt.xlabel('Date')
            plt.ylabel(f'{result} ({unit})')
            plt.title("Average "+result)
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()
        except Exception as e:
            print(e)
    
    


        
def main():
    healthParser = Health_Parser()
    running = True
    while running:
        print("** Operations **")
        operations = ['Show all types','Select type','Graph type','Create CSV', 'Quit']
        [print(f'   {idx}. {operation}') for idx,operation in enumerate(operations)]
        user_input = int(input("   Make a Selection: "))
        match user_input:
            case 0:
                healthParser.print_all_types()
            case 1:
                user_selection = int(input("Enter index of type: "))
                healthParser.get_selected_type(user_selection)
            case 2:
                user_selection = int(input("Enter index of type: "))
                healthParser.graph_selected_type(user_selection)
            case 3:
                user_selection = int(input("Enter index of type: "))
                healthParser.create_csv(user_selection)
            case 4:
                running = False


if __name__ == '__main__':
    main()


    
    
