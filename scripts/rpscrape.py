#!/usr/bin/env python3.6
#
# Scrapes results and saves them in csv format

import os
import sys
import json
import requests
import readline
from lxml import html
from re import search


class Completer(object):

    def __init__(self, options):
        self.options = sorted(options)

    def complete(self, text, state):
        if state == 0:
            if text:
                self.matches = [s for s in self.options if s and s.startswith(text)]
            else:
                self.matches = self.options[:]
        try: 
            return self.matches[state]
        except IndexError:
            return None


def show_options(opt='help'):
    opts =  '\n'.join([
            '       regions              List all available region codes',
            '       regions [search]     Search regions for a specific country code',
            '',
            '       courses              List all courses',
            '       courses [search]     Search for specific course',
            '       courses [region]     List courses in region - e.g courses ire'
            ])

    if opt == 'help':
        print(
            '\n'.join([
            '  Usage:',
            '       [rpscrape]> [region|course] [year|range] [flat|jumps]',
            '',
            '       Regions have alphabetic codes.',
            '       Courses have numeric codes.'
            '',
            '  Examples:',
            '       [rpscrape]> ire 1999 flat',
            '       [rpscrape]> gb 2015-2018 jumps',
            '       [rpscrape]> 533 1998-2018 flat',
            '',
            '  Options:',
            '{}'.format(opts),
            '',
            '  More info:',
            '       help           Show help',
            '       options        Show options',
            '       cls, clear     Clear screen',
            '       q, quit        Quit',
            ''
        ]))
    else:
        print(opts)


def get_courses(region='all'):
    with open(f'../courses/{region}_course_ids', 'r') as courses:
        for course in courses:
            yield (course.split('-')[0].strip(), ' '.join(course.split('-')[1::]).strip())
         

def get_course_name(code):
    if code.isalpha():
        return code
    for course in get_courses():
        if course[0] == code:
            return course[1].replace('()', '').replace(' ', '-')


def course_search(term):
    for course in get_courses():
        if term.lower() in course[1].lower():
            print_course(course[0], course[1])


def print_course(key, course):
    if len(key) == 5:
        print(f'     CODE: {key}| {course}')
    elif len(key) == 4:
        print(f'     CODE: {key} | {course}')
    elif len(key) == 3:
        print(f'     CODE: {key}  | {course}')
    elif len(key) == 2:
        print(f'     CODE: {key}   | {course}')
    else:
        print(f'     CODE: {key}    | {course}')


def print_courses(region='all'):
    for course in get_courses(region):
        print_course(course[0], course[1])


def validate_course(course_id):
    return course_id in [course[0] for course in get_courses()]


def x_y():
    import base64
    return base64.b64decode('aHR0cHM6Ly93d3cucmFjaW5ncG9zdC5jb206NDQzL3Byb2ZpbGUvY291cnNlL2ZpbHRlci9yZXN1bHRz')\
    .decode('utf-8'), base64.b64decode('aHR0cHM6Ly93d3cucmFjaW5ncG9zdC5jb20vcmVzdWx0cw==').decode('utf-8')


def get_regions():
    with open('../courses/_countries', 'r') as regions:
        return json.load(regions)


def region_search(term):
    for key, region in get_regions().items():
        if term.lower() in region.lower():
            print_region(key, region)


def print_region(key, region):
    if len(key) == 3:
        print(f'     CODE: {key} | {region}')
    else:
        print(f'     CODE: {key}  | {region}')


def print_regions():
    for key, region in get_regions().items():
        print_region(key, region)


def validate_region(region):
    return region in get_regions().keys()


def validate_years(years):
    if years:
        return all(year.isdigit() and int(year) > 1995 and int(year) < 2019 for year in years)
    else:
        return False

