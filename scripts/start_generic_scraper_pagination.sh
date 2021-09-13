#!/bin/bash


# SENADO
# scrapy crawl generic-scraper-pagination \
# -a root="https://www6g.senado.leg.br/busca/?q=comunidades+tradicionais&colecao=Not%C3%ADcias&p=45" \
# -a site_name="senado" \
# -a next_button_xpath="//*[@id=\"conteudoPrincipal\"]/div/div[2]/div[2]/nav/ul/li[8]/a" \
# -a allow_domains="www12.senado.leg.br,www25.senado.leg.br" \
# -a allow="noticias" \
# # -a items_xpath="//*[@id=\"conteudoPrincipal\"]/div/div[2]/div[2]/div/div/h3/a" \

# TCU
scrapy crawl generic-scraper-pagination \
-a root="https://pesquisa.apps.tcu.gov.br/#/resultado/todas-bases/quilombolas?ts=1631452168640&pb=jurisprudencia-selecionada" \
-a site_name="tcu" \
-a next_button_xpath="//*[@id=\"container\"]/div[2]/div/div/header/div[2]/mat-paginator/div/div/div[2]/button[2]" \
-a allow_domains="pesquisa.apps.tcu.gov.br" \
-a allow="#/documento" \
# -a items_xpath='//*[@id="lista-resultado__itens"]//a'
