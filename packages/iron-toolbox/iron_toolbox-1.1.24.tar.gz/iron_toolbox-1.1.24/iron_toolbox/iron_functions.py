import datetime
from unidecode import unidecode


def tratar_idade(birthdate):
    """ Função para gerar idade do paciente
        today = dia atual
        one_or_zero = booleano para saber se o dia precede dia/ano do aniversário dia/ano
    """
    data_atual = datetime.date.today()
    one_or_zero = ((data_atual.month, data_atual.day) < (birthdate.month, birthdate.day))

    year_difference = data_atual.year - birthdate.year
    idade = year_difference - one_or_zero

    return idade


def preencher_vazios(dataset):
    for coluna in dataset.columns:
        if dataset[coluna].dtypes.name == 'string':
            dataset[coluna].fillna('N/A', inplace=True)
            continue
        elif dataset[coluna].dtypes.name == 'boolean':
            dataset[coluna].fillna(False, inplace=True)

    return dataset


def tratar_especialidade_agendamento(especialidade_aps):
    # dataset[coluna_especialidade] = dataset[coluna_especialidade].title()
    if ('INQ' in especialidade_aps.upper()) | ('QUESTION' in especialidade_aps.upper()):
        especialidade_aps = 'Inquérito'
    elif 'FARM' in especialidade_aps.upper():
        especialidade_aps = 'Farmacêutico'
    elif ('MEDICO' in unidecode(especialidade_aps.upper())) & ('CLINICO' in unidecode(especialidade_aps.upper())):
        especialidade_aps = 'Médico Clínico'
    elif  'CLINICA MEDICA' in unidecode(especialidade_aps.upper()):
        especialidade_aps = 'Médico Clínico'
    elif ('MEDICO' in especialidade_aps.upper()) & ('FAMILIA' in unidecode(especialidade_aps.upper())):
        especialidade_aps = 'Médico Família e Comunidade'
    elif 'FAMILIA' in unidecode(especialidade_aps.upper()):
        especialidade_aps = 'Médico Família e Comunidade'
    elif 'TECNI' in especialidade_aps.upper():
        especialidade_aps = 'Técnico de Enfermagem'
    elif 'CARDIO' in especialidade_aps.upper():
        especialidade_aps = 'Cardiologista'
    elif 'OFTAL' in especialidade_aps.upper():
        especialidade_aps = 'Oftalmologista'
    elif 'NUTR' in especialidade_aps.upper():
        especialidade_aps = 'Nutricionista'
    elif 'EDUC' in especialidade_aps.upper():
        especialidade_aps = 'Educador Físico'
    elif 'FISIOT' in especialidade_aps.upper():
        especialidade_aps = 'Fisioterapeuta'
    elif 'PSI' in especialidade_aps.upper():
        especialidade_aps = 'Psicólogo'
    elif ('ENF' in unidecode(especialidade_aps.upper())) & ('ASS' in unidecode(especialidade_aps.upper())):
        especialidade_aps = 'Enfermeiro Assistente de Saúde'
    elif 'ENF' in especialidade_aps.upper():
        especialidade_aps = 'Enfermeiro Clínico'
    elif 'SOCIAL' in especialidade_aps.upper():
        especialidade_aps = 'Assistente Social'
    elif 'ASSISTENTE DE SAUDE' in especialidade_aps.upper():
        especialidade_aps = 'Assistente de Saúde'
    elif 'DERMA' in especialidade_aps.upper():
        especialidade_aps = 'Dermatologista'
    elif 'ENDOC' in especialidade_aps.upper():
        especialidade_aps = 'Endocrinologista'
    elif 'GASTRO' in especialidade_aps.upper():
        especialidade_aps = 'Gastroenterologista'
    elif 'GERIA' in especialidade_aps.upper():
        especialidade_aps = 'Geriatra'
    elif 'ORTO' in especialidade_aps.upper():
        especialidade_aps = 'Ortopedista e Traumatologista'
    elif 'OROTTINO' in especialidade_aps.upper():
        especialidade_aps = 'Otorrinolaringologista'
    elif 'PEDIATR' in especialidade_aps.upper():
        especialidade_aps = 'Pediatra'
    elif 'URG' in especialidade_aps.upper():
        especialidade_aps = 'Urgência'
    elif 'GINE' in especialidade_aps.upper():
        especialidade_aps = 'Ginecologia e Obstetricia'
    elif 'UROLO' in especialidade_aps.upper():
        especialidade_aps = 'Urologia'
    elif 'PRIMEIRA' in especialidade_aps.upper():
        especialidade_aps = 'Primeira Avaliação Médica'
    elif 'PREVENTIVA' in especialidade_aps.upper():
        especialidade_aps = 'Medicina Preventiva'
    elif 'ANGIO' in especialidade_aps.upper():
        especialidade_aps = 'Angiologia'
    elif 'ALERG' in especialidade_aps.upper():
        especialidade_aps = 'Alergia e Imunologia'
    elif 'NEFRO' in especialidade_aps.upper():
        especialidade_aps = 'Nefrologia'
    else:
        especialidade_aps = especialidade_aps
    return especialidade_aps



