# Ezonzo api

Hiring assignment project for EarthDaily

## What is Ezonzo?

During the first year of the pandemic, local shops faced an existential risk due to the lockdowns, the general avoidance of public spaces, and the competition with online shops. People were aware of this problem, and most were sympathetic towards local businesses, but local shopping was just way more time demanding, risky, and cumbersome than online shopping.
I wanted to simplify local shopping and make it competitive with online shopping during the covid years. To do so, I needed to address the following issues:
- When you go to a shop searching for an item, you are not guaranteed to find it, which means you need to try different shops until you find what you look for (e.g. a specific cable or specific model of headphones)
- Shop-hopping is time demanding
- Shop-hopping exposes you to health risks.

To address the above, I wanted to fill, for each city area, a database of products being sold in each local shop, so that one could look up the closest shop that sells the item of interest before leaving home, and being guaranteed to find it.

Ezonzo scrapes the local businesses' online catalogues and stores the products in a single data store together with the shops' data. An web interface allows for search functionality.

To scrape businesses I built a scraping framework on top of scrapy that is specific to online shops/catalogues and is configurable with a simple json configuration for each new website to scrape. It supports both static and dynamic websites, by using a headless browser with js rendering.

## What's the state of the project?
I started the project in 2020 and interrupted it after a couple of months due to some legal obstacles to its implementation (turns out scraping requires permissions) and the change in the general pandemic sistuation.

The scraping framework was built and in a working state, there and there was a simple UI ready. 
The project was still in a scratch/brainstorming phase when I interrupted it.

## What does ezonzoapi do?
For the EarthDaily task I drafted an api that would work to serve ezonzo product data to a hypothetical user. 
The end user provides

- its location coordinates
- a query string to match the name or the tags of the product
- a maximum distance from its location
- a maximum price for the products

For this task, Ezonzoapi simply returns all the products that match. As I imagine this would be used on a map, the ordering doesn't matter. This is also advantageous for our query speed, as we can simply use ST_DWithin instead of calculating the distance.

## What's the ezonzoapi design?

Ezonzoapi is written in python 3.10 using the FastApi framework, and deployed on the AWS serverless stack (API Gateway, Lambda, RDS Proxy), a postgres database with the postgis extension

![image](https://github.com/robertocarta/ezonzoapi/assets/15035783/ecb7ad52-fcc4-4179-a4d2-757049d70490)

## Earth daily assignment:

For this assignment I decided to give priority to the following instruction:

"We love to see APIs that are imaginative. Another variation of the pet store API example does not demonstrate creativity or the ability to
code something from scratch. Maybe you have a personal project in mind that you need an API for? Or have a day to day problem that
an API might solve?"

Which meant I had to compromise on other aspects. This is not a project that can be designed, developed and deployed in 4 hours, but I hope the design gives us enough to talk about.

**Assignment load requirements**
The load requirements are handled in the design by lambda and RDS proxy, although changes would be needed to the database (read replicas, query optimisation, indices, ditching ORMs depending on data size)
Note that in the aws current deployment RDS proxy isn't set up, and everything is massively underprovisioned, from the RDS instance, to the lambda maximum concurrency allowance. So while the design would be handle to handle the required load, this draft implementation most definitely wouldn't.


**Current state of the implementation**
The api works locally and on aws at https://ut0b3vuq6e.execute-api.us-east-1.amazonaws.com/dev/docs, where the database has been populated with some testing data consisting of 4 shops in Bologna, all in the games&toys sector, and the same 3000 products for each of them. 

```
shops table:

 id |        name         |        lat         |        lon         | location |                    address                     |                       url
----+---------------------+--------------------+--------------------+----------+------------------------------------------------+-------------------------------------------------
  1 | Giocheria           |   44.4910507609255 | 11.346836656806383 | ...      | Via Castiglione, 11a, 40120, Bologna BO        | https://www.giocheriabologna.it
  2 | Tutti Bambini       |  44.49949871123964 | 11.338983147716995 | ...      | Via Guglielmo Marconi, 32, 40122 Bologna BO    |
  3 | Toys Centre         |  44.50605454797169 | 11.331729237761035 | ...      | Via Paolo Bovi Campeggi, 2/2, 40131 Bologna BO | http://www.toyscenter.it/
  4 | Tempo di giocattoli | 44.488760851260565 |  11.31727048855604 | ...      | Via Saragozza, 212, 40134 Bologna BO           | https://toschestationcomics.com/andaresuamazon9
```

The api supports GET and POST for the `/products` endpoint. It allows to get all products within a certain distance from the user, and create new products (and shops).

The POST request product schema is a bit atypical, as it always includes the shop data.


```
{
  "url": "string",
  "name": "string",
  "price": 0,
  "thumbnail": "string",
  "tags": "string",
  "shop": {
    "name": "string",
    "lat": 0,
    "lon": 0,
    "address": "string",
    "url": "string"
  }
```
This triggers a create action for the product, and a create-if-not-exists for the shop. The reason for this setup is that its user would be the actual ezonzo scraper, so it's shaped around the scrapers' data model. It could be handled better by checking for the existence of the shop and creating the shop/product in separate requests.

GET is more standard and shaped around a hypothetical user basic needs:

`products/?search_str=[str]&lat=[float]&lon=[float]&max_distance=[float]&max_price=[float]`

Note that "max_distance" is expressed in km.




### Further notes
This is a draft. It was constrained by my time availability, my covid (hich kept me company during the development) and the ~5 hours indication (although it took me more), so nothing here is up to production standards. Among other issues:
- there is no infrastructure code
- security wasn't thought through
- no database optimisation
- tests only cover happy paths
- missing endpoints
- PostGis functionality quickly put together (this was my first experience with postgis)



### Running the project:


**Virtual environment**
Set up a python virtual environment and install requirements
`pip install -r requirements.txt`


**Postgres**
1. Install postgres
2. `create database ezonzoapi`
3. connect to the database and `create extension postgis`

Create a ./app/.env file containing:
```
DB_USER=[dbuser]
DB_PASS=[dbpassword]
DB_HOST=[dbhost]
DB_PORT=[dbport]
DB_NAME=ezonzoapi
```

**Run locally**
from the app subdirectory run
```
  uvicorn app:app --reload
```

API documentation will be accessible at http://127.0.0.1:8000/docs

**Run unit tests**
from ./app run `pytest test_app.py`

**Run on the aws**

Infrastructure code was not included, so it needs to be set up manually. You will need:

- Docker
- An ECR repository
- A postgres RDS instance 
- A lambda function with access to RDS
- An APIGetway REST api with a resource configured with lambda proxy integration

Build - push -deploy:
```
aws ecr get-login-password --region [region] | docker login --username AWS --password-stdin [ecr repository URI] && docker build -t ezonzoapi .
docker push [ecr repository URI]/ezonzoapi:latest
aws lambda update-function-code \
    --function-name ezonzoapi \
    --image-uri [repository uri ]/ezonzoapi:latest\
    --region [region]
```
