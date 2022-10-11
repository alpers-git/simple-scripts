#reads a bibtex file and creates a html file with the papers

#get file name from command line
import sys
import bibtexparser
from bibtexparser.bwriter import BibTexWriter
# Import unidecode module from unidecode
from unidecode import unidecode

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

file_name = sys.argv[1]

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
def process_title(title):
    title = title.replace('{', '')
    title = title.replace('}', '')
    title = '"' + title + '"'
    return title

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
   html_file_name = file_name[:-4] + ".html"
   html_file = open(html_file_name, 'w')

   #Create detailed looks into latest three papers
   counter = 0
   for entry in bibtex_database.entries[0:3]:
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

        html_file.write(process_title(entry['title']) + " \n\t\t\t\t\t\t")
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

