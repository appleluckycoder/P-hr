# rpscrape - (BETA)

Horse racing data has been hoarded by a few companies, enabling them to effectively extort the public for access to any worthwhile historical amount. Compared to other sports where historical data is easily and freely available to use and query as you please, racing data in most countries is far harder to come by and is often only available with subscriptions to expensive software.

The aim of this tool is to provide a way of gathering large amounts of historical results data at no cost.


#### Example data from Ascot 2018

![data](https://i.postimg.cc/7LncCDMG/data1.png)
![data](https://i.postimg.cc/SsQPC5DZ/data2.png)

## Install

```
~$ git clone https://github.com/4A47/rpscrape.git
```

If you don't have git installed you can download the folder [here](https://github.com/4A47/rpscrape/archive/master.zip).

## Usage

Run the program from the scripts folder:
```
~$ cd rpscrape/scripts
~$ ./rpscrape.py

```

Make scrape requests as shown below:
```
[rpscrape]> [region|course] [year|range] [flat|jumps]
```

#### Options

```
regions              List all available region codes
regions [search]     Search regions for a specific country code

courses              List all courses
courses [search]     Search courses for specific course
courses [region]     List courses in region - e.g courses ire
```

Tab complete is available for all options.

The first option is that of a region or a course

Each region has a 2 or 3 letter code like ire for Ireland or gb for Great Britain. You can show the list of region codes with the following command:
```
[rpscrape]> regions
     CODE: mal | Malaysia
     CODE: mac | Macau
     CODE: gue | Guernsey
     CODE: ity | Italy
     CODE: swi | Switzerland
     CODE: tur | Turkey
     CODE: hk  | Hong Kong
     CODE: chi | Chile
     CODE: uae | United Arab Emirates
```

The other possibility for the first option is that of a specific course. To view the course codes, use the courses option as shown in the following example.

```
[rpscrape]> courses
     CODE: 32   | Aintree
     CODE: 2    | Ascot
     CODE: 3    | Ayr
     CODE: 4    | Bangor
     CODE: 5    | Bath
     CODE: 6    | Beverley
     CODE: 7    | Brighton
     CODE: 8    | Carlisle
```

If you want to search for a specific region or course, add a search term as shown below.

```
[rpscrape]> regions france
    CODE: fr  | France
```

```
[rpscrape]> courses york
    CODE: 107  | York
    CODE: 1347 | York Aus
```

To list the courses from a specific region, add the region code like so:
 ```
[rpscrape]> courses ire
     CODE: 175  | Ballinrobe
     CODE: 176  | Bellewstown
     CODE: 177  | Clonmel
     CODE: 596  | Cork
     CODE: 178  | Curragh
     CODE: 180  | Down Royal
     CODE: 179  | Downpatrick
     CODE: 181  | Dundalk
 ```

### Examples

The following example shows a request for flat races from Ireland in 2017.

```
[rpscrape]> ire 2017 flat
```

The next example shows a request for the last 2 years flat form in Great Britain.

```
[rpscrape]> gb 2017-2018 flat
```

The next example shows a request for the last 20 years jump form at Ascot(code: 2).
```
[rpscrape]> 2 1999-2018 jumps
```

### Known Issues

* Region scrape: HTTP 403 Error when trying to scrape full regions causing all following requests to fail despite working when scraped individually.