def tratar_especialidade_encaminhamento(especialidade_enc):
    # dataset[coluna_especialidade] = dataset[coluna_especialidade].title()
    if ('emerg' in especialidade_enc.lower()) | ('urg' in especialidade_enc.lower()) | \
            ('interna' in especialidade_enc.lower()):
        especialidade = 'Emergência'
    elif ('interna' in especialidade_enc.lower()) | ('socor' in especialidade_enc.lower()) | \
            ('emr' in especialidade_enc.lower()):
        especialidade = 'Emergência'
    elif ('encaminhamento_medico_ao_ps' in especialidade_enc.lower()) | \
            ('encaminhamento_ao_ps' in especialidade_enc.lower()):
        especialidade = 'Emergência'
    elif 'alerg' in especialidade_enc.lower():
        especialidade = 'Alergista'
    elif 'alerg' in especialidade_enc.lower():
        especialidade = 'Alergista'
    elif 'angi' in especialidade_enc.lower():
        especialidade = 'Angiologista'
    elif 'cardio' in especialidade_enc.lower():
        especialidade = 'Cardiologista'
    elif 'geral' in especialidade_enc.lower():
        especialidade = 'Clínico Geral'
    elif 'derma' in especialidade_enc.lower():
        especialidade = 'Dermatologista'
    elif 'nurse' in especialidade_enc.lower():
        especialidade = 'Enfermagem'
    elif 'endoc' in especialidade_enc.lower():
        especialidade = 'Endocrinologista'
    elif 'farmac' in especialidade_enc.lower():
        especialidade = 'Farmacêutico'
    elif 'fisiot' in especialidade_enc.lower():
        especialidade = 'Fisioterapeuta'
    elif 'fonoaud' in especialidade_enc.lower():
        especialidade = 'Fonoaudiologia'
    elif 'gastro' in especialidade_enc.lower():
        especialidade = 'Gastroenterologista'
    elif 'geria' in especialidade_enc.lower():
        especialidade = 'Geriatra'
    elif 'ginec' in especialidade_enc.lower():
        especialidade = 'Ginecologista'
    elif 'hemat' in especialidade_enc.lower():
        especialidade = 'Hematologista'
    elif 'infec' in especialidade_enc.lower():
        especialidade = 'Infectologista'
    elif 'mastol' in especialidade_enc.lower():
        especialidade = 'Mastologia'
    elif 'medicina_de_familia_e_comunidade' in especialidade_enc.lower():
        especialidade = 'Medicina de Familia e Comunidade'
    elif 'medicina_do_trabalho' in especialidade_enc.lower():
        especialidade = 'Medicina do Trabalho'
    elif 'medicina_esportiva' in especialidade_enc.lower():
        especialidade = 'Medicina Esportiva'
    elif 'medicina_fisica_e_reabilitacao' in especialidade_enc.lower():
        especialidade = 'Medicina Fisica e Reabilitacao'
    elif 'medicina_preventiva_e_social' in especialidade_enc.lower():
        especialidade = 'Medicina Preventiva e Social'
    elif 'nefr' in especialidade_enc.lower():
        especialidade = 'Nefrologia'
    elif 'neur' in especialidade_enc.lower():
        especialidade = 'Neurologista'
    elif 'nutri' in especialidade_enc.lower():
        especialidade = 'Nutricionista'
    elif 'odonto' in especialidade_enc.lower():
        especialidade = 'Odontologista'
    elif 'ofta' in especialidade_enc.lower():
        especialidade = 'Oftalmologista'
    elif 'ortop' in especialidade_enc.lower():
        especialidade = 'Ortopedista'
    elif 'osteop' in especialidade_enc.lower():
        especialidade = 'Osteopatia'
    elif 'otorr' in especialidade_enc.lower():
        especialidade = 'Otorrinolaringologista'
    elif 'patologia_clinicamedicina_laboratorial' in especialidade_enc.lower():
        especialidade = 'Patologia Clinica Medicina Laboratorial'
    elif 'pedia' in especialidade_enc.lower():
        especialidade = 'Pediatra'
    elif ('pneu' in unidecode(especialidade_enc.lower())) | ('penu' in unidecode(especialidade_enc.lower())):
        especialidade = 'Pneumologista'
    elif 'procto' in especialidade_enc.lower():
        especialidade = 'Proctologista'
    elif 'pronto_atend' in especialidade_enc.lower():
        especialidade = 'Pronto Atendimento'
    elif 'psic' in especialidade_enc.lower():
        especialidade = 'Psicólogo'
    elif 'psiq' in especialidade_enc.lower():
        especialidade = 'Psiquiatra'
    elif ('rede' in unidecode(especialidade_enc.lower())) & ('cassi' in unidecode(especialidade_enc.lower())):
        especialidade = 'Rede Credenciada'
    elif 'reuma' in especialidade_enc.lower():
        especialidade = 'Reumatologista'
    elif 'terapia_ocupacional' in especialidade_enc.lower():
        especialidade = 'Terapia Ocupacional'
    elif 'urol' in especialidade_enc.lower():
        especialidade = 'Urologista'
    elif especialidade_enc.lower() != '':
        especialidade = 'Não Especificado'
    else:
        especialidade = 'DESCONHECIDO'
    return especialidade


