
import requests

class LegiswebClient:
    BASE_URL = "https://www.legisweb.com.br/api"

    def __init__(self, token: str, codigo_cliente: str):
        self.token = token
        self.codigo_cliente = codigo_cliente

    def _get(self, endpoint: str, params: dict) -> dict:
        params["t"] = self.token
        params["c"] = self.codigo_cliente
        url = f"{self.BASE_URL}/{endpoint}"
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def consulta_ii(self, ncm: str = None, descricao: str = None, excecao_num: str = None) -> dict:
        """
        Consulta a Tarifa Externa Comum (TEC) da API da Legisweb com base no NCM ou descrição do produto.
        """
        if not any([ncm, descricao]):
            raise ValueError("É necessário informar ao menos um dos parâmetros: ncm ou descricao.")

        params = {}
        if ncm:
            params["ncm"] = ncm
        if descricao:
            params["descricao"] = descricao
        if excecao_num:
            params["excecao_num"] = excecao_num

        return self._get("ii", params)

    def consulta_ipi(
        self, 
        ncm: str = None, 
        codigo: str = None,
        descricao: str = None, 
        excecao_num: str = None
    ) -> dict:        
        """
        Consulta a API da Legisweb para obter a alíquota de IPI de um produto.

        Parâmetros:
            ncm (str, opcional): Código NCM do produto.
            codigo (str, opcional): Código do registro conforme cadastro da Legisweb.
            descricao (str, opcional): Descrição textual do produto (mínimo 2 caracteres).
            excecao_num (str, opcional): Número da exceção tarifária.

        Observação:
            É obrigatório informar pelo menos um entre: `ncm`, `codigo` ou `descricao`.

        Retorno:
            dict: Dicionário com os dados do IPI, incluindo alíquota, exceções, observações e base legal.

        Exemplo:
            client.consulta_ipi(ncm="34012090", excecao_num="001")
        """
        if not any([ncm, codigo, descricao]):
            raise ValueError("É necessário informar ao menos um dos parâmetros: ncm ou codigo ou descricao.")
        params = {}
        if ncm:
            params["ncm"] = ncm
        if codigo:
            params["codigo"] = codigo
        if descricao:
            params["descricao"] = descricao
        if excecao_num:
            params["excecao_num"] = excecao_num

        return self._get("ipi", params)

    def consulta_icms(
        self,
        estado: str,
        ncm: str = None,
        codigo: str = None,
        descricao: str = None,
        modo_busca: bool = False
    ) -> dict:
        """
        Consulta a API da Legisweb para obter a alíquota de ICMS de um produto por Estado.

        Parâmetros:
            estado (str): Sigla da unidade federativa (ex: 'SP', 'MG').
            ncm (str, opcional): Código NCM do produto.
            codigo (str, opcional): Código do registro do produto.
            descricao (str, opcional): Descrição do produto com no mínimo 2 caracteres.
            modo_busca (bool, opcional): Quando True, ativa busca por subposição da NCM (6 dígitos).

        Observação:
            É obrigatório informar pelo menos um entre: `ncm`, `codigo` ou `descricao`.

        Retorno:
            dict: Dicionário com os dados de ICMS, incluindo alíquotas, FCP, base legal e vigência.

        Exemplo:
            client.consulta_icms(estado="SP", descricao="cerveja", modo_busca=True)
        """
        if not any([ncm, codigo, descricao]):
            raise ValueError("É necessário informar ao menos um dos parâmetros: ncm, codigo ou descricao.")

        params = {"estado": estado}
        if ncm:
            params["ncm"] = ncm
        if codigo:
            params["codigo"] = codigo
        if descricao:
            params["descricao"] = descricao
        if modo_busca:
            params["modo_busca"] = "1"

        return self._get("icms", params)

    def consulta_piscofins(
        self,
        regime_tributario_origem: int,
        atividade_origem: int,
        ncm: str = None,
        atividade_destino: int = None,
        descricao: str = None,
        excecao_num: str = None,
        aliquota_padrao: bool = False
    ) -> dict:
        """
        Consulta a API da Legisweb para obter as alíquotas e regras de PIS e COFINS de um produto.

        Esta função realiza uma requisição à API de PIS/COFINS da Legisweb utilizando parâmetros
        relacionados ao regime tributário, atividade econômica e classificação do produto.

        Parâmetros:
            regime_tributario_origem (int): Código do regime tributário da empresa de origem.
                - 1 = Lucro Presumido
                - 2 = Lucro Real
                - 3 = Simples Nacional

            atividade_origem (int): Código da atividade econômica da empresa de origem.
                - 1 = Atacadista
                - 2 = Distribuidor
                - 3 = Fabricante
                - 4 = Varejista

            ncm (str, opcional): Código NCM do produto. Obrigatório se `descricao` não for informado.

            atividade_destino (int, opcional): Código da atividade econômica da empresa de destino.
                - 1 = Atacadista
                - 2 = Distribuidor
                - 3 = Fabricante
                - 4 = Varejista

            descricao (str, opcional): Descrição do produto com pelo menos 2 caracteres. Obrigatório se `ncm` não for informado.

            excecao_num (str, opcional): Número de exceção do produto (EX tarifário).

            aliquota_padrao (bool, opcional): Se True, retorna apenas a alíquota padrão (valor `"1"` na requisição).

        Retorno:
            dict: Dicionário com os dados retornados da API, incluindo:
                - regras de aplicação
                - valores de alíquota
                - CST de PIS/COFINS
                - base legal
                - identificadores de regime e atividades

        Exceções:
            ValueError: Se nenhum dos parâmetros `ncm` ou `descricao` for fornecido.

        Exemplo de uso:
            client.consulta_piscofins(
                regime_tributario_origem=2,
                atividade_origem=1,
                ncm="22030000",
                aliquota_padrao=True
            )
        """
        if not any([ncm, descricao]):
            raise ValueError("É necessário informar ao menos um dos parâmetros: ncm ou descricao.")

        params = {
            "regime_tributario_origem": regime_tributario_origem,
            "atividade_origem": atividade_origem,
        }

        if ncm:
            params["ncm"] = ncm
        if atividade_destino:
            params["atividade_destino"] = atividade_destino
        if descricao:
            params["descricao"] = descricao
        if excecao_num:
            params["excecao_num"] = excecao_num
        if aliquota_padrao:
            params["aliquota_padrao"] = "1"

        return self._get("piscofins", params)

    def consulta_piscofins_importacao(self, ncm: str = None, codigo: str = None, descricao: str = None) -> dict:
        """
        Consulta as alíquotas de PIS/COFINS na importação de produtos.
        """
        if not any([ncm, codigo, descricao]):
            raise ValueError("É necessário informar ao menos um dos parâmetros: ncm, codigo ou descricao.")

        params = {}
        if ncm:
            params["ncm"] = ncm
        if codigo:
            params["codigo"] = codigo
        if descricao:
            params["descricao"] = descricao

        return self._get("piscofins-importacao", params)

    def consulta_tipi(
        self,
        ncm: str = None,
        codigo: str = None,
        descricao: str = None,
        excecao_num: str = None
    ) -> dict:
        """
        Consulta a Tabela TIPI (Tabela de Incidência do IPI) na API da Legisweb.

        Parâmetros:
            ncm (str, opcional): Código NCM do produto.
            codigo (str, opcional): Código interno da TIPI.
            descricao (str, opcional): Descrição do produto (mínimo 2 caracteres).
            excecao_num (str, opcional): Número da exceção tarifária.

        Observação:
            É obrigatório informar pelo menos um entre: `ncm`, `codigo` ou `descricao`.

        Retorno:
            dict: Informações completas da TIPI, incluindo capítulo, seção, alíquota e observações.

        Exemplo:
            client.consulta_tipi(descricao="refrigerante")
        """
        if not any([ncm, codigo, descricao]):
            raise ValueError("É necessário informar ao menos um dos parâmetros: ncm, codigo ou descricao.")

        params = {}
        if ncm:
            params["ncm"] = ncm
        if codigo:
            params["codigo"] = codigo
        if descricao:
            params["descricao"] = descricao
        if excecao_num:
            params["excecao_num"] = excecao_num

        return self._get("tipi", params)

    def consulta_st_interna(
        self,
        estado: str,
        ncm: str = None,
        codigo: str = None,
        descricao: str = None,
        cest: str = None,
        regime_tributario_destino: int = None
    ) -> dict:
        """
        Consulta a Substituição Tributária (ST) Interna para um determinado estado via API da Legisweb.

        Parâmetros:
            estado (str): Sigla do estado (ex: 'SP', 'PR').
            ncm (str, opcional): Código NCM do produto.
            codigo (str, opcional): Código do registro.
            descricao (str, opcional): Descrição textual do produto (mínimo 2 caracteres).
            cest (str, opcional): Código CEST do produto.
            regime_tributario_destino (int, opcional): Se estado = PR, deve indicar o regime tributário:
                - 1 = Regime Normal
                - 2 = Simples Nacional

        Observação:
            É obrigatório informar ao menos um dos seguintes: `ncm`, `codigo` ou `descricao`.

        Retorno:
            dict: Dados da ST interna, incluindo alíquotas, MVA, base de cálculo e base legal.

        Exemplo:
            client.consulta_st_interna(estado="SP", ncm="22030000")
        """
        if not any([ncm, codigo, descricao]):
            raise ValueError("É necessário informar ao menos um dos parâmetros: ncm, codigo ou descricao.")

        params = {"estado": estado}
        if ncm:
            params["ncm"] = ncm
        if codigo:
            params["codigo"] = codigo
        if descricao:
            params["descricao"] = descricao
        if cest:
            params["cest"] = cest
        if regime_tributario_destino:
            params["regime_tributario_destino"] = str(regime_tributario_destino)

        return self._get("st-interna", params)

    def consulta_st_interestadual(
        self,
        uf_origem: str,
        uf_destino: str,
        destinacao: int,
        ncm: str = None,
        codigo: str = None,
        descricao: str = None,
        cest: str = None,
        regime_tributario_origem: int = None,
        regime_tributario_destino: int = None,
        opt_cred_presumido: int = None,
        id_segmento: int = None
    ) -> dict:
        """
        Consulta a Substituição Tributária (ST) em operações interestaduais via API da Legisweb.

        Parâmetros obrigatórios:
            estado_origem (str): UF do remetente (ex: 'SP').
            estado_destino (str): UF do destinatário (ex: 'RJ').
            destinacao_mercadoria (int): Código do tipo de operação:
                - 1 = Op. Subsequente - Comercialização
                - 2 = Ativo Fixo ou Imobilizado
                - 3 = Uso e Consumo
                - 4 = Transferência para Varejista

        Pelo menos um dos seguintes deve ser informado:
            ncm (str, opcional): Código NCM do produto.
            codigo (str, opcional): Código interno do item.
            descricao (str, opcional): Descrição do produto.
            cest (str, opcional): Código CEST.

        Parâmetros adicionais opcionais:
            regime_tributario_origem (int): 1 = Normal, 2 = Simples Nacional
            regime_tributario_destino (int): 1 = Normal, 2 = Simples Nacional
            opt_cred_presumido (int): 0 = Não, 1 = Sim
            id_segmento (int): ID do segmento, conforme retorno da API

        Retorno:
            dict: Dados sobre MVA, alíquota, base de cálculo, observações e legislação aplicada.

        Exemplo:
            client.consulta_st_interestadual(
                estado_origem="SP",
                estado_destino="MG",
                destinacao_mercadoria=1,
                ncm="22030000"
            )
        """
        if not any([ncm, codigo, descricao, cest]):
            raise ValueError("É necessário informar ao menos um entre: ncm, codigo, descricao ou cest.")

        params = {
            "estado_origem": uf_origem,
            "estado_destino": uf_destino,
            "destinacao_mercadoria": destinacao,
        }
        if ncm:
            params["ncm"] = ncm
        if codigo:
            params["codigo"] = codigo
        if descricao:
            params["descricao"] = descricao
        if cest:
            params["cest"] = cest
        if regime_tributario_origem:
            params["regime_tributario_origem"] = regime_tributario_origem
        if regime_tributario_destino:
            params["regime_tributario_destino"] = regime_tributario_destino
        if opt_cred_presumido is not None:
            params["opt_cred_presumido"] = opt_cred_presumido
        if id_segmento:
            params["id_segmento"] = id_segmento

        return self._get("st-interestadual", params)

    def consulta_preferencia_tarifaria(self, codigo: str, operacao: int, pais: int) -> dict:
        return self._get("preferencia-tarifaria", {
            "codigo": codigo,
            "operacao": operacao,
            "pais": pais,
            "codigo_exato": 1
        })

    def consulta_nve(self, ncm: str) -> dict:
        return self._get("nve", {"ncm": ncm})

    def consulta_ptax(self, moeda: str, data: str) -> dict:
        return self._get("ptax", {"moeda": moeda, "data": data})

    def consulta_defesa_comercial(self, ncm: str) -> dict:
        return self._get("defesa-comercial", {"ncm": ncm})

    def consulta_cide_combustivel(self, ncm: str) -> dict:
        return self._get("cide-combustivel", {"ncm": ncm})

    def consulta_tratamento_adm_importacao(self, ncm: str) -> dict:
        return self._get("tratamento-administrativo-importacao", {"ncm": ncm, "grupo_busca": "ncm"})

    def consulta_tratamento_adm_exportacao(self, ncm: str) -> dict:
        return self._get("tratamento-administrativo-exportacao", {"ncm": ncm, "grupo_busca": "ncm"})

    def consulta_produto_ssn(self, ncm: str) -> dict:
        return self._get("produto-ssn", {"ncm": ncm})

    def consulta_correlacao_ncm(
        self,
        codigo: str,
        de: str,
        para: str
    ) -> dict:
        """
        Consulta a correlação entre códigos fiscais: NBM, NCM e NALADI via API da Legisweb.

        Parâmetros:
            codigo (str): Código a ser convertido (ex: '22030000').
            de (str): Origem do código. Pode ser:
                - 'nbm'
                - 'ncm'
                - 'naladi'
            para (str): Destino da conversão. Pode ser:
                - 'nbm'
                - 'ncm'
                - 'naladi'

        Retorno:
            dict: Dicionário contendo os códigos equivalentes, descrição do produto e histórico de correlação.

        Exemplo:
            client.consulta_correlacao_ncm(codigo="22030000", de="nbm", para="ncm")
        """
        if de not in {"nbm", "ncm", "naladi"} or para not in {"nbm", "ncm", "naladi"}:
            raise ValueError("Parâmetros 'de' e 'para' devem ser um dos seguintes: 'nbm', 'ncm', 'naladi'.")

        params = {
            "codigo": codigo,
            "de": de,
            "para": para
        }

        return self._get("correlacao-nbm-ncm-naladi", params)
        
    def consulta_pauta_fiscal(
        self,
        estado: str,
        busca: str,
        opcao: int = 1,
        categoria: str = None,
        descricao: str = None,
        produto: str = None,
        marca: str = None,
        caracteristica: str = None,
        codigo_barras: str = None,  
    ) -> dict:
        """
        Consulta a pauta fiscal (preço mínimo fiscal) para um produto em determinado estado via API da Legisweb.

        Parâmetros obrigatórios:
            estado (str): Sigla da UF de consulta (ex: 'SP', 'RJ').
            opcao indica o tipo de busca:
                - 1 Tudo
                - 2 Categoria
                - 3 Descrição
                - 4 Produto
                - 5 Marca
                - 6 Característica
                - 7 Código de Barras
                - 8 Busca Combinada
            busca (str): Palavra-chave de busca conforme opcão escolhida.
            
        Parâmetros opcionais:
            se opção informado for 8, ao menos um dos parâmetros abaixo devem ser informados:
            - categoria
            - descricao
            - produto
            - marca
            - caracteristica
            - codigo_barras

        Retorno:
            dict: Informações da pauta fiscal, incluindo:
        """
        if not any([estado, busca]):
            raise ValueError("É necesario informar ao menos os parâmetros: estado e busca.")
        
        if opcao == 8 and not any([ descricao, produto, marca, caracteristica, codigo_barras, categoria]):
            raise ValueError("Quando a opção for 8, é necessário informar ao menos um dos parâmetros: categoria, descrição,produto, marca, caracteristica ou codigo_barras")

        params = {"estado": estado, "busca": busca, "opcao": opcao}        
        if descricao:
            params["descricao"] = descricao
        if produto:
            params["produto"] = produto
        if marca:
            params["marca"] = marca
        if caracteristica:
            params["caracteristica"] = caracteristica
        if codigo_barras:
            params["codigo_barras"] = codigo_barras
        if categoria:
            params["categoria"] = categoria

        return self._get("pauta-fiscal", params)

    def consulta_agenda_tributaria(
        self,
        data: str,
        incluir_estadual: bool = False,
        incluir_municipal: bool = False,
        estado: str = None,
        municipio: str = None
    ) -> dict:
        """
        Consulta a agenda tributária nacional, estadual e/ou municipal via API da Legisweb.

        Parâmetros:
            data (str): Data da agenda no formato 'dd/mm/yyyy'.
            incluir_estadual (bool, opcional): Se True, inclui tributos estaduais na agenda.
            incluir_municipal (bool, opcional): Se True, inclui tributos municipais na agenda.
            estado (str, opcional): UF da agenda estadual.
            municipio (str, opcional): Nome do município para agenda municipal.

        Retorno:
            dict: Lista de obrigações acessórias e tributos com vencimento na data informada,
                contendo descrições, códigos de receita, esfera de aplicação e base legal.

        Exemplo:
            client.consulta_agenda_tributaria(
                data="17/05/2025",
                incluir_estadual=True,
                estado="SP"
            )
        """
        params = {"data": data}
        if incluir_estadual:
            params["estadual"] = 1
        if incluir_municipal:
            params["municipal"] = 1
        if estado:
            params["estado"] = estado
        if municipio:
            params["municipio"] = municipio

        return self._get("agenda-tributaria", params)

    def consulta_beneficio_fiscal(
        self,
        estado: str,
        categoria: int,
        ncm: str = None,
        descricao: str = None,
        codigo: str = None
    ) -> dict:
        """
        Consulta os benefícios fiscais de ICMS disponíveis para um produto em um determinado estado.

        Parâmetros:
            estado (str): Sigla da UF onde o benefício é vigente (ex: 'SP', 'MG').
            categoria (int): Código da categoria do benefício fiscal:
                - 2 = Reduções de Base de Cálculo
                - 3 = Isenções
                - 4 = Créditos Presumidos/Outorgados
                - 5 = Deferimentos

        Pelo menos um dos seguintes parâmetros deve ser informado:
            ncm (str, opcional): Código NCM do produto.
            descricao (str, opcional): Descrição textual do produto (mínimo 2 caracteres).
            codigo (str, opcional): Código do benefício.

        Retorno:
            dict: Dicionário com os dados do benefício, incluindo:
                - ID, descrição, base legal, vigência, observações e tabelas específicas (reduções, isenções, créditos).

        Exemplo:
            client.consulta_beneficio_fiscal(
                estado="SP",
                categoria=3,
                ncm="84128000"
            )
        """
        if not any([ncm, descricao, codigo]):
            raise ValueError("É necessário informar ao menos um dos parâmetros: ncm, descricao ou codigo.")

        params = {
            "estado": estado,
            "categoria": categoria
        }
        if ncm:
            params["ncm"] = ncm
        if descricao:
            params["descricao"] = descricao
        if codigo:
            params["codigo"] = codigo

        return self._get("beneficio-fiscal", params)

    def consulta_empresa(
        self,
        empresa: str = None,
        cnae: str = None,
        data_inicio: str = None,
        data_fim: str = None,
        estado: str = None,
        cidade: str = None,
        situacao_cadastral: int = None,
        matriz: int = None,
        pagina: int = None
    ) -> dict:
        """
        Consulta informações cadastrais e tributárias de empresas via API da Legisweb (dados públicos do CNPJ).

        Parâmetros obrigatórios:
            É necessário informar ao menos um dos seguintes:
                - empresa (str): Nome, Fantasia ou CNPJ
                - cnae (str): Código CNAE (7 dígitos)
                - data_inicio (str): Data inicial da atividade no formato dd/mm/yyyy
                (obrigatório se `data_fim` for informado)

        Parâmetros opcionais:
            data_fim (str): Data final da atividade (se for usado `data_inicio`)
            estado (str): Sigla da UF
            cidade (str): Nome da cidade
            situacao_cadastral (int): 1 = Nulo, 2 = Ativa, 3 = Suspensa, 4 = Inapta, 5 = Baixada
            matriz (int): 1 = Matriz, 2 = Filial
            pagina (int): Página para paginação dos resultados (máximo 50 por página)

        Retorno:
            dict: Dicionário contendo:
                - CNPJ, razão social, nome fantasia, CNAE, regime tributário, endereço, porte, situação, capital, etc.

        Exemplo:
            client.consulta_empresa(empresa="10750466000168")
        """
        if not any([empresa, cnae, (data_inicio and data_fim)]):
            raise ValueError("Informe 'empresa', 'cnae' ou o intervalo 'data_inicio' e 'data_fim' para consulta.")

        params = {}
        if empresa:
            params["empresa"] = empresa
        if cnae:
            params["cnae"] = cnae
        if data_inicio:
            params["data_inicio"] = data_inicio
        if data_fim:
            params["data_fim"] = data_fim
        if estado:
            params["estado"] = estado
        if cidade:
            params["cidade"] = cidade
        if situacao_cadastral:
            params["situacao_cadastral"] = situacao_cadastral
        if matriz:
            params["matriz"] = matriz
        if pagina:
            params["p"] = pagina

        return self._get("empresas", params)

    def consulta_cfop(
        self,
        codigo: str = None,
        descricao: str = None
    ) -> dict:
        """
        Consulta CFOP (Código Fiscal de Operações e Prestações) na API da Legisweb.

        Parâmetros:
            codigo (str, opcional): Código numérico do CFOP (ex: '5201', sem ponto).
            descricao (str, opcional): Texto da operação (ex: "Devolução de compra").

        Observação:
            É obrigatório informar ao menos um dos parâmetros: `codigo` ou `descricao`.

        Retorno:
            dict: Dicionário contendo:
                - código, título, descrição do CFOP
                - seção (título e descrição)
                - operação associada (código, título e descrição)
                - legislação aplicável

        Exemplo:
            client.consulta_cfop(codigo="5201")
        """
        if not any([codigo, descricao]):
            raise ValueError("É necessário informar ao menos um dos parâmetros: codigo ou descricao.")

        params = {}
        if codigo:
            params["codigo"] = codigo
        if descricao:
            params["descricao"] = descricao

        return self._get("cfop", params)

    def consulta_aliquota_padrao(self, estado: str) -> dict:
        """
        Consulta a alíquota padrão de ICMS e FCP (Fundo de Combate à Pobreza) para um determinado estado.

        Parâmetros:
            estado (str): Sigla da unidade federativa (ex: 'SP', 'MG', 'RJ').

        Retorno:
            dict: Dicionário com os seguintes campos:
                - tipo (str): Tipo da alíquota ('Alíquota ICMS' ou 'Alíquota FCP')
                - estado (str): UF consultada
                - aliquota (str): Valor percentual da alíquota
                - descricao (str): Descrição da base legal
                - base_legal (str): Texto legal da norma

        Exemplo:
            client.consulta_aliquota_padrao("SP")
        """
        return self._get("aliquota-padrao", {"estado": estado})

def consulta_gtin(self, gtin: str, cod_cert: str) -> dict:
    """
    Consulta o Cadastro Centralizado de GTIN (CCG) via API da Legisweb.

    Parâmetros:
        gtin (str): Código GTIN do produto (ex: código de barras).
        cod_cert (str): Código do certificado digital A1 cadastrado na plataforma da Legisweb.

    Retorno:
        dict: Dicionário com os dados do produto, incluindo:
            - c_status: Código de status do retorno
            - motivo: Descrição da resposta
            - gtin: Código GTIN consultado
            - produto: Nome do produto
            - ncm: NCM associado ao produto
            - cest: CEST (se disponível)
   
    """
    params = {
        "gtin": gtin,
        "cod_cert": cod_cert
    }
    return self._get("gtin", params)