import os, csv

def get_fieldnames( report : dict, key_field : str ) -> list:
    if len(report) == 0:
        return []
    else:
        key = next(iter(report))
        fieldnames = [key_field] + list(report[key])
        return fieldnames


def write_report( report : dict, output_path : str, report_name, key_field : str ) -> bool:
    fieldnames = get_fieldnames( report, key_field )
    if fieldnames == []:
        return False

    report_path = os.path.join( output_path, f'{report_name}.csv' )
    f_out = open( report_path, mode='w', newline='', encoding='UTF-8' )
    writer = csv.DictWriter( f_out, delimiter='|', fieldnames=fieldnames, quotechar='"', quoting=csv.QUOTE_MINIMAL, escapechar='\\' )
    writer.writeheader()

    for year in report:
        dict_to_write = { key_field : year, **report[year] }
        writer.writerow( dict_to_write )

    f_out.close()

    return True