def tratar_uf(dataset, coluna_uf):
    for i in range(len(dataset)):
        dataset[coluna_uf][i] = dataset[coluna_uf][i].upper()
        if dataset[coluna_uf][i].upper() in 'ALAGOAS':
            dataset[coluna_uf][i] = 'AL'
        elif unidecode(dataset[coluna_uf][i].upper()) in 'AMAPA':
            dataset[coluna_uf][i] = 'AP'
        elif dataset[coluna_uf][i].upper() in 'BAHIA':
            dataset[coluna_uf][i] = 'BA'
        elif dataset[coluna_uf][i].upper() in 'MINAS GERAIS':
            dataset[coluna_uf][i] = 'MG'
        elif unidecode(dataset[coluna_uf][i].upper()) in 'CEARA':
            dataset[coluna_uf][i] = 'CE'
        elif unidecode(dataset[coluna_uf][i].upper()) in 'DISTRITO FEDERAL':
            dataset[coluna_uf][i] = 'DF'
        elif unidecode(dataset[coluna_uf][i].upper()) in 'BRASILIA':
            dataset[coluna_uf][i] = 'DF'
        elif unidecode(dataset[coluna_uf][i].upper()) in 'BR':
            dataset[coluna_uf][i] = 'DF'
        elif unidecode(dataset[coluna_uf][i].upper()) in 'ESPIRITO SANTO':
            dataset[coluna_uf][i] = 'ES'
        elif unidecode(dataset[coluna_uf][i].upper()) in 'GOIAS':
            dataset[coluna_uf][i] = 'GO'
        elif unidecode(dataset[coluna_uf][i].upper()) in 'PARAN':
            dataset[coluna_uf][i] = 'PR'
        elif unidecode(dataset[coluna_uf][i].upper()) in 'BH':
            dataset[coluna_uf][i] = 'MG'
        elif unidecode(dataset[coluna_uf][i].upper()) in 'MARANHAO':
            dataset[coluna_uf][i] = 'MA'
        elif unidecode(dataset[coluna_uf][i].upper()) in 'MATO GROSSO DO SUL':
            dataset[coluna_uf][i] = 'MS'
        elif unidecode(dataset[coluna_uf][i].upper()) in 'MATO GROSSO':
            dataset[coluna_uf][i] = 'MT'
        elif unidecode(dataset[coluna_uf][i].upper()) in 'PARA':
            dataset[coluna_uf][i] = 'PA'
        elif unidecode(dataset[coluna_uf][i].upper()) in 'JOAO PESSOA':
            dataset[coluna_uf][i] = 'PB'
        elif unidecode(dataset[coluna_uf][i].upper()) in 'PERNAMBUCO':
            dataset[coluna_uf][i] = 'PE'
        elif unidecode(dataset[coluna_uf][i].upper()) in 'PIAU':
            dataset[coluna_uf][i] = 'PI'
        elif unidecode(dataset[coluna_uf][i].upper()) in 'JANEIRO':
            dataset[coluna_uf][i] = 'RJ'
        elif unidecode(dataset[coluna_uf][i].upper()) in 'RONDONIA':
            dataset[coluna_uf][i] = 'RO'
        elif unidecode(dataset[coluna_uf][i].upper()) in 'CATARINA':
            dataset[coluna_uf][i] = 'SC'
        elif unidecode(dataset[coluna_uf][i].upper()) in 'SUL':
            dataset[coluna_uf][i] = 'RS'
        elif unidecode(dataset[coluna_uf][i].upper()) in 'NORTE':
            dataset[coluna_uf][i] = 'RR'
        elif unidecode(dataset[coluna_uf][i].upper()) in 'PAULO':
            dataset[coluna_uf][i] = 'RJ'
        elif unidecode(dataset[coluna_uf][i].upper()) in 'TOCANTINS':
            dataset[coluna_uf][i] = 'TO'
        elif unidecode(dataset[coluna_uf][i].upper()) in 'SERGIPE':
            dataset[coluna_uf][i] = 'SE'
        elif dataset[coluna_uf][i].upper() in 'MINAS GERAIS':
            dataset[coluna_uf][i] = 'MG'
        elif dataset[coluna_uf][i].upper() in 'SANTA CATARINA':
            dataset[coluna_uf][i] = 'SC'
        elif dataset[coluna_uf][i].upper() in 'EXTREMA':
            dataset[coluna_uf][i] = 'MG'
        elif dataset[coluna_uf][i].upper() in 'MESSIAS':
            dataset[coluna_uf][i] = 'AL'
        elif dataset[coluna_uf][i].upper() in 'PALMEIRINA':
            dataset[coluna_uf][i] = 'PE'
        elif dataset[coluna_uf][i].upper() in 'ITANHAEM':
            dataset[coluna_uf][i] = 'SP'
        elif dataset[coluna_uf][i].upper() in 'ATALAIA':
            dataset[coluna_uf][i] = 'AL'
        elif dataset[coluna_uf][i].upper() in 'UBATA':
            dataset[coluna_uf][i] = 'BA'
        elif dataset[coluna_uf][i].upper() in 'TOLEDO':
            dataset[coluna_uf][i] = 'PR'
        elif dataset[coluna_uf][i].upper() in 'SERRA':
            dataset[coluna_uf][i] = 'ES'
        elif dataset[coluna_uf][i].upper() in 'VALENCA DO PIAUI':
            dataset[coluna_uf][i] = 'PI'
        elif dataset[coluna_uf][i].upper() in 'VICOSA':
            dataset[coluna_uf][i] = 'MG'
        elif dataset[coluna_uf][i].upper() in 'OSASCO':
            dataset[coluna_uf][i] = 'SP'
        elif dataset[coluna_uf][i].upper() in 'RIO GRANDE DO SUL':
            dataset[coluna_uf][i] = 'RS'
        elif dataset[coluna_uf][i].upper() in 'TEOTONIO VILELA':
            dataset[coluna_uf][i] = 'AL'
        elif dataset[coluna_uf][i].upper() in 'ITAPEVA':
            dataset[coluna_uf][i] = 'SP'
        elif dataset[coluna_uf][i].upper() in 'FERRAZ DE VASCONCELOS':
            dataset[coluna_uf][i] = 'SP'
        elif dataset[coluna_uf][i].upper() in 'DIAS DBVILA':
            dataset[coluna_uf][i] = 'BA'
        elif dataset[coluna_uf][i].upper() in 'CATU':
            dataset[coluna_uf][i] = 'BA'
        elif (dataset[coluna_uf][i] in '') | (dataset[coluna_uf][i] in 'IT') | (dataset[coluna_uf][i] in 'VEN'):
            dataset[coluna_uf][i] = 'NÃO INFORMADO'
        elif (dataset[coluna_uf][i] in '-') | (dataset[coluna_uf][i] in '--') | (dataset[coluna_uf][i] in '.'):
            dataset[coluna_uf][i] = 'NÃO INFORMADO'
        elif (dataset[coluna_uf][i] in 'AN') | (dataset[coluna_uf][i] in 'VARGEM') | (dataset[coluna_uf][i] in 'NUMENAL'):
            dataset[coluna_uf][i] = 'NÃO INFORMADO'
    return dataset


