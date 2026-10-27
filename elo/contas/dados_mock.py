"""Dados de exemplo (mock) da área do pesquisador.

As telas Meu cadastro, Meus estudos e Novo projeto ainda não estão ligadas ao
banco: o conteúdo vem daqui, igual aos mockups em claude/prototipo/mapa/
(Cadastro, Pesquisador e Novo). Para ligar ao banco, troque estas estruturas
por consultas que devolvam os mesmos campos.
"""

VINCULOS = [
    'Servidor Ebserh no HU',
    'Docente de IES com atuação no HU',
    'Residente do HU',
    'Profissional do HU com outro vínculo (cedido, fundação, terceirizado)',
    'Docente de IES (sem atuação no HU)',
    'Pós-graduando (mestrado, doutorado, pós-doc)',
    'Graduando (PIC, PIT, TCC)',
    'Pesquisador de outra instituição',
    'Voluntário ou outro',
]

# --- Meu cadastro (Cadastro.dc.html) ---

CADASTRO = {
    'situacao': 'Não enviado',
    'nome': 'Elisa Exemplo Épsilon',
    'email': 'elisa.epsilon@exemplo.edu.br',
    'vinculo': 'Pós-graduando (mestrado, doutorado, pós-doc)',
    'instituicao': 'Universidade de Brasília',
    'area': 'Saúde mental',
    'lattes': 'http://lattes.cnpq.br/0000000000000005',
    'orcid': '0000-0000-0000-0005',
    'telefone': '(61) 90000-0005',
}

# --- Meus estudos (Pesquisador.dc.html) ---

DEVOLUCAO = {
    'codigo': 'HUB-0142/2026',
    'apelido': 'IMUNO-PULMÃO',
    'motivo': (
        'Documento ausente ou desatualizado. Anexar o TCUD com a lista da equipe '
        'e a versão atual do cronograma.'
    ),
    'devolvido_em': '07/10/2026',
    'etapa': 'análise documental',
    'retorno_previsto': '14/10/2026',
    'prazo_dias_uteis': 5,
}

# classe: '' (em andamento), 'aviso' (em tramitação) ou 'ruim' (devolvido).
ESTUDOS = [
    {
        'codigo': 'HUB-0142/2026',
        'titulo': 'Perfil de resposta a imunoterapia em carcinoma de pulmão',
        'apelido': 'IMUNO-PULMÃO',
        'tipo': 'Observacional',
        'situacao': 'Devolvido · retorno até 14/10',
        'classe': 'ruim',
    },
    {
        'codigo': 'HUB-0143/2026',
        'titulo': 'Ensaio de dose única de vitamina D em pós-operatório',
        'apelido': 'VITD-POP',
        'tipo': 'Ensaio clínico',
        'situacao': 'Análise ética (CEP)',
        'classe': 'aviso',
    },
    {
        'codigo': 'HUB-0098/2026',
        'titulo': 'Satisfação com a escala de enfermagem',
        'apelido': 'ESCALA-ENF',
        'tipo': 'Ensino, serviço e gestão',
        'situacao': 'Em andamento',
        'classe': '',
    },
]

PARECER = {
    'codigo': 'HUB-0143/2026',
    'caae': '00000000.0.0000.0000',
    'cep': 'CEP FM-UnB',
    'data': '09/10/2026',
    'resultado': 'Aprovado',
}

RESULTADOS_PARECER = ['Aprovado', 'Pendência', 'Não aprovado']

PRODUTOS = {
    'codigo': 'HUB-0098/2026',
    'itens': [
        {'tipo': 'Artigo científico', 'referencia': 'DOI 10.0000/exemplo.2026.001', 'data': '05/10/2026'},
    ],
}

TIPOS_PRODUTO = [
    'Artigo científico', 'Resumo em congresso', 'Tese ou dissertação', 'Relatório técnico',
    'Material educacional', 'Software ou aplicativo', 'Patente', 'Registro de software',
    'Dispositivo ou protótipo', 'Nota técnica ou parecer', 'Protocolo assistencial', 'Outro',
]

# --- Novo projeto (Novo.dc.html) ---

# (número, título curto para a barra, pendências)
SECOES = [
    (1, 'Identificação', 0),
    (2, 'Classificação', 0),
    (3, 'Níveis acadêmicos', 0),
    (4, 'Produtos', 1),
    (5, 'Local e cronograma', 0),
    (6, 'Orçamento', 2),
    (7, 'Uso do HU', 0),
    (8, 'Equipe', 0),
    (9, 'Documentos', 3),
    (10, 'Declarações', 12),
]
PREENCHIMENTO = 68

IDENTIFICACAO = {
    'titulo': 'Perfil de resposta a imunoterapia em carcinoma de pulmão',
    'apelido': 'IMUNO-PULMÃO',
    'hospital': 'HUB-UnB',
    'tipo': 'Observacional',
    'palavras_chave': 'imunoterapia, pulmão, biomarcadores',
}
HOSPITAIS = ['HUB-UnB', 'HC-UFMG', 'HC-UFPE', 'HU-UFSCar']
TIPOS_ESTUDO = ['Observacional', 'Ensaio clínico', 'Desenvolvimento tecnológico', 'Ensino, serviço e gestão']

