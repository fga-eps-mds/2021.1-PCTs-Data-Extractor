[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=fga-eps-mds_2021.1-PCTs-Scraper&metric=coverage)](https://sonarcloud.io/dashboard?id=fga-eps-mds_2021.1-PCTs-Scraper)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=fga-eps-mds_2021.1-PCTs-Scraper&metric=sqale_rating)](https://sonarcloud.io/dashboard?id=fga-eps-mds_2021.1-PCTs-Scraper)

# 2021.1-PCTs-Data-Extractor

Repositório com o serviço de extração de dados

# Como executar (Docker)

### Pré requisitos

- [Docker](https://docs.docker.com/engine/install/ubuntu/)
- [Docker Compose](https://docs.docker.com/compose/install/)


1. Configurar variáveis de ambiente (containers):
  * Atualizar arquivo "env" na raiz do repositório
  * Adicionar os hosts (ips) das apis de documentos e crawlers
  * Variáveis necessárias:
  ```shell
    POSTGRES_HOST # Host do banco
    POSTGRES_PORT # Porta do banco
    POSTGRES_USER # Usuário do banco
    POSTGRES_PASSWORD # Senha do banco
    POSTGRES_DB # Nome do banco
    PCTS_DOCUMENTS_API_URL # Host da api de documentos. Exemplo: http://pcts-documents:8000
    PCTS_DOCUMENTS_API_RECORDS_ENDPOINT # Endpoint da api de bancos. Exemplo: api/documents/
    DJANGO_SUPERUSER_EMAIL # Email do usuario admnistrador
    DJANGO_SUPERUSER_USERNAME # Username do usuario admnistrador
    DJANGO_SUPERUSER_PASSWORD # Senhado do usuario admnistrador
    PROJECT_ENV_EXECUTOR=DOCKER # Ambiente de execução. Não precisa alterar
    CELERY_BROKER_URL=amqp://guest@pcts-crawlers-rabbitmq:5672 # Host do rabbitmq. Não precisa alterar
  ```


2. Construir imagens e executar containers

### Pré requisitos

- [Docker](https://docs.docker.com/engine/install/ubuntu/)
- [Docker Compose](https://docs.docker.com/compose/install/)


1. Configurar variáveis de ambiente (containers):
  * Atualizar arquivo "env" na raiz do repositório
  * Adicionar os hosts (ips) das apis de documentos e crawlers
  * Variáveis necessárias:
  ```shell
    POSTGRES_HOST # Host do banco
    POSTGRES_PORT # Porta do banco
    POSTGRES_USER # Usuário do banco
    POSTGRES_PASSWORD # Senha do banco
    POSTGRES_DB # Nome do banco
    PCTS_DOCUMENTS_API_URL # Host da api de documentos. Exemplo: http://pcts-documents:8000
    PCTS_DOCUMENTS_API_RECORDS_ENDPOINT # Endpoint da api de bancos. Exemplo: api/documents/
    DJANGO_SUPERUSER_EMAIL # Email do usuario admnistrador
    DJANGO_SUPERUSER_USERNAME # Username do usuario admnistrador
    DJANGO_SUPERUSER_PASSWORD # Senhado do usuario admnistrador
    PROJECT_ENV_EXECUTOR=DOCKER # Ambiente de execução. Não precisa alterar
    CELERY_BROKER_URL=amqp://guest@pcts-crawlers-rabbitmq:5672 # Host do rabbitmq. Não precisa alterar
  ```


2. Construir imagens e executar containers

```shell
docker-compose build
docker-compose up
```

## Contribuição

1. Clone io repositório
2. Crie uma branch (`git checkout -b feat/x-branch-name`)
3. Commit suas alterações (`git commit -am "Add feat"`)
4. Push para a branch (`git push origin feat/x-branch-name`)

### Extras

- [Guia completo de contribuição completo](https://github.com/fga-eps-mds/2021.1-PCTs-Docs/blob/main/CONTRIBUTING.md)