def tratar_respostas_consumo_alcool(resposta):
    if ('nao ingere' in unidecode(resposta.lower())) | ('nunca' in unidecode(resposta.lower())):
        resposta = 'Nunca'
    elif unidecode(resposta.lower()) == '2   3 vezes/semana|':
        resposta = '2-3 vezes/semana'
    elif unidecode(resposta.lower()) == '2 -3 vezes/semana':
        resposta = '2-3 vezes/semana'
    elif unidecode(resposta.lower()) == '2   3 vezes/semana':
        resposta = '2-3 vezes/semana'
    elif unidecode(resposta.lower()) == '2 - 3 vezes/semana':
        resposta = '2-3 vezes/semana'
    elif unidecode(resposta.lower()) == 'de 2 a 3 vezes por semana':
        resposta = '2-3 vezes/semana'
    elif 'duas a tres vezes por semana' in unidecode(resposta.lower()):
        resposta = '2-3 vezes/semana'
    elif unidecode(resposta.lower()) == '4 ou mais vezes por semana':
        resposta = '4 vezes/semana ou mais'
    elif 'quatro vezes ou mais por semana' in unidecode(resposta.lower()):
        resposta = '4 vezes/semana ou mais'
    elif unidecode(resposta.lower()) == '4 ou mais vezes / semana':
        resposta = '4 vezes/semana ou mais'
    elif unidecode(resposta.lower()) == 'quatro_vezes_ou_mais_por_semana':
        resposta = '4 vezes/semana ou mais'
    elif '4 ou mais vezes/semana' in unidecode(resposta.lower()):
        resposta = '4 vezes/semana ou mais'
    elif unidecode(resposta.lower()) == 'mensalmente ou menos':
        resposta = '1 vez/mes ou menos'
    elif unidecode(resposta.lower()) == 'uma_vez_por_mes_ou_menos':
        resposta = '1 vez/mes ou menos'
    elif unidecode(resposta.lower()) == '1 vez/mes ou menos|':
        resposta = '1 vez/mes ou menos'
    elif unidecode(resposta.lower()) == '1 vez/mes ou menos':
        resposta = '1 vez/mes ou menos'
    elif 'uma vez por mes ou menos' in unidecode(resposta.lower()):
        resposta = '1 vez/mes ou menos'
    elif unidecode(resposta.lower()) == '2 - 3 vezes/mes':
        resposta = '2-4 vezes/mes'
    elif unidecode(resposta.lower()) == '2 - 4 vezes/mes':
        resposta = '2-4 vezes/mes'
    elif unidecode(resposta.lower()) == 'de 2 a 4 vezes por mes':
        resposta = '2-4 vezes/mes'
    elif unidecode(resposta.lower()) == '2   4 vezes/mes':
        resposta = '2-4 vezes/mes'
    elif unidecode(resposta.lower()) == '2 - 4 vezes/mes':
        resposta = '2-4 vezes/mes'
    elif 'duas a quatro vezes por mes' in unidecode(resposta.lower()):
        resposta = '2-4 vezes/mes'
    elif unidecode(resposta.lower()) == 'duas_a_quatro_vezes_por_mes':
        resposta = '2-4 vezes/mes'
    elif unidecode(resposta.lower()) == '2   4 vezes/mes|':
        resposta = '2-4 vezes/mes'
    elif unidecode(resposta.lower()) == ' 2 - 4 vezes/mes':
        resposta = '2-4 vezes/mes'
    return resposta


