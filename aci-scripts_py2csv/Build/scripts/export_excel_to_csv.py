#from __future__ import absolute_import, division, print_function
import xlrd
import csv
import os

workbook = "d:\design\Airbus_aci_divisional_build_input_data_v0.12.xlsx"
csv_dir = "./input/"


#
def processWorksheet(sheetname, wb):
    try:
        sh = wb.sheet_by_name(sheetname)
    except:
        print("\nWorksheet '{0}' does not exist in workbook\n".format(sheetname))
        return

    csv_file = open(csv_dir + sheetname + ".csv", 'w', newline='')
    #csv_file = open("d:\\temp\\" + sheetname + ".csv", 'w', newline='')
    #csv_file = open(csv_dir + sheetname + ".csv", 'wb')
    wr = csv.writer(csv_file, quoting=csv.QUOTE_NONE, escapechar='\\', quotechar='"')

    print("Processing {0} rows..".format(sh.nrows))
    for rownum in range(sh.nrows):
        wr.writerow(sh.row_values(rownum))
    csv_file.close()

#
def processWorkbook(wb):
    build_tasks_sheet = wb.sheet_by_name("build_tasks")
    for rownum in range(build_tasks_sheet.nrows):
        if build_tasks_sheet.cell(rownum,0).value == "yes":
                print("Processing worksheet '{0}'...".format(build_tasks_sheet.cell(rownum,2).value))
                processWorksheet(build_tasks_sheet.cell(rownum,2).value, wb)

# main
def main():
    try:
        os.system('cls')  # on windows
    except:
        try:
            os.system('clear')  # on linux
        except:
            print("\n\n\n\n")
    print("****************************************************************************")
    print("\nUsing workbook '{0}'...\n".format(workbook))
    print("CSV output directory is {0}\n".format(csv_dir))
    print("Press Enter to continue...")
    opt = input("> ")
    try:
        wb = xlrd.open_workbook(workbook)
    except:
        print("\nUnable to open workbook:", workbook, "... Aborting")
        return
    processWorkbook(wb)

if __name__ == "__main__":
    main()