# (rótulo, marcado)
CLASSIFICACAO = [
    ('Envolve seres humanos', True),
    ('Multicêntrico', False),
    ('Projeto acadêmico', True),
    ('Desenvolvimento tecnológico', False),
]
TCLE_OPCOES = ['Não se aplica', 'Sim', 'Solicitação de dispensa']
TCLE = 'Solicitação de dispensa'

# Campos do tipo Observacional: (rótulo, valor)
DESENHO = [
    ('Desenho do estudo', 'Coorte'),
    ('Objetivo principal', 'Prognóstico ou preditivo'),
    ('Direção temporal', 'Retrospectivo'),
    ('Fonte dos dados', 'Prontuário'),
    ('Acessa prontuário ou dado identificável', 'Sim'),
    ('Unidade de análise', 'Pessoas'),
    ('Coleta de material biológico', 'Não'),
    ('População especial', 'Nenhuma'),
]

NIVEIS_ACADEMICOS = [
    {'nivel': 'Mestrado', 'pessoa': 'Elisa Exemplo Épsilon', 'orientador': 'Dra. Ana Alfa', 'curso': 'PPG Ciências da Saúde'},
    {'nivel': 'PIC', 'pessoa': 'Lucas Almeida Reis', 'orientador': 'Dra. Ana Alfa', 'curso': 'Medicina, UnB'},
]

PRODUTOS_ESPERADOS = [
    (tipo, tipo in {'Artigo científico', 'Resumo em congresso', 'Tese ou dissertação'})
    for tipo in TIPOS_PRODUTO
]

UNIDADES = [
    ('Oncologia', True), ('Laboratório', True), ('Arquivo médico (SAME)', True),
    ('UTI Adulto', False), ('Ambulatório', False), ('Centro cirúrgico', False),
    ('Pediatria', False), ('Farmácia', False),
]
LOCAL = {
    'fomento': 'CNPq',
    'inicio': '01/12/2026',
    'termino': '30/11/2028',
    'contrapartida': 'Relatório de resultados ao serviço',
}

RUBRICAS = [
    'Pessoal e bolsas', 'Material de consumo', 'Exames e procedimentos',
    'Equipamentos', 'Serviços de terceiros', 'Ressarcimento ao HU', 'Outros',
]
QUEM_CUSTEIA = ['Fomento', 'HU (contrapartida)', 'Patrocinador', 'Próprio pesquisador']
ORCAMENTO = [
    {'rubrica': 'Pessoal e bolsas', 'descricao': 'Bolsa de iniciação científica, 12 meses', 'valor': 14400, 'quem': 'Fomento'},
    {'rubrica': 'Material de consumo', 'descricao': 'Reagentes e kits', 'valor': 9800, 'quem': 'Fomento'},
    {'rubrica': 'Exames e procedimentos', 'descricao': 'Exames de imagem do protocolo', 'valor': 18000, 'quem': 'HU (contrapartida)'},
    {'rubrica': 'Ressarcimento ao HU', 'descricao': 'Uso de sala e equipe de apoio', 'valor': 6000, 'quem': 'Fomento'},
]

USO_HU = [
    ('Espaço físico', False), ('Equipamentos', False), ('Insumos e materiais', False),
    ('Medicamentos e farmácia', False), ('Laboratório e exames', False),
    ('Prontuário ou AGHU', True), ('Tempo de profissionais do HU', True), ('Outro', False),
]
USO_HU_DESCRICAO = (
    'Consulta a prontuários de pacientes com carcinoma de pulmão (arquivo médico) e 4 h '
    'semanais de um profissional da Oncologia para validar casos, por 12 meses.'
)
DEMANDAS_CENTRO = [
    ('Apoio ao recrutamento', False), ('Coleta e processamento de amostras', False),
    ('Enfermagem de pesquisa', False), ('Apoio estatístico e metodológico', True),
    ('Gestão de dados', True), ('Apoio regulatório e ao CEP', False),
    ('Capacitação da equipe', False),
]
DEMANDAS_DETALHE = 'Apoio na análise estatística e no banco de dados, de janeiro a junho de 2027.'

