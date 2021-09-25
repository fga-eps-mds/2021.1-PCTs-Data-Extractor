[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=fga-eps-mds_2021.1-PCTs-Scraper&metric=alert_status)](https://sonarcloud.io/dashboard?id=fga-eps-mds_2021.1-PCTs-Scraper)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=fga-eps-mds_2021.1-PCTs-Scraper&metric=coverage)](https://sonarcloud.io/dashboard?id=fga-eps-mds_2021.1-PCTs-Scraper)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=fga-eps-mds_2021.1-PCTs-Scraper&metric=sqale_rating)](https://sonarcloud.io/dashboard?id=fga-eps-mds_2021.1-PCTs-Scraper)

# 2021.1-PCTs-Data-Extractor

Repositório com o serviço de extração de dados

# Como executar (Docker)

Com esse comando, o container do splash será iniciado, como uma API, por outro lado, o container do scraper irá executar sua rotina e depois parar.
Esse método atualmente está sendo utilizado sem uma API para o Scraper, portanto o container do scraper não irá se manter ativo para receber requisições.

__Importante:__ Esse método apenas foi adicionado para facilitar a execução por parte dos integrantes ainda não familiarizados com o framework Scrapy. Futuramente, toda execução será realizada por uma API com um cronjob.

```shell
docker-compose up
```

## Contribuição

1. Clone io repositório
2. Crie uma branch (`git checkout -b feat/x-branch-name`)
3. Commit suas alterações (`git commit -am "Add feat"`)
4. Push para a branch (`git push origin feat/x-branch-name`)

### Extras

- [Guia completo de contribuição completo](https://github.com/fga-eps-mds/2021.1-PCTs-Docs/blob/main/CONTRIBUTING.md)
