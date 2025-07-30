# legisweb-api

Cliente Python para a API pública da LegisWeb, com suporte para múltiplos endpoints fiscais como ICMS, IPI, PIS/COFINS, ST, II, CFOP, TIPI, pautas fiscais, entre outros.

## Instalação

```bash
pip install legisweb-api
```

## Requisitos

- Python 3.7 ou superior
- Biblioteca `requests`

## Uso

```python
from legiswebapi.legisweb_client import LegiswebClient

client = LegiswebClient(token="SEU_TOKEN", codigo_cliente="SEU_CODIGO")

# Exemplo: Consulta ICMS
resposta = client.consulta_icms(ncm="22030000", estado="SP")
print(resposta)

# Exemplo: Consulta PIS/COFINS
resposta = client.consulta_piscofins(ncm="22030000", regime=1, atividade=1)
print(resposta)
```

## Endpoints Suportados

- `consulta_icms(ncm, estado)`
- `consulta_ipi(ncm)`
- `consulta_ii(ncm)`
- `consulta_st_interna(ncm, estado)`
- `consulta_st_interestadual(ncm, uf_origem, uf_destino, destinacao)`
- `consulta_piscofins(ncm, regime, atividade)`
- `consulta_piscofins_importacao(ncm)`
- `consulta_tipi(ncm)`
- `consulta_cfop(codigo)`
- `consulta_ptax(moeda, data)`
- `consulta_agenda_tributaria(data, estado)`
- `consulta_aliquota_padrao(estado)`
- `consulta_nve(ncm)`
- `consulta_defesa_comercial(ncm)`
- `consulta_preferencia_tarifaria(codigo, operacao, pais)`
- `consulta_tratamento_adm_importacao(ncm)`
- `consulta_tratamento_adm_exportacao(ncm)`
- `consulta_produto_ssn(ncm)`
- `consulta_correlacao_ncm(codigo, de, para)`
- `consulta_empresa(cnpj)`
- `consulta_beneficio_fiscal(descricao, estado, categoria)`
- `consulta_pauta_fiscal(estado, busca)`

## Licença

MIT