# acesso ao cadastro: Coordenador (atribui as seções e envia), Preenchedor
# (edita as seções que recebeu) ou Leitor (só vê; não recebe seção).
EQUIPE = [
    {
        'nome': 'Dra. Ana Exemplo Alfa', 'email': 'ana.alfa@exemplo.edu.br',
        'papel': 'Coordenador(a)', 'acesso': 'Coordenador',
        'vinculo': 'Docente de IES com atuação no HU',
        'orcid': '0000-0000-0000-0001', 'no_hu': True,
    },
    {
        'nome': 'Elisa Exemplo Épsilon', 'email': 'elisa.epsilon@exemplo.edu.br',
        'papel': 'Estudante', 'acesso': 'Preenchedor',
        'vinculo': 'Pós-graduando (mestrado)',
        'orcid': '0000-0000-0000-0005', 'no_hu': False,
    },
    {
        'nome': 'Dr. Bruno Exemplo Beta', 'email': 'bruno.beta@exemplo.edu.br',
        'papel': 'Orientador(a)', 'acesso': 'Preenchedor',
        'vinculo': 'Residente do HU',
        'orcid': '0000-0000-0000-0002', 'no_hu': True,
    },
    {
        'nome': 'Dra. Clara Exemplo Gama', 'email': 'clara.gama@exemplo.edu.br',
        'papel': 'Responsável no HU', 'acesso': 'Leitor',
        'vinculo': 'Servidor Ebserh no HU',
        'orcid': '0000-0000-0000-0003', 'no_hu': True,
    },
]

# Quem está vendo o formulário quando a URL não diz (índice em EQUIPE).
PREENCHENDO_COMO = 1

# Delegação (Delegacao.dc.html): (seção, título, responsável, situação).
# As declarações (seção 10) não entram: só o coordenador as assume.
DELEGACAO = [
    (1, 'Identificação', 'Dra. Ana Exemplo Alfa', 'Concluída'),
    (2, 'Classificação e desenho do estudo', 'Dra. Ana Exemplo Alfa', 'Concluída'),
    (3, 'Níveis acadêmicos', 'Elisa Exemplo Épsilon', 'Em preenchimento'),
    (4, 'Produtos esperados', 'Elisa Exemplo Épsilon', 'Em preenchimento'),
    (5, 'Local, financiamento e cronograma', 'Dr. Bruno Exemplo Beta', 'Não iniciada'),
    (6, 'Orçamento detalhado', 'Dr. Bruno Exemplo Beta', 'Não iniciada'),
    (7, 'Uso do HU e demandas ao centro de pesquisa', 'Dra. Ana Exemplo Alfa', 'Concluída'),
    (8, 'Equipe de pesquisa', 'Dra. Ana Exemplo Alfa', 'Concluída'),
    (9, 'Documentos', 'Dr. Bruno Exemplo Beta', 'Não iniciada'),
]

DOCUMENTOS = [
    ('Projeto detalhado', True),
    ('Cronograma', True),
    ('Orçamento do estudo', True),
    ('Solicitação de dispensa de TCLE/TALE (carta ao CEP com justificativa)', True),
    ('Currículo Lattes da equipe', True),
    ('Carta de anuência das chefias', True),
    ('Instrumento de coleta de dados', True),
    ('TCUD (termo de uso de dados), por usar prontuário', False),
    ('Carta do orientador', False),
    ('Comprovante de matrícula', False),
]

# (grupo, [(texto, base, marcado)])
DECLARACOES = [
    ('Informações e ética', [
        ('Declaro que as informações são verdadeiras e completas e me comprometo a mantê-las atualizadas.', 'HUB', True),
        ('Só inicio a pesquisa após a aprovação do CEP e as autorizações do hospital; anexo o parecer aprovado.', 'HC-UFPE, HUB', True),
        ('Cumpro e faço cumprir as normas éticas, a LGPD e as normas internas do hospital.', 'HC-UFPE', True),
        ('Alterações relevantes serão comunicadas e, quando couber, reapreciadas.', 'HUB', True),
    ]),
    ('Devolutiva científica', [
        ('Insiro no sistema o texto completo de publicações, livros, registros e patentes do estudo.', 'HUB', True),
        ('Insiro relatórios anuais e o relatório final.', 'HUB', True),
        ('Autorizo a divulgação do projeto e dos produtos no site do hospital.', 'HUB', True),
        ('Ciente de que a não devolução dos resultados restringe trabalhos futuros.', 'HUB', True),
    ]),
    ('Recursos, acesso e confidencialidade', [
        ('Ciente de que o HU só assume os custos declarados como contrapartida.', 'proposto', True),
        ('Acesso institucional é pessoal e intransferível; toda a equipe fará o curso de integração.', 'HC-UFPE, HU-UFSCar', True),
        ('Preservo o sigilo e a privacidade dos participantes, mesmo após o fim do estudo.', 'HC-UFPE, HU-UFSCar', True),
    ]),
    ('Quando se aplicam ao estudo', [
        ('TCUD: uso mínimo e só para o projeto, anonimização, sem copiar ou repassar prontuários, sem reidentificar, comunicar incidentes, guardar 5 anos.', 'HUB, HC-UFPE, HU-UFSCar', False),
        ('Ciente de que o descumprimento do TCUD suspende o projeto e que toda a equipe assina.', 'HUB, HU-UFSCar', False),
        ('Material biológico exige termo específico e nova autorização para outro uso.', 'HUB', False),
        ('Estudo multicêntrico: análise ética única, comunicada aos CEPs dos demais centros.', 'INAEP', False),
    ]),
    ('Equipe', [
        ('Os demais membros da equipe estão cientes e de acordo.', 'HUB', True),
    ]),
]
