# ATM

A simple ATM controller implementation

## Getting Started

### Prerequisites

Install the software below to test the code:

- [Docker, Docker Compose](https://www.docker.com/)

You may want to bellow Python3 programming language, 
if you want to develop the code without relying on Docker.

- [Python 3](https://www.python.org/downloads/)


### Fokr the repository

```bash
git clone git@github.com:dlimdlimdlim/practice1.git
```

Build project using docker-compose
```bash
docker-compose -f docker-compose.test.yml build
```


## TEST

### Running the tests
```bash
docker-compose -f docker-compose.test.yml run --rm tests pytest
```