def get_races(tracks, names, years, code,  xy):
    for track, name in zip(tracks, names):
        for year in years:
            r = requests.get(f'{xy[0]}/{track}/{year}/{code}/all-races', headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code == 200:
                try:
                    results = r.json()
                    if results['data']['principleRaceResults'] == None:
                        print(f'No {code} race data for {get_course_name(track)} in {year}.')
                        continue
                    for result in results['data']['principleRaceResults']:
                        yield (f'{xy[1]}/{track}/{name}/{result["raceDatetime"][:10]}/{result["raceInstanceUid"]}')
                except:
                    pass
            else:
                print(f'Unable too access races from {get_course_name(track)} in {year}')


def clean(data):
    return [d.strip().replace('–', '') for d in data]


def scrape_races(races, target, years):
    if not os.path.exists('../data'):
        os.makedirs('../data')

    with open(f'../data/{target.lower()}-{years}.csv', 'w') as csv:
        csv.write(('"date","course","time","race_name","class","band","distance","going","pos","draw","btn","name",'
            '"sp","age","weight","gear","jockey","trainer","or","ts","rpr","prize","comment"\n'))
            
        for race in races:
            r = requests.get(race, headers={'User-Agent': 'Mozilla/5.0'})
            doc = html.fromstring(r.content)

            course_name = race.split('/')[5]
            try:
                date = doc.xpath("//span[@data-test-selector='text-raceDate']/text()")[0]
            except IndexError:
                date = 'not found'
            try:
                time = doc.xpath("//span[@data-test-selector='text-raceTime']/text()")[0]
            except IndexError:
                time = 'not found'

            try:
                race = doc.xpath("//h2[@class='rp-raceTimeCourseName__title']/text()")[0].strip().strip('\n').replace(',', ' ')
            except IndexError:
                race = 'not found'

            if '(Group' in race:
                race_class = search('(Grou..)\w+', race).group(0)
                race = race.replace(f'({race_class})', '')
            elif '(Grade' in race:
                race_class = search('(Grad..)\w+', race).group(0)
                race = race.replace(f'({race_class})', '') 
            elif '(Listed Race)' in race:
                race_class = 'Listed'
                race = race.replace('(Listed Race)', '')
            else:
                try:
                    race_class = doc.xpath("//span[@class='rp-raceTimeCourseName_class']/text()")[0].strip().strip('()')
                except:
                    race_class = 'not found'

            try:
                band = doc.xpath("//span[@class='rp-raceTimeCourseName_ratingBandAndAgesAllowed']/text()")[0].strip().strip('()')
            except:
                band = 'not found'
            if ',' in band:
                split_band = band.split(',')
                race_class = split_band[0]
                band = split_band[1]
            if '(Fillies & Mares)' in race:
                band = band + ' Fillies & Mares'
                race = race.replace('(Fillies & Mares)', '')
            elif '(Fillies)' in race or 'Fillies' in race:
                band = band + ' Fillies'
                race = race.replace('(Fillies)', '')
            elif '(Colts & Geldings)' in race:
                band = band + ' Colts & Geldings'
                race = race.replace('(Colts & Geldings)', '')

            try:
                distance = doc.xpath("//span[@class='rp-raceTimeCourseName_distance']/text()")[0].strip()
            except IndexError:
                distance = 'not found'
            dist = ''.join([d.strip().replace('¼', '.25').replace('½', '.5').replace('¾', '.75') for d in distance])

            try:
                going = doc.xpath("//span[@class='rp-raceTimeCourseName_condition']/text()")[0].strip()
            except IndexError:
                going ='not found'

            coms = doc.xpath("//tr[@class='rp-horseTable__commentRow ng-cloak']/td/text()")
            com = [x.strip().replace('  ', '').replace(',', ' -') for x in coms]
            possy = doc.xpath("//span[@data-test-selector='text-horsePosition']/text()")
            del possy[1::2]
            pos = [x.strip() for x in possy]
            prizes = doc.xpath("//div[@data-test-selector='text-prizeMoney']/text()")
            prize = [p.strip().replace(",", '').replace("£", '') for p in prizes]
            try:
                del prize[0]
                for i in range(len(pos) - len(prize)):
                    prize.append('')
            except IndexError:
                prize = ['' for x in range(len(pos))]    
            draw = clean(doc.xpath("//sup[@class='rp-horseTable__pos__draw']/text()"))
            draw = [d.strip("()") for d in draw]
            beaten = doc.xpath("//span[@class='rp-horseTable__pos__length']/span/text()")
            del beaten[1::2]
            btn = [b.strip().strip("[]").replace('¼', '.25').replace('½', '.5').replace('¾', '.75') for b in beaten]
            btn.insert(0, '')
            if len(btn) < len(pos):
                btn.extend(['' for x in range(len(pos) - len(btn))])
            name = clean(doc.xpath("//a[@data-test-selector='link-horseName']/text()"))
            sp = clean(doc.xpath("//span[@class='rp-horseTable__horse__price']/text()"))
            jock = clean(doc.xpath("//a[@data-test-selector='link-jockeyName']/text()"))
            del jock[::2]
            trainer = clean(doc.xpath("//a[@data-test-selector='link-trainerName']/text()"))
            del trainer[::2]
            age = clean(doc.xpath("//td[@data-test-selector='horse-age']/text()"))
            _or = clean(doc.xpath("//td[@data-ending='OR']/text()"))
            ts = clean(doc.xpath("//td[@data-ending='TS']/text()"))
            rpr = clean(doc.xpath("//td[@data-ending='RPR']/text()"))
            st = doc.xpath("//span[@data-ending='st']/text()")
            lb = doc.xpath("//span[@data-ending='lb']/text()")
            wgt = [a.strip() +'-' + b.strip() for a, b in zip(st, lb)]
            headgear = doc.xpath("//td[contains(@class, 'rp-horseTable__wgt')]")
            gear = []
            for h in headgear:
                span = h.find('span[@class="rp-horseTable__headGear"]')
                if span is not None:
                    gear.append(span.text)
                else:
                    gear.append('')

            for p, pr, dr, bt, n, s, j, tr, a, o, t, rp, w, g, c in \
            zip(pos, prize, draw, btn, name, sp, jock, trainer, age, _or, ts, rpr, wgt, gear, com):
                csv.write((f'{date},{course_name},{time},{race},{race_class},{band},{dist},{going},'
                            f'{p},{dr},{bt},{n},{s},{a},{w},{g},{tr},{j},{o},{t},{rp},{pr},{c}\n'))

    print(f'\nFinished scraping. {target.lower()}-{years}.csv saved in rpscrape/data')


def parse_args(args=sys.argv):
    if len(args) == 1:
        if 'help' in args or 'options' in args:
            show_options(args[0])
        elif 'clear' in args:
            os.system('cls' if os.name == 'nt' else 'clear')
        elif 'quit' in args or 'q' in args:
            sys.exit()
        elif 'regions' in args:
            print_regions()
        elif 'courses' in args:
            print_courses()

    elif len(args) == 2:
        if args[0] == 'regions':
            region_search(args[1])
        elif args[0] == 'courses':
            if validate_region(args[1]):
                print_courses(args[1])
            else:
                course_search(args[1])

    elif len(args) == 3:
        if validate_region(args[0]):
            region = args[0]
        elif validate_course(args[0]):
            course = args[0]
        else:
            return print('Invalid course or region.')

        if '-' in args[1]:
            try:
                years = [str(x) for x in range(int(args[1].split('-')[0]), int(args[1].split('-')[1]) + 1)]
            except ValueError:
                return print('Invalid year, must be in range 1996-2018.')
        else:
            years = [args[1]]
        if not validate_years(years):
            return print('Invalid year, must be in range 1996-2018.')

        if 'jumps' in args or 'jump' in args or '-j' in args:
            code = 'jumps'
        elif 'flat' in args or '-f' in args:
            code = 'flat'
        else:
            return print('Invalid racing code. -f, flat or -j, jumps.')

        if 'region' in locals():
            tracks = [course[0] for course in get_courses(region)]
            names = [get_course_name(track) for track in tracks]
            scrape_target = region
            print(f'Scraping {code} results from {scrape_target} in {args[1]}...')
        else:
            tracks = [course]
            names = [get_course_name(course)]
            scrape_target = course
            print(f'Scraping {code} results from {get_course_name(scrape_target)} in {args[1]}...')

        races = get_races(tracks, names, years, code, x_y())
        scrape_races(races, get_course_name(scrape_target), args[1])

    else:
        show_options()


def main():
    if len(sys.argv) > 1:
        sys.exit(show_options())

    completions = Completer(["courses", "regions", "options", "help", "quit", "clear", "flat", "jumps"])
    readline.set_completer(completions.complete)
    readline.parse_and_bind('tab: complete')

    while True:
        args =  input('[rpscrape]> ').lower().strip()
        parse_args([arg.strip() for arg in args.split()])


if __name__ == '__main__':
    main()
