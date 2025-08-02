#!/usr/bin/env python

import re, sys, urllib2
import arrow # http://crsmithdev.com/arrow/
import pypandoc # https://github.com/bebraw/pypandoc
from bs4 import BeautifulSoup
from itertools import cycle

def locale():
    return arrow.locales.get_locale('en_us')

def regex(keyword):
    return re.compile('(.*)' + keyword + '(.*)', re.DOTALL)

def make_url(semester, year): 
    ''' Takes semester and year as strings, returns url to calendar '''
    baseurl = 'https://registrar.rice.edu/calendars/'
    url = baseurl + semester.lower() + year[-2:] + '/'
    return url

def date_formats():
    ''' based on Arrow string formats at http://crsmithdev.com/arrow/#tokens '''
    date_formats = [('September 3', 'MMMM D'),
            ('Sep. 3', 'MMM. D'),
            ('Wednesday, September 3', 'dddd, MMMM D'),
            ('Wednesday, September 3, 2025', 'dddd, MMMM D, YYYY'),
            ('Wed., Sep. 3, 2025', 'ddd., MMM. D, YYYY'),
            ('Wed., Sep. 3', 'ddd., MMM. D'),
            ('September 3, 2025', 'MMMM D, YYYY'),
            ('September 3', 'MMMM D'),
            ('Sep. 3', 'MMM. D'),
            ('September 3 (Wednesday)', 'MMMM D (dddd)'),
            ('9/3', 'M/D'),
            ('09/03', 'MM/DD'),
            ('2025-09-3', 'YYYY-MM-DD')]
    return date_formats

def fetch_registrar_table(url):
    ''' Get academic calendar table from registrar website '''
    html = urllib2.urlopen(url).read()
    soup = BeautifulSoup(html, 'html.parser')
    return soup.find('table')

def range_of_days(start, end):
    return arrow.Arrow.range('day', start, end)

def clean_cell(td):
    ''' Remove whitespace from a registrar table cell '''
    return re.sub(r"\s+", "", td)

def parse_td_for_dates(td):
    ''' Get date or date range as lists from cell in registrar's table '''
    cell = clean_cell(td)
    months = ['September', 'February', 'March', 'April', 'May',
            'June', 'July', 'August', 'September', 'October', 'November', 'December']
    ms = [locale().month_number(m) for m in months if m in cell]
    ds = [int(d) for d in re.split('\D', cell) if 0 < len(d) < 3]
    ys = [int(y) for y in re.split('\D', cell) if len(y) == 4]
    dates = zip(cycle(ms), ds) if len(ds) > len(ms) else zip(ms, ds)
    dates = [arrow.get(ys[0], md[0], md[1]) for md in dates]
    if len(dates) > 1:
        return range_of_days(dates[0], dates[1])
    else:
        return dates

def parse_registrar_table(table):
    ''' Parse registrar table and return first, last, cancelled days of class as lists '''
    no_classes = []
    for row in table.findAll('tr'):
        cells = row.findAll('td')
        if len(cells) > 1:
           try:
               days = clean_cell(cells[0].get_text())
           except:
               pass
           try:
               description = cells[1].get_text()
           except:
               pass
           if re.match(regex('(?i)FIRST DAY OF CLASSES'), description):
               first_day = parse_td_for_dates(days)
           if re.match(regex('(?i)LAST DAY OF CLASSES'), description):
               last_day = parse_td_for_dates(days)
           for date in parse_td_for_dates(days):
               if re.match(regex('(?i)NO SCHEDULED CLASSES'), description):
                   no_classes.append(date)
    return first_day, last_day, no_classes

def sorted_classes(weekdays, first_day, last_day, no_classes):
    ''' Take class meetings as list of day names, return lists of Arrow objects '''
    semester = range_of_days(first_day[0], last_day[0])
    possible_classes = [d for d in semester if locale().day_name(d.isoweekday()) in weekdays]
    return possible_classes, no_classes

def schedule(possible_classes, no_classes, show_no=None, fmt=None):
    ''' Take lists of Arrow objects, return list of course meetings as strings '''
    course = []
    date_format = fmt if fmt else 'dddd, MMMM D, YYYY'
    for d in possible_classes:
        if d not in no_classes:
            course.append(d.format(date_format))
        elif show_no:
            course.append(d.format(date_format) + ' - NO CLASS')
    return course

def markdown(schedule, semester, year, templatedir):
    course = ['## ' + d + '\n' for d in schedule]
    course = [d + '[Fill in class plan]\n\n' if 'NO CLASS' not in d else d for d in course]
    md_args = ['--template=' + templatedir + '/syllabus.md', '--to=markdown',
            '--variable=semester:' + semester.capitalize(), '--variable=year:' + year]
    return pypandoc.convert('\n'.join(course), 'md', 'md', md_args)

def output(schedule, semester, year, fmt, templatedir, outfile):
    md = markdown(schedule, semester, year, templatedir)
    template = templatedir + '/syllabus.' + fmt if templatedir else ""
    if fmt == 'docx':
        template_arg = '--reference-docx=' + template
    else:
        template_arg = '--template=' + template
    pandoc_args = ['--standalone']
    pandoc_args.append(template_arg)
    output = pypandoc.convert(md, fmt, 'md', pandoc_args, outputfile=outfile)
    assert output == ''
