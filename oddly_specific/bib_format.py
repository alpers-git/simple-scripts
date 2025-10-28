import sys
import re

if len(sys.argv)!=2:
    print('Error: invalid parameter count')
    exit()

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

entry_types = ('@article', '@book', '@booklet', '@conference', '@inbook',
        '@incollection', '@inproceedings', '@manual', '@masterthesis', 
        '@misc', '@phdtehsis', '@proceedings', '@techreport', '@unpublished',
        '@ARTICLE', '@BOOK', '@BOOKLET', '@CONFERENCE', '@INBOOK',
        '@INCOLLECTION', '@INPROCEEDINGS', '@MANUAL', '@MASTERTHESIS', 
        '@MISC', '@PHDTHESIS', '@PROCEEDINGS', '@TECHREPORT', '@UNPUBLISHED',)

with open(sys.argv[1], "r") as fp, open('new.bib', 'w') as new_file :
    for line in fp:
        if line.lower().startswith(entry_types):
            entry_name_s = line.index('{')+1
            entry_name_e = line.index(',')
            entry_name = line[entry_name_s:entry_name_e]

            entry_name = entry_name.capitalize() #1)make first author name capital

            date_s = re.search(r'\d', entry_name) #2)reformat dates
            no_date = False
            if not date_s:
                print('Warning: No date found for entry ', entry_name)
                no_date = True
            else:
                date_s = date_s.start(0)
                date_e = re.match('.+([0-9])[^0-9]*$', entry_name).start(1)+1
                if date_e - date_s >= 5:    #handle if paper title cue includes a number
                    if entry_name[date_s + 4].isdigit():
                        date_e = date_s + 4
                    elif entry_name[date_s + 2].isdigit():
                        date_e = date_s + 2
                elif  date_e - date_s == 3: #handle if paper title cue includes a number
                    date_e = date_s + 2

                if (date_e - date_s != 4) and (date_e - date_s !=2):
                    print('Warning: No date found for entry ', entry_name, date_e - date_s)
                    no_date = True
                if date_e - date_s ==2:
                    if int(entry_name[date_s:date_e]) > 22:
                        print("Warning: reformatting 2 digit dates to 4 digits by adding '19'. Please check entry", entry_name)
                        entry_name = entry_name[:date_s] + '19' + entry_name[date_s:]
                    else:
                            print("Warning: reformatting 2 digit dates to 4 digits by adding '20'. Please check entry", entry_name)
                            entry_name = entry_name[:date_s] + '20' + entry_name[date_s:]
                    date_e +=2
                #print(entry_name[date_s:date_e])

            if (not no_date) and not (date_e == entry_name[-1]): #reformat title alias
                entry_name = entry_name[:date_e] + entry_name[date_e:].capitalize()
            else:
                    print('Warning: No alias found for entry ', entry_name)
            #print(entry_name)
            line = line.replace( line[entry_name_s:entry_name_e], entry_name)
        new_file.write(line)
        
            #print(line)
#fp = open(sys.argv[1], "r+")

#print(data)