def formatar_cnpj(cnpj):
    try:
        cnpj = str(cnpj)
        if len(cnpj) == 14:
          cnpj = f'{cnpj[0:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:14]}'
    finally:
        print('CNPJ_INVALIDO')
    return cnpj


def adicionar_faixa_etaria(dataset, col_idade):
    dataset.loc[dataset[col_idade] < 18, 'FAIXA_ETARIA'] = '< 18'
    dataset.loc[dataset[col_idade].between(18, 34), 'FAIXA_ETARIA'] = '18 a 34'
    dataset.loc[dataset[col_idade].between(35, 49), 'FAIXA_ETARIA'] = '35 a 49'
    dataset.loc[dataset[col_idade].between(50, 64), 'FAIXA_ETARIA'] = '50 a 64'
    dataset.loc[dataset[col_idade] >= 65, 'FAIXA_ETARIA'] = '65 ou mais'
    dataset['FAIXA_ETARIA'].fillna('N/A', inplace=True)

    dataset.loc[dataset[col_idade] < 18, 'FAIXA_ETARIA_ORDEM'] = '1'
    dataset.loc[dataset[col_idade].between(18, 34), 'FAIXA_ETARIA_ORDEM'] = '2'
    dataset.loc[dataset[col_idade].between(35, 49), 'FAIXA_ETARIA_ORDEM'] = '3'
    dataset.loc[dataset[col_idade].between(50, 64), 'FAIXA_ETARIA_ORDEM'] = '4'
    dataset.loc[dataset[col_idade] >= 65, 'FAIXA_ETARIA_ORDEM'] = '5'
    dataset['FAIXA_ETARIA_ORDEM'].fillna('N/A', inplace=True)

    return dataset


