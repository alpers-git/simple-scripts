#reads a bibtex file and creates a html file with the papers

#get file name from command line
import sys
import bibtexparser
from bibtexparser.bwriter import BibTexWriter
# Import unidecode module from unidecode
from unidecode import unidecode
import datetime

month_ranks = {
    'jan': 1,
    'feb': 2,
    'mar': 3,
    'apr': 4,
    'may': 5,
    'jun': 6,
    'jul': 7,
    'aug': 8,
    'sep': 9,
    'oct': 10,
    'nov': 11,
    'dec': 12
}

print_pubs = True
print_teaser = True

file_name = sys.argv[1]
#check if 2nd parameter is given
if len(sys.argv) > 2:
    #if its "-t-only" or "--teaser-only" then set print_pubs to false
    if sys.argv[2] == "-t-only" or sys.argv[2] == "--teaser-only":
        print_pubs = False
    #if its "-p-only" or "--pubs-only" then set print_teaser to false
    elif sys.argv[2] == "-p-only" or sys.argv[2] == "--pubs-only":
        print_teaser = False
    else:
        print("Invalid parameter")
        sys.exit()

#process author
#a function that takes author name and shortens the first names to initials 
#and add a period
def process_author_name(author):
    dict = bibtexparser.customization.splitname(author)
    shortened_name = str(dict.get('first')[0][0]) + '. ' + str(dict.get('last')[0])

    #convert bibtex umlauts to ASCII characters
    shortened_name = shortened_name.replace('{\"a}', 'ä')
    shortened_name = shortened_name.replace('{\"o}', 'ö')
    shortened_name = shortened_name.replace('{\"u}', 'ü')
    shortened_name = shortened_name.replace('\\"u', 'ü')
    shortened_name = shortened_name.replace('{\"A}', 'Ä')
    shortened_name = shortened_name.replace('{\"O}', 'Ö')
    shortened_name = shortened_name.replace('{\"U}', 'Ü')
    shortened_name = shortened_name.replace('{\"s}', 'ß')
    shortened_name = shortened_name.replace('\c{c}', 'ç')
    shortened_name = shortened_name.replace('\c{C}', 'Ç')
    #shortened_name = shortened_name.replace('\u{g}', 'ğ')
    #shortened_name = shortened_name.replace('\u{G}', 'Ğ')
    shortened_name = shortened_name.replace('{\i}', 'ı')
    shortened_name = shortened_name.replace('\.{I}', 'İ')
    shortened_name = shortened_name.replace('\c{s}', 'ş')
    shortened_name = shortened_name.replace('\c{S}', 'Ş')
    return shortened_name

#process title
#a function that takes title, puts it in double quotes and removes curly brackets
def process_title(title, quotes=True):
    title = title.replace('{', '')
    title = title.replace('}', '')
    if quotes:
        title = '"' + title + '"'
    return title
def generate_teaser(size, html_file, bibtex_database):
    counter = 0
    for entry in bibtex_database.entries[0:size]:
            html_file.write("""<ul>
        <li class="row" id="extra-info-text">
            <div class="col s12 l12">
                <!--TEASER IMAGES here-->
            </div>
            <p class="col s12 m12 l12" id = "extra-info-text">""")
                #go over all the authors and add them to the html file if author name is 'Alper Sahistan' make it bold
                #make shorten first names to initials and add a period
            for author in entry['author'].split(' and '):
                if author == 'Sahistan, Alper':
                    html_file.write("<b>" + process_author_name(author) + "</b>")
                else:
                    html_file.write(unidecode(process_author_name(author)))
                #don't write a comma after the last author
                if author != entry['author'].split(' and ')[-1]:
                    html_file.write(", ")
                else:
                    html_file.write(" \n\t\t\t\t\t\t")

            html_file.write(process_title(entry['title'], True) + " \n\t\t\t\t\t\t")
            html_file.write("<b>" + entry['booktitle'] + "</b>\n")
            html_file.write('<a href= + LINK HERE> <i class="material-icons icon-light">picture_as_pdf</i></a>')
            html_file.write('<a class=" modal-trigger" href="#modal' + str(counter) + '"><i class="icon-light" style="font-family: Source Code Pro">BibTeX</i></a></p>')
            html_file.write("""\n\t\t</li>\n</ul>\n""")

            html_file.write('<!-- Modal -->\n')
            html_file.write('<div id="modal' + str(counter) + '" class="modal">\n')
            html_file.write("""\t <div class="modal-content" id="citation-box">\n
            \t\t<h4>BibTeX citation</h4>\n
            \t\t\t<div class="card-panel" id ="citation-text">\n
            \t\t\t\t<p type="text" id="paper"""+ str(counter) + '">')
            
            bibtex_str = bibtex_list[4-counter]
            html_file.write("@" + bibtex_str)
            html_file.write("""</p>
            </div>
            <div class="row">
            <div class="col m11"></div>
            <a class="button col m1" onclick="copyToClipboard('paper""" + str(counter) + """')"\n""")
            html_file.write(""" style="position: absolute; right: 0;"><i class="material-icons">copy_all</i></a>
            </div>
        </div>
        </div>\n""")
            counter += 1

