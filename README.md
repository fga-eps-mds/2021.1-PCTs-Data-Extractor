[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=fga-eps-mds_2021.1-PCTs-Scraper&metric=alert_status)](https://sonarcloud.io/dashboard?id=fga-eps-mds_2021.1-PCTs-Scraper)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=fga-eps-mds_2021.1-PCTs-Scraper&metric=coverage)](https://sonarcloud.io/dashboard?id=fga-eps-mds_2021.1-PCTs-Scraper)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=fga-eps-mds_2021.1-PCTs-Scraper&metric=sqale_rating)](https://sonarcloud.io/dashboard?id=fga-eps-mds_2021.1-PCTs-Scraper)

# 2021.1-PCTs-Data-Extractor

Repositório com o serviço de extração de dados

# Como testar

Atualmente como não há uma API para iniciar um scraper a partir dela, temos apenas o arquivo "call_generic_scraper.py" para realizar a chamada para o Scraper em generic_scraper_pagination.py.

Importante 1: Como o spider (caminho pcts_scrapers/spiders/generic_scraper_pagination.py) utiliza o Splash em um container docker para processar as paginas de maneira assincrona, é preciso iniciar o container splash antes de executar "call_generic_scraper.py".

Importante 2: Como no momento o scraper ainda não executado em docker, é necessário instalar as dependências diretamente em seu PC, ou ambiente virtualenv

```shell
virtualenv -p python3 venv
source ven/bin/activate
pip install -r requirements

```

Exemplo debugando o container splash:

Terminal 1:
```shell
docker-compose up pcts-scrapers-splash
```

Terminal 2:
Como no momen
```shell
python call_generic_scraper.py
```

## Contribuição

1. Clone io repositório
2. Crie uma branch (`git checkout -b feat/x-branch-name`)
3. Commit suas alterações (`git commit -am "Add feat"`)
4. Push para a branch (`git push origin feat/x-branch-name`)

### Extras

- [Guia completo de contribuição completo](https://github.com/fga-eps-mds/2021.1-PCTs-Docs/blob/main/CONTRIBUTING.md)