def adicionar_faixa_etaria_atendimento(dataset, col_idade, nome_coluna_faixa_etaria, nome_coluna_faixa_etaria_ordem):
    dataset.loc[dataset[col_idade] < 18, nome_coluna_faixa_etaria] = '< 18'
    dataset.loc[dataset[col_idade].between(18, 34), nome_coluna_faixa_etaria] = '18 a 34'
    dataset.loc[dataset[col_idade].between(35, 49), nome_coluna_faixa_etaria] = '35 a 49'
    dataset.loc[dataset[col_idade].between(50, 64), nome_coluna_faixa_etaria] = '50 a 64'
    dataset.loc[dataset[col_idade] >= 65, nome_coluna_faixa_etaria] = '65 ou mais'
    dataset[nome_coluna_faixa_etaria].fillna('N/A', inplace=True)

    dataset.loc[dataset[col_idade] < 18, nome_coluna_faixa_etaria_ordem] = '1'
    dataset.loc[dataset[col_idade].between(18, 34), nome_coluna_faixa_etaria_ordem] = '2'
    dataset.loc[dataset[col_idade].between(35, 49), nome_coluna_faixa_etaria_ordem] = '3'
    dataset.loc[dataset[col_idade].between(50, 64), nome_coluna_faixa_etaria_ordem] = '4'
    dataset.loc[dataset[col_idade] >= 65, nome_coluna_faixa_etaria_ordem] = '5'
    dataset[nome_coluna_faixa_etaria_ordem].fillna('N/A', inplace=True)

    return dataset