def generate_pubs(html_file, bibtex_database):
    #Get the current year
    current_year = datetime.datetime.now().year
    first_pub_year = int(bibtex_database.entries[-1]['year'])

    html_file.write("""<div class="col s12 m12">
        \t<h2>"""+ str(current_year) +"""</h2>
        \t<hr>\n""")
    counter = 0
    #go over all the publications from bibtex_database
    for entry in bibtex_database.entries:
        #if the year of the publication is the same as the current year
        if entry['year'] != str(current_year):
            #decremenet the current year until it matches the year of the publication
            while entry['year'] != str(current_year):
                current_year -= 1
                html_file.write("""
                \t<h2>"""+ str(current_year) +"""</h2>
                \t<hr>\n""")

        html_file.write("""\t\t<div class="row">
        \t\t\t<div class="col s12 m12">
        \t\t\t\t<div class="card" style="background-color:#1c415b;">
        \t\t\t\t\t<div class="card-content white-text">
        \t\t\t\t\t\t<div class="row">
        \t\t\t\t\t\t\t<div class="col s6 m6">
        \t\t\t\t\t\t\t\t<!--Teaser Images here-->
        \t\t\t\t\t\t\t</div>
        \t\t\t\t\t\t</div>\n""")
        html_file.write("""\t\t\t\t\t\t<span class="card-title">""" 
        +process_title(entry['title'], False)+"""</span>
        \t\t\t\t\t\t<p><i>"""+ entry['booktitle'] +"""</i></p>\n""")
        html_file.write("""\t\t\t\t\t\t<p>Authors: """)
        #go over all the authors and add them to the html file if author name is 'Alper Sahistan' make it bold
        for author in entry['author'].split(' and '):
                if author == 'Sahistan, Alper':
                    html_file.write("<b>" + process_author_name(author) + "</b>")
                else:
                    html_file.write(unidecode(process_author_name(author)))
                #don't write a comma after the last author
                if author != entry['author'].split(' and ')[-1]:
                    html_file.write(", ")
                else:
                    html_file.write("</p>\n")
        html_file.write("""\t\t\t\t\t</div>
        \t\t\t\t\t<div class="card-action">
        \t\t\t\t\t\t<a href= + LINK HERE> <i class="material-icons icon-light">picture_as_pdf</i></a>
        \t\t\t\t\t\t<a class=" modal-trigger" href="#modal"""+ str(counter) + """"><i class="icon-light" style="font-family: Source Code Pro; text-transform: none">BibTeX</i></a>
        \t\t\t\t\t</div>
        \t\t\t\t</div>
        \t\t\t</div>
        \t\t</div>\n""")
        html_file.write('\t\t<!-- Modal -->\n')
        html_file.write('\t\t<div id="modal' + str(counter) + '" class="modal">\n')
        html_file.write("""\t\t\t <div class="modal-content" id="citation-box">
        \t\t\t\t<h4>BibTeX citation</h4>
        \t\t\t\t\t<div class="card-panel" id ="citation-text">
        \t\t\t\t\t\t<p type="text" id="paper"""+ str(counter) + '">\n')
        html_file.write("@" + entry['ID'] + "{" + entry['ID'] + ",\n")
        for key in entry.keys():
            if key != 'ID' and key != 'ENTRYTYPE':
                html_file.write("\t" + key + " = {" + entry[key] + "},\n")
        html_file.write("}\n")
        html_file.write("""\t\t\t\t\t\t</p>
        \t\t\t\t\t</div>
        \t\t\t\t\t<div class="row">
        \t\t\t\t\t\t<div class="col m11"></div>
        \t\t\t\t\t\t<a class="button col m1" onclick="copyToClipboard('paper""" + str(counter) + """')"\n""")
        html_file.write("""\t\t\t\t\t\t style="position: absolute; right: 0;"><i class="material-icons">copy_all</i></a>
        \t\t\t\t\t</div>
        \t\t\t</div>
        \t\t</div>\n""")
        counter+=1
    html_file.write("""</div>\n""")




#open the bibtex file and read the lines
with open(file_name) as bibtex_file:
    bibtex_database = bibtexparser.load(bibtex_file)
    #sort entries by first year and then month and then auhors name. year and month is descending order and author name is ascending order. Use the month_ranks dictionary to convert month to a number
    bibtex_database.entries.sort(key=lambda x: (x['year'], month_ranks[x['month'].lower()], x['author']), reverse=True)

    writer = BibTexWriter()
    writer.contents = ['entries']
    writer.indent = '  '
    writer.order_entries_by = ('year', 'month', 'author')
    #give first element of the bibtext entry to the writer
    bibtex_str = bibtexparser.dumps(bibtex_database, writer)
    bibtex_list = bibtex_str.split('@')

    #create the html file
    html_file_name = file_name[:-len(bibtex_database.entries)] + ".html"
    html_file = open(html_file_name, 'w')

    if print_teaser:
        html_file.write("<!-- Teaser -->\n")
        generate_teaser(3, html_file, bibtex_database)
    
    if print_pubs:
        html_file.write("<!-- Full Pubs -->\n")
        generate_pubs(html_file, bibtex_database)
    

