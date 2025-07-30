import pymongo
import pandas as pd
import os
from tqdm import tqdm

client = pymongo.MongoClient(os.environ["MONGO_PROD_URL"], port=27017, compressors='zlib', zlibCompressionLevel=1)
db = client.parse_db
print(client.server_info())

''' Funções para download de collections do Mongo '''


def create_table_schema(mongodb_collection):
    schema = []
    if mongodb_collection == 'Support':
        schema = ['_id', '_p_activeStaff', 'job', '_p_patient', '_created_at', '_updated_at', '_p_support', 'startTime',
                  'endTime', 'duration', 'waitingTime', 'status', 'isTransfer', 'rating', 'review', 'fup24', 'fup48',
                  'description', 'symptomsStarted', 'complains', 'exams', 'orientations', 'isGiftCard', 'cid10', 'ciap',
                  'videoEctoscopicExams', 'outsideAppointments', 'illnessAllergies', 'medicines', 'additionalNotes',
                  'ideConsulta']

    if mongodb_collection == 'UserTelephoneCall':
        schema = ['_created_at', '_p_corporation', 'date', '_p_staff', '_p_responsible', '_p_scheduledAppointments',
                  '_p_support', '_p_user', '_updated_at', 'additionalComments', 'duplicatedFlag', 'reason', 'title',
                  'end_time', 'start_time', 'CIDdiagnose', 'CIAPdiagnose', 'contactChannel', 'status', 'serviceReturn',
                  'complains', 'orientations', 'exams', 'medicines', 'fup', 'illnessAllergies', 'note']

    dataframe = pd.DataFrame(columns=schema)
    return dataframe


def remove_pointers(collection):
    for column in collection.columns:
        if column.startswith('_p_'):
            for i in range(0, len(collection[column])):
                string_id = collection.loc[collection[column].notnull()].reset_index(drop=True)[column][0]
                if type(string_id) == str:
                    if len(string_id) > 11:
                        new_string = string_id.split('$')[0]
                        collection = collection.replace({f'{column}': f'^{new_string}\$'}, {f'{column}': f''},
                                                        regex=True)
                        break
                else:
                    continue
    return collection
# def remove_pointers(collection):
#     for column in collection.columns:
#         if column.startswith('_p_'):
#             for i in range(0, len(collection[column])):
#                 string_id = collection[column][i]
#                 if type(string_id) != str:
#                     string_id = ''
#                 if len(string_id) > 11:
#                     new_string = string_id.split('$')[0]
#                     collection = collection.replace({f'{column}': f'^{new_string}\$'}, {f'{column}': f''}, regex=True)
#                 else:
#                     continue
#     return collection


def contar_itens_collection(filtro, mongodb_collection):
    if filtro is None:
        doc_count = db[mongodb_collection].count_documents({})
    else:
        doc_count = db[mongodb_collection].count_documents(filtro)
    print(f'\nNúmero de itens na Collection {mongodb_collection}: {doc_count}')
    return doc_count


def gerar_data_do_ultimo_registro(mongodb_collection):
    data_ultimo_registo = pd.DataFrame(db[mongodb_collection].find({}, {'_updated_at': 1}).sort([('_updated_at',
                                                                                                  -1)]).limit(1))
    return data_ultimo_registo


def gerar_tabela_schema(mongodb_collection='_SCHEMA'):
    contar_itens_collection(filtro=None, mongodb_collection=mongodb_collection)
    dbSchema = pd.DataFrame(tqdm(db[mongodb_collection].find({})))
    print(f'Dataset {mongodb_collection} Criado!')
    return dbSchema


def gerar_tabela_support(filtro=None, colunas=None, mongodb_collection='Support'):
    # contar_itens_collection(filtro, mongodb_collection)
    dbsupport_schema = create_table_schema(mongodb_collection)
    if colunas is None:
        dbsupport = pd.DataFrame(tqdm(db['Support'].find(filtro, {'_id': 1,
                                                                  '_p_activeStaff': 1,
                                                                  'job': 1,
                                                                  '_p_patient': 1,
                                                                  '_created_at': 1,
                                                                  '_updated_at': 1,
                                                                  '_p_support': 1,
                                                                  'startTime': 1,
                                                                  'endTime': 1,
                                                                  'duration': 1,
                                                                  'waitingTime': 1,
                                                                  'status': 1,
                                                                  'isTransfer': 1,
                                                                  'rating': 1,
                                                                  'review': 1,
                                                                  'fup24': 1,
                                                                  'fup48': 1,
                                                                  'symptomsStarted': 1,
                                                                  'complains': 1,
                                                                  'exams': 1,
                                                                  'orientations': 1,
                                                                  'videoEctoscopicExams': 1,
                                                                  'isGiftCard': 1,
                                                                  'outsideAppointments': 1,
                                                                  'illnessAllergies': 1,
                                                                  'medicines': 1,
                                                                  'additionalNotes': 1,
                                                                  'description': 1,
                                                                  'ideConsulta': 1,
                                                                  'staffFailureReport': 1,
                                                                  'cid10': 1,
                                                                  'ciap': 1,
                                                                  'reason': 1,
                                                                  'title': 1,
                                                                  'cabin': 1,
                                                                  'note': 1}), desc="Total itens recebidos:"))
        print(f'Realizando tratamento do Dataset {mongodb_collection}!')
        dbsupport = dbsupport.replace({'_p_patient': r'^_User\$'}, {'_p_patient': ''}, regex=True)
        dbsupport = dbsupport.replace({'_p_activeStaff': r'^Staff\$'}, {'_p_activeStaff': ''}, regex=True)
        dbsupport = dbsupport.replace({'_p_support': r'^Support\$'}, {'_p_support': ''}, regex=True)
        dbsupport = pd.concat([dbsupport, dbsupport_schema])
    else:
        dbsupport = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas), desc="Total itens recebidos:"))
        dbsupport = remove_pointers(dbsupport)

    print(f'Dataset {mongodb_collection} Criado!')
    return dbsupport


def gerar_tabela_corporation(filtro=None, colunas=None, mongodb_collection='Corporation'):
    # contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        dbCorporation = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {'_id': 1,
                                                                               'name': 1,
                                                                               '_created_at': 1,
                                                                               '_updated_at': 1,
                                                                               'job': 1}),
                                          desc="Total itens recebidos:"))
        print(f'Realizando tratamento do Dataset {mongodb_collection}!')
    else:
        dbCorporation = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas), desc="Total itens recebidos:"))
        dbCorporation = remove_pointers(dbCorporation)

    print(f'Dataset {mongodb_collection} Criado!')
    return dbCorporation


def gerar_tabela_corporation_pin(filtro=None, colunas=None, mongodb_collection='CorporationPin'):
    # contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        dbCorporationPin = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {'_id': 1,
                                                                                  'pin': 1,
                                                                                  'userNumber': 1,
                                                                                  'email': 1,
                                                                                  'name': 1,
                                                                                  '_p_corporation': 1,
                                                                                  'cpf': 1,
                                                                                  'isValid': 1,
                                                                                  'unsubscribed': 1,
                                                                                  '_created_at': 1,
                                                                                  '_p_user': 1,
                                                                                  '_updated_at': 1}),
                                             desc="Total itens recebidos:"))

        dbCorporationPin = dbCorporationPin.replace({'_p_user': r'^_User\$'}, {'_p_user': ''}, regex=True)
    else:
        dbCorporationPin = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas),
                                             desc="Total itens recebidos:"))
        dbCorporationPin = remove_pointers(dbCorporationPin)

    print(f'Dataset {mongodb_collection} Criado!')
    return dbCorporationPin


def gerar_tabela_user(filtro=None, colunas=None, mongodb_collection='_User'):
    # contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        dbuser = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {'_id': 1,
                                                                        'name': 1,
                                                                        'cpf': 1,
                                                                        'useremail': 1,
                                                                        'externalId': 1,
                                                                        '_p_corporation': 1,
                                                                        '_p_userPublic': 1,
                                                                        'mainRole': 1,
                                                                        '_created_at': 1,
                                                                        '_updated_at': 1,
                                                                        'isDependent': 1,
                                                                        'family_id': 1,
                                                                        'familyNames': 1,
                                                                        'numeroCartao': 1,
                                                                        'isAdmaUser': 1,
                                                                        'isBlocked': 1,
                                                                        '_p_contractualData': 1,
                                                                        'ContractualId': 1,
                                                                        'termsOfsubscription': 1,
                                                                        'termsOfUse': 1,
                                                                        'privacyPolicy': 1,
                                                                        'termsAccepted': 1,
                                                                        'termsHistory': 1,
                                                                        '_p_establishment': 1,
                                                                        'consentTerm': 1,
                                                                        'isDeleted': 1,
                                                                        'isTestUser': 1,
                                                                        'organizationCNPJ': 1,
                                                                        'organizationDepartment': 1,
                                                                        'organizationDescription': 1,
                                                                        'organizationOperator': 1,
                                                                        'organizationPlan': 1,
                                                                        'organizationRole': 1,
                                                                        'organizationUnity': 1,
                                                                        'organizationCNAE': 1,
                                                                        'customData': 1,
                                                                        'userType': 1,
                                                                        'matriculaVida': 1,
                                                                        'migrationStatus': 1,
                                                                        'matriculaProtheus': 1,
                                                                        'planHolderRelationship': 1,
                                                                        'dateOfBlock': 1,
                                                                        'userNumber': 1,
                                                                        '_p_personalHealthCoach': 1,
                                                                        'cardEmissionDate': 1,
                                                                        'cardExpirationDate': 1,
                                                                        'cardHistory': 1,
                                                                        'isPatientCaptated': 1,
                                                                        'captationDate': 1,
                                                                        'captationInteractionId': 1,
                                                                        'baseOrigem': 1,
                                                                        'serviceAccess': 1,
                                                                        'isStaff': 1}), desc="Total itens recebidos:"))

        dbuser = dbuser.replace({'_p_corporation': r'^Corporation\$'}, {'_p_corporation': ''},
                                regex=True)
        dbuser = dbuser.replace({'_p_userPublic': r'^UserPublic\$'}, {'_p_userPublic': ''}, regex=True)
        dbuser = dbuser.replace({'_p_establishment': r'^EstablishmentData\$'}, {'_p_establishment': ''},
                                regex=True)
    else:
        dbuser = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas), desc="Total itens recebidos:"))
        dbuser = remove_pointers(dbuser)

    print(f'Dataset {mongodb_collection} Criado!')
    return dbuser


def gerar_tabela_user_phone(filtro=None, colunas=None, mongodb_collection='UserPhone'):
    # contar_itens_collection(filtro, mongodb_collection)
    dbUserPhone = pd.DataFrame()
    if colunas is None:
        UserPhone = pd.DataFrame(tqdm(db[mongodb_collection].find({}, {'_id': 1,
                                                                       '_created_at': 1,
                                                                       '_updated_at': 1,
                                                                       '_p_user': 1,
                                                                       'primary': 1,
                                                                       'number': 1}), desc="Total itens recebidos:"))

        print(f'Realizando tratamento do Dataset {mongodb_collection}!')
        UserPhone = UserPhone.replace({'_p_user': r'^_User\$'}, {'_p_user': ''}, regex=True)
        UserPhone.sort_values(['_p_user', '_created_at'], inplace=True)

        UserPhone_true = UserPhone.loc[UserPhone['primary'] == True]
        UserPhone_true.drop_duplicates(['_p_user'], keep='last', inplace=True)
        UserPhone_true.rename(columns={'number': 'phone_number_01'}, inplace=True)

        UserPhone_false = UserPhone.loc[UserPhone['primary'] == False]
        UserPhone_false.drop_duplicates(['_p_user'], keep='last', inplace=True)
        UserPhone_false = UserPhone_false[['_p_user', 'number']]
        UserPhone_false.rename(columns={'number': 'phone_number_02'}, inplace=True)
        if len(UserPhone_false) > 1:
            dbUserPhone = pd.merge(UserPhone_true, UserPhone_false, how="outer", on=['_p_user']).reset_index(drop=True)
        else:
            dbUserPhone = UserPhone_true

        dbUserPhone.drop(columns=['primary'])

    else:
        dbUserPhone = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas), desc="Total itens recebidos:"))
        dbUserPhone = remove_pointers(dbUserPhone)

    print(f'Dataset {mongodb_collection} Criado!')
    return dbUserPhone


def gerar_tabela_user_contract(filtro=None, colunas=None, mongodb_collection='UserContract'):
    # contar_itens_collection(filtro, mongodb_collection)
    dbUserContract = pd.DataFrame()
    if colunas is None:
        dbUserContract = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro), desc="Total itens recebidos:"))
        dbUserContract = dbUserContract.replace({'_p_user': r'^_User\$'}, {'_p_user': ''}, regex=True)
    else:
        dbUserContract = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas), desc="Total itens recebidos:"))
        dbUserContract = remove_pointers(dbUserContract)

    print(f'Dataset {mongodb_collection} Criado!')
    return dbUserContract


def gerar_tabela_user_adress(filtro=None, colunas=None, mongodb_collection='UserAddress'):
    # contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        dbUserAddress = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro), desc="Total itens recebidos:"))
        dbUserAddress = dbUserAddress.replace({'_p_user': r'^_User\$'}, {'_p_user': ''}, regex=True)
    else:
        dbUserAddress = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas), desc="Total itens recebidos:"))
        dbUserAddress = remove_pointers(dbUserAddress)

    print(f'Dataset {mongodb_collection} Criado!')
    return dbUserAddress


def gerar_tabela_user_public(filtro=None, colunas=None, mongodb_collection='UserPublic'):
    # contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        dbUserPublic = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro), desc="Total itens recebidos:"))
    else:
        dbUserPublic = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas), desc="Total itens recebidos:"))
        dbUserPublic = remove_pointers(dbUserPublic)

    print(f'Dataset {mongodb_collection} Criado!')
    return dbUserPublic


def gerar_tabela_user_sicknote(filtro=None, colunas=None, mongodb_collection='UserSickNote'):
    # contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        dbUserSickNote = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {'_id': 1,
                                                                                '_created_at': 1,
                                                                                '_p_CID10': 1,
                                                                                '_p_doctor': 1,
                                                                                '_p_support': 1,
                                                                                '_p_appointmentId': 1,
                                                                                '_p_telephonecallId': 1,
                                                                                '_p_user': 1,
                                                                                'date': 1,
                                                                                'days': 1,
                                                                                'document': 1,
                                                                                'city': 1,
                                                                                'uf': 1,
                                                                                'name': 1,
                                                                                'file': 1,
                                                                                '_updated_at': 1}),
                                           desc="Total itens recebidos:"))

        dbUserSickNote = dbUserSickNote.replace({'_p_user': r'^_User\$'}, {'_p_user': ''}, regex=True)
        dbUserSickNote = dbUserSickNote.replace({'_p_CID10': r'^CID10\$'}, {'_p_CID10': ''}, regex=True)
        dbUserSickNote = dbUserSickNote.replace({'_p_doctor': r'^Staff\$'}, {'_p_doctor': ''}, regex=True)
        dbUserSickNote = dbUserSickNote.replace({'_p_appointmentId': r'^ScheduledAppointments\$'},
                                                {'_p_appointmentId': ''}, regex=True)
        dbUserSickNote = dbUserSickNote.replace({'_p_support': r'^Support\$'}, {'_p_support': ''}, regex=True)
        dbUserSickNote = dbUserSickNote.replace({'_p_appointmentId': r'^ScheduledAppointments\$'},
                                                {'_p_appointmentId': ''}, regex=True)
        dbUserSickNote = dbUserSickNote.replace({'_p_telephonecallId': r'^UserTelephoneCall\$'},
                                                {'_p_telephonecallId': ''}, regex=True)

    else:
        dbUserSickNote = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas), desc="Total itens recebidos:"))
        dbUserSickNote = remove_pointers(dbUserSickNote)

    print(f'Dataset {mongodb_collection} Criado!')
    return dbUserSickNote


def gerar_tabela_user_outside_appointment(filtro=None, colunas=None, mongodb_collection='UserOutsideAppointment'):
    # contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        dbUserOutsideAppointment = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {'_id': 1,
                                                                                          '_created_at': 1,
                                                                                          '_p_createdBy': 1,
                                                                                          '_p_doctorPatient': 1,
                                                                                          '_p_user': 1,
                                                                                          '_updated_at': 1,
                                                                                          'date': 1,
                                                                                          'isCanceled': 1,
                                                                                          'isCompleted': 1,
                                                                                          'entryCollection': 1,
                                                                                          'entryObjectId': 1,
                                                                                          'isDeleted': 1,
                                                                                          'forwardingType': 1,
                                                                                          'speciality': 1,
                                                                                          'specialityLabel': 1,
                                                                                          '_p_scheduledAppointment': 1,
                                                                                          'note': 1,
                                                                                          '_p_support': 1,
                                                                                          '_p_appointmentId': 1,
                                                                                          '_p_telephonecallId': 1}),
                                                     desc="Total itens recebidos:"))

        dbUserOutsideAppointment = dbUserOutsideAppointment.replace({'_p_user': r'^_User\$'},
                                                                    {'_p_user': ''}, regex=True)
        dbUserOutsideAppointment = dbUserOutsideAppointment.replace({'_p_doctorPatient': r'^DoctorPatient\$'},
                                                                    {'_p_doctorPatient': ''}, regex=True)
        dbUserOutsideAppointment = dbUserOutsideAppointment.replace({'_p_createdBy': r'^Staff\$'}, {'_p_createdBy': ''},
                                                                    regex=True)
        dbUserOutsideAppointment = dbUserOutsideAppointment.replace({'_p_scheduledAppointment':
                                                                    r'^ScheduledAppointments\$'},
                                                                    {'_p_scheduledAppointment': ''}, regex=True)
        dbUserOutsideAppointment = dbUserOutsideAppointment.replace({'_p_support': r'^Support\$'}, {'_p_support': ''},
                                                                    regex=True)
        dbUserOutsideAppointment = dbUserOutsideAppointment.replace({'_p_appointmentId': r'^ScheduledAppointments\$'},
                                                                    {'_p_appointmentId': ''}, regex=True)
        dbUserOutsideAppointment = dbUserOutsideAppointment.replace({'_p_telephonecallId': r'^UserTelephoneCall\$'},
                                                                    {'_p_telephonecallId': ''}, regex=True)
    else:
        dbUserOutsideAppointment = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas),
                                                     desc="Total itens recebidos:"))
        dbUserOutsideAppointment = remove_pointers(dbUserOutsideAppointment)

    print(f'Dataset {mongodb_collection} Criado!')
    return dbUserOutsideAppointment


def gerar_tabela_family(filtro=None, colunas=None, mongodb_collection='Family'):
    # contar_itens_collection(filtro, mongodb_collection)
    dbFamily = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas), desc="Total itens recebidos:"))
    dbFamily = remove_pointers(dbFamily)
    print(f'Dataset {mongodb_collection} Criado!')
    return dbFamily


def gerar_tabela_cid10(filtro=None, colunas=None, mongodb_collection='CID10'):
    # contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        dbCID10 = pd.DataFrame(tqdm(db[mongodb_collection].find({}, {'_id': 1,
                                                                     '_created_at': 1,
                                                                     '_updated_at': 1,
                                                                     'code': 1,
                                                                     'description': 1,
                                                                     'is_chronic': 1}), desc="Total itens recebidos:"))
        print(f'Dataset {mongodb_collection} Criado!')
    else:
        dbCID10 = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas), desc="Total itens recebidos:"))
        dbCID10 = remove_pointers(dbCID10)

    print(f'Dataset {mongodb_collection} Criado!')
    return dbCID10


def gerar_tabela_ciap(filtro=None, colunas=None, mongodb_collection='CIAP'):
    # contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        dbCIAP = pd.DataFrame(tqdm(db[mongodb_collection].find({}, {}), desc="Total itens recebidos:"))
    else:
        dbCIAP = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas), desc="Total itens recebidos:"))
        dbCIAP = remove_pointers(dbCIAP)

    print(f'Dataset {mongodb_collection} Criado!')
    return dbCIAP


def gerar_tabela_staff(filtro=None, colunas=None, mongodb_collection='Staff'):
    # contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        dbStaff = pd.DataFrame(tqdm(db[mongodb_collection].find({}, {'_id': 1,
                                                                     '_created_at': 1,
                                                                     '_updated_at': 1,
                                                                     'name': 1,
                                                                     'isBlocked': 1,
                                                                     'isDeleted': 1,
                                                                     'job': 1,
                                                                     'department': 1,
                                                                     'register': 1,
                                                                     'email': 1,
                                                                     '_p_user': 1,
                                                                     'phone': 1,
                                                                     'siglaConselho': 1,
                                                                     'numeroConselho': 1,
                                                                     'siglaEstadoConselho': 1,
                                                                     '_p_corporation': 1,
                                                                     'liveSupport': 1,
                                                                     'signatureImage': 1,
                                                                     'isDigitalCertificate': 1,
                                                                     'cbo': 1}), desc="Total itens recebidos:"))

        dbStaff = dbStaff.replace({'_p_user': r'^_User\$'}, {'_p_user': ''}, regex=True)
        dbStaff = dbStaff.replace({'_p_corporation': r'^Corporation\$'}, {'_p_corporation': ''}, regex=True)
    else:
        dbStaff = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas), desc="Total itens recebidos:"))
        dbStaff = remove_pointers(dbStaff)

    print(f'Dataset {mongodb_collection} Criado!')
    return dbStaff


def gerar_tabela_staff_cbo(filtro=None, colunas=None, mongodb_collection='StaffCBO'):
    # contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        dbStaffCBO = pd.DataFrame(tqdm(db[mongodb_collection].find({}, {'_id': 1,
                                                                        '_created_at': 1,
                                                                        '_updated_at': 1,
                                                                        'code': 1,
                                                                        'category': 1,
                                                                        'title': 1}), desc="Total itens recebidos:"))
    else:
        dbStaffCBO = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas), desc="Total itens recebidos:"))
        dbStaffCBO = remove_pointers(dbStaffCBO)

    print(f'Dataset {mongodb_collection} Criado!')
    return dbStaffCBO


def gerar_tabela_corporation_staff(filtro=None, colunas=None, mongodb_collection='_Join:corporations:Staff'):
    # contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        dbCorporationStaff = pd.DataFrame(tqdm(db[mongodb_collection].find({}, {'_id': 1,
                                                                                'owningId': 1,
                                                                                'relatedId': 1}),
                                               desc="Total itens recebidos:"))

        dbCorporationStaff = remove_pointers(dbCorporationStaff)
    else:
        dbCorporationStaff = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas),
                                                   desc="Total itens recebidos:"))
        dbCorporationStaff = remove_pointers(dbCorporationStaff)

    print(f'Dataset {mongodb_collection} Criado!')
    return dbCorporationStaff


def gerar_tabela_doctor_patient(filtro=None, colunas=None, mongodb_collection='DoctorPatient'):
    # contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        dbDoctorPatient = pd.DataFrame(tqdm(db[mongodb_collection].find({}, {'_id': 1,
                                                                             '_created_at': 1,
                                                                             '_updated_at': 1,
                                                                             '_p_corporation': 1,
                                                                             '_p_doctor': 1,
                                                                             '_p_patient': 1,
                                                                             'healthProfile': 1,
                                                                             'healthProfileHistory': 1,
                                                                             'status': 1}),
                                            desc="Total itens recebidos:"))

        dbDoctorPatient = dbDoctorPatient.replace({'_p_doctor': r'^Staff\$'}, {'_p_doctor': ''}, regex=True)
        dbDoctorPatient = dbDoctorPatient.replace({'_p_patient': r'^_User\$'}, {'_p_patient': ''}, regex=True)
        dbDoctorPatient = dbDoctorPatient.replace({'_p_corporation': r'^Corporation\$'}, {'_p_corporation': ''},
                                                  regex=True)
    else:
        dbDoctorPatient = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas),
                                            desc="Total itens recebidos:"))
        dbDoctorPatient = remove_pointers(dbDoctorPatient)

    print(f'Dataset {mongodb_collection} Criado!')
    return dbDoctorPatient


def gerar_tabela_user_health_complain(filtro=None, colunas=None, mongodb_collection='UserHealthComplain'):
    # contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        dbUserHealthComplain = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {'_id': 1,
                                                                                      '_created_at': 1,
                                                                                      '_updated_at': 1,
                                                                                      '_p_patient': 1,
                                                                                      '_p_doctorPatient': 1,
                                                                                      'date': 1,
                                                                                      'name': 1,
                                                                                      'isDeleted': 1,
                                                                                      '_p_createdBy': 1,
                                                                                      'description': 1,
                                                                                      'code': 1}),
                                                 desc="Total itens recebidos:"))

        dbUserHealthComplain = dbUserHealthComplain.replace({'_p_patient': r'^_User\$'}, {'_p_patient': ''}, regex=True)
        dbUserHealthComplain = dbUserHealthComplain.replace({'_p_doctorPatient': r'^DoctorPatient\$'},
                                                            {'_p_doctorPatient': ''}, regex=True)
        dbUserHealthComplain = dbUserHealthComplain.replace({'_p_createdBy': r'^Staff\$'}, {'_p_createdBy': ''},
                                                            regex=True)
    else:
        dbUserHealthComplain = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas),
                                                 desc="Total itens recebidos:"))
        dbUserHealthComplain = remove_pointers(dbUserHealthComplain)

    print(f'Dataset {mongodb_collection} Criado!')
    return dbUserHealthComplain


def gerar_tabela_user_telephone_call(filtro=None, colunas=None, mongodb_collection='UserTelephoneCall'):
    # contar_itens_collection(filtro, mongodb_collection)
    dbusertelephonecall_schema = create_table_schema(mongodb_collection)
    if colunas is None:
        dbusertelephonecall = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {'_id': 1,
                                                                                     '_created_at': 1,
                                                                                     '_p_corporation': 1,
                                                                                     'date': 1,
                                                                                     '_p_staff': 1,
                                                                                     '_p_responsible': 1,
                                                                                     '_p_scheduledAppointments': 1,
                                                                                     '_p_support': 1,
                                                                                     '_p_user': 1,
                                                                                     '_updated_at': 1,
                                                                                     'additionalComments': 1,
                                                                                     'duplicatedFlag': 1,
                                                                                     'reason': 1,
                                                                                     'title': 1,
                                                                                     'end_time': 1,
                                                                                     'start_time': 1,
                                                                                     'CIDdiagnose': 1,
                                                                                     'CIAPdiagnose': 1,
                                                                                     'contactChannel': 1,
                                                                                     'status': 1,
                                                                                     'serviceReturn': 1,
                                                                                     'complains': 1,
                                                                                     'orientations': 1,
                                                                                     'exams': 1,
                                                                                     'medicines': 1,
                                                                                     'outsideAppointments': 1,
                                                                                     'fup': 1,
                                                                                     'illnessAllergies': 1,
                                                                                     'linkedMedicine': 1,
                                                                                     'linkedSickNote': 1,
                                                                                     'note': 1,
                                                                                     'isCaptationEligible': 1,
                                                                                     'isCaptationAccepted': 1}),
                                                desc="Total itens recebidos:"))
        print(f'Realizando tratamento do Dataset {mongodb_collection}!')
        dbusertelephonecall = dbusertelephonecall.replace({'_p_support': r'^Support\$'}, {'_p_support': ''}, regex=True)
        dbusertelephonecall = dbusertelephonecall.replace({'_p_scheduledAppointments': r'^ScheduledAppointments\$'},
                                                          {'_p_scheduledAppointments': ''}, regex=True)
        dbusertelephonecall = dbusertelephonecall.replace({'_p_staff': r'^Staff\$'}, {'_p_staff': ''}, regex=True)
        dbusertelephonecall = dbusertelephonecall.replace({'_p_responsible': r'^Staff\$'}, {'_p_responsible': ''},
                                                          regex=True)
        dbusertelephonecall = dbusertelephonecall.replace({'_p_user': r'^_User\$'}, {'_p_user': ''}, regex=True)
        dbusertelephonecall = dbusertelephonecall.replace({'_p_corporation': r'^Corporation\$'},
                                                                  {'_p_corporation': ''}, regex=True)
        dbusertelephonecall = pd.concat([dbusertelephonecall, dbusertelephonecall_schema])
    else:
        dbusertelephonecall = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas),
                                                desc="Total itens recebidos:"))
        dbusertelephonecall = remove_pointers(dbusertelephonecall)

    print(f'Dataset {mongodb_collection} Criado!')
    return dbusertelephonecall


def gerar_tabela_scheduled_appointments(filtro=None, colunas=None, mongodb_collection='ScheduledAppointments'):
    # contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        dbScheduledAppointments = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {'_id': 1,
                                                                                         'UTCdatetime': 1,
                                                                                         '_created_at': 1,
                                                                                         '_p_activeStaff': 1,
                                                                                         '_p_corporation': 1,
                                                                                         '_p_patient': 1,
                                                                                         '_updated_at': 1,
                                                                                         'appointmentDate': 1,
                                                                                         'appointmentEndTime': 1,
                                                                                         'appointmentStartTime': 1,
                                                                                         'cancelledAppointmentDate': 1,
                                                                                         '_p_deletedBy': 1,
                                                                                         'isTransfer': 1,
                                                                                         'job': 1,
                                                                                         'staffSpeciality': 1,
                                                                                         '_p_createdBy': 1,
                                                                                         'status': 1,
                                                                                         'type': 1,
                                                                                         'waitingTime': 1,
                                                                                         'complains': 1,
                                                                                         'exams': 1,
                                                                                         'note': 1,
                                                                                         'orientations': 1,
                                                                                         'videoEctoscopicExams': 1,
                                                                                         'outsideAppointments': 1,
                                                                                         'medicines': 1,
                                                                                         'appointmentOrigin': 1}),
                                                    desc="Total itens recebidos:"))
        print(f'Realizando tratamento do Dataset {mongodb_collection}!')
        dbScheduledAppointments = dbScheduledAppointments.replace({'_p_activeStaff': r'^ScheduledStaff\$'},
                                                                  {'_p_activeStaff': ''}, regex=True)
        dbScheduledAppointments = dbScheduledAppointments.replace({'_p_patient': r'^_User\$'}, {'_p_patient': ''},
                                                                  regex=True)
        dbScheduledAppointments = dbScheduledAppointments.replace({'_p_createdBy': r'^_User\$'}, {'_p_createdBy': ''},
                                                                  regex=True)
        dbScheduledAppointments = dbScheduledAppointments.replace({'_p_deletedBy': r'^_User\$'}, {'_p_deletedBy': ''},
                                                                  regex=True)
        dbScheduledAppointments = dbScheduledAppointments.replace({'_p_corporation': r'^Corporation\$'},
                                                                  {'_p_corporation': ''}, regex=True)
    else:
        dbScheduledAppointments = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas),
                                                    desc="Total itens recebidos:"))
        dbScheduledAppointments = remove_pointers(dbScheduledAppointments)

    print(f'Dataset {mongodb_collection} Criado!')
    return dbScheduledAppointments


def gerar_tabela_scheduling_report(filtro=None, colunas=None, mongodb_collection='SchedulingReport'):
    # contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        dbSchedulingReport = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {'_id': 1,
                                                                                    'PatientEmail': 1,
                                                                                    'PatientPhone': 1,
                                                                                    '_created_at': 1,
                                                                                    '_p_corporation': 1,
                                                                                    '_p_patient': 1,
                                                                                    '_p_scheduleAppointment': 1,
                                                                                    '_p_staff': 1,
                                                                                    '_updated_at': 1,
                                                                                    'appointmentDate': 1,
                                                                                    'duration': 1,
                                                                                    'patientName': 1,
                                                                                    'staffSpeciality': 1,
                                                                                    'staffState': 1,
                                                                                    'status': 1,
                                                                                    'totalCompletedCalls': 1,
                                                                                    '_p_scheduleCallLogs': 1,
                                                                                    'endTime': 1,
                                                                                    'startTime': 1,
                                                                                    'doctor_review': 1,
                                                                                    'patient_review': 1,
                                                                                    'patient_rating': 1,
                                                                                    'additionalNotes': 1}),
                                               desc="Total itens recebidos:"))
        print(f'Realizando tratamento do Dataset {mongodb_collection}!')
        dbSchedulingReport = dbSchedulingReport.replace({'_p_activeStaff': r'^ScheduledStaff\$'},
                                                        {'_p_activeStaff': ''}, regex=True)
        dbSchedulingReport = dbSchedulingReport.replace({'_p_patient': r'^_User\$'}, {'_p_patient': ''},
                                                        regex=True)
        dbSchedulingReport = dbSchedulingReport.replace({'_p_corporation': r'^Corporation\$'},
                                                        {'_p_corporation': ''}, regex=True)
        dbSchedulingReport = dbSchedulingReport.replace({'_p_scheduledAppointment': r'^ScheduledAppointments\$'},
                                                        {'_p_scheduledAppointment': ''}, regex=True)
        dbSchedulingReport = dbSchedulingReport.replace({'_p_scheduleAppointment': r'^ScheduledAppointments\$'},
                                                        {'_p_scheduleAppointment': ''}, regex=True)
        dbSchedulingReport = dbSchedulingReport.replace({'_p_staff': r'^ScheduledStaff\$'}, {'_p_staff': ''},
                                                        regex=True)
    else:
        dbSchedulingReport = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas),
                                               desc="Total itens recebidos:"))
        dbSchedulingReport = remove_pointers(dbSchedulingReport)

    print(f'Dataset {mongodb_collection} Criado!')
    return dbSchedulingReport


def gerar_tabela_user_health_analyze(filtro=None, colunas=None, mongodb_collection='UserHealthAnalyze'):
    # contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        dbUserHealthAnalyze = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {'id': 1,
                                                                                     '_created_at': 1,
                                                                                     '_p_corporation': 1,
                                                                                     '_p_doctorPatient': 1,
                                                                                     '_p_staff': 1,
                                                                                     '_p_user': 1,
                                                                                     '_updated_at': 1,
                                                                                     'cidCode': 1,
                                                                                     'cidDescription': 1,
                                                                                     'date': 1,
                                                                                     'groupName': 1,
                                                                                     'isAnalysed': 1,
                                                                                     'isDeleted': 1,
                                                                                     'isPending': 1,
                                                                                     'observation': 1,
                                                                                     'orientation': 1,
                                                                                     'staffName': 1,
                                                                                     'tag': 1,
                                                                                     'title': 1,
                                                                                     'tussCode': 1,
                                                                                     'tussCodeDescription': 1,
                                                                                     'type': 1,
                                                                                     '_p_supportId': 1,
                                                                                     '_p_clinicalExam': 1,
                                                                                     '_p_support': 1,
                                                                                     '_p_appointmentId': 1,
                                                                                     '_p_telephonecallId': 1}),
                                                desc="Total itens recebidos:"))
        print(f'Realizando tratamento do Dataset {mongodb_collection}!')
        dbUserHealthAnalyze = dbUserHealthAnalyze.replace({'_p_corporation': r'^Corporation\$'}, {'_p_corporation': ''},
                                                          regex=True)
        dbUserHealthAnalyze = dbUserHealthAnalyze.replace({'_p_doctorPatient': r'^DoctorPatient\$'},
                                                          {'_p_doctorPatient': ''}, regex=True)
        dbUserHealthAnalyze = dbUserHealthAnalyze.replace({'_p_staff': r'^Staff\$'}, {'_p_staff': ''}, regex=True)
        dbUserHealthAnalyze = dbUserHealthAnalyze.replace({'_p_user': r'^_User\$'}, {'_p_user': ''}, regex=True)
        dbUserHealthAnalyze = dbUserHealthAnalyze.replace({'_p_clinicalExam': r'^CatalogClinicalExam\$'},
                                                          {'_p_clinicalExam': ''},regex=True)
        dbUserHealthAnalyze = dbUserHealthAnalyze.replace({'_p_supportId': r'^Support\$'}, {'_p_supportId': ''},
                                                          regex=True)
        dbUserHealthAnalyze = dbUserHealthAnalyze.replace({'_p_appointmentId': r'^ScheduledAppointments\$'},
                                                          {'_p_appointmentId': ''}, regex=True)
        dbUserHealthAnalyze = dbUserHealthAnalyze.replace({'_p_support': r'^Support\$'}, {'_p_support': ''},
                                                          regex=True)
        dbUserHealthAnalyze = dbUserHealthAnalyze.replace({'_p_appointmentId': r'^ScheduledAppointments\$'},
                                                          {'_p_appointmentId': ''}, regex=True)
        dbUserHealthAnalyze = dbUserHealthAnalyze.replace({'_p_telephonecallId': r'^UserTelephoneCall\$'},
                                                          {'_p_telephonecallId': ''}, regex=True)

    else:
        dbUserHealthAnalyze = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas),
                                                desc="Total itens recebidos:"))
        dbUserHealthAnalyze = remove_pointers(dbUserHealthAnalyze)

    print(f'Dataset {mongodb_collection} Criado!')
    return dbUserHealthAnalyze


def gerar_tabela_user_health_medicine(filtro=None, colunas=None, mongodb_collection='UserHealthMedicine'):
    # contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        dbUserHealthMedicine = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {'_id': 1,
                                                                                      '_created_at': 1,
                                                                                      '_p_corporation': 1,
                                                                                      '_p_user': 1,
                                                                                      'category': 1,
                                                                                      'code': 1,
                                                                                      'name': 1,
                                                                                      'type': 1,
                                                                                      'dosage': 1,
                                                                                      'dosageMeasure': 1,
                                                                                      'frequency': 1,
                                                                                      'frequencyTime': 1,
                                                                                      'orientation': 1,
                                                                                      '_updated_at': 1,
                                                                                      '_p_doctor': 1,
                                                                                      'dosageInformation': 1,
                                                                                      '_p_supportId': 1,
                                                                                      'cidCode': 1,
                                                                                      'cidDescription': 1,
                                                                                      'isContinuous': 1,
                                                                                      'isControlled': 1,
                                                                                      'via': 1,
                                                                                      '_p_support': 1,
                                                                                      '_p_appointmentId': 1,
                                                                                      '_p_telephonecallId': 1}),

                                                 desc="Total itens recebidos:"))
        print(f'Realizando tratamento do Dataset {mongodb_collection}!')
        dbUserHealthMedicine = dbUserHealthMedicine.replace({'_p_corporation': r'^Corporation\$'},
                                                            {'_p_corporation': ''}, regex=True)
        dbUserHealthMedicine = dbUserHealthMedicine.replace({'_p_user': r'^_User\$'}, {'_p_user': ''}, regex=True)
        dbUserHealthMedicine = dbUserHealthMedicine.replace({'_p_doctor': r'^Staff\$'}, {'_p_doctor': ''},regex=True)
        dbUserHealthMedicine = dbUserHealthMedicine.replace({'_p_supportId': r'^Support\$'}, {'_p_supportId': ''},
                                                            regex=True)
        dbUserHealthMedicine = dbUserHealthMedicine.replace({'_p_support': r'^Support\$'}, {'_p_support': ''},
                                                            regex=True)
        dbUserHealthMedicine = dbUserHealthMedicine.replace({'_p_appointmentId': r'^ScheduledAppointments\$'},
                                                            {'_p_appointmentId': ''}, regex=True)
        dbUserHealthMedicine = dbUserHealthMedicine.replace({'_p_telephonecallId': r'^UserTelephoneCall\$'},
                                                            {'_p_telephonecallId': ''}, regex=True)

    else:
        dbUserHealthMedicine = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas),
                                                 desc="Total itens recebidos:"))
        dbUserHealthMedicine = remove_pointers(dbUserHealthMedicine)

    print(f'Dataset {mongodb_collection} Criado!')
    return dbUserHealthMedicine


def gerar_tabela_user_illness_allergy(filtro=None, colunas=None, mongodb_collection='UserIllnessAllergy'):
    # contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        UserIllnessAllergy = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {}), desc="Total itens recebidos:"))
        print(f'Realizando tratamento do Dataset {mongodb_collection}!')
        UserIllnessAllergy = UserIllnessAllergy.replace({'_p_corporation': r'^Corporation\$'},
                                                            {'_p_corporation': ''}, regex=True)
        UserIllnessAllergy = UserIllnessAllergy.replace({'_p_user': r'^_User\$'}, {'_p_user': ''},regex=True)
        UserIllnessAllergy = UserIllnessAllergy.replace({'_p_createdBy': r'^Staff\$'}, {'_p_createdBy': ''},regex=True)
        UserIllnessAllergy = UserIllnessAllergy.replace({'_p_supportId': r'^Support\$'}, {'_p_supportId': ''},
                                                            regex=True)
        UserIllnessAllergy = UserIllnessAllergy.replace({'_p_appointmentId': r'^ScheduledAppointments\$'},
                                                            {'_p_appointmentId': ''}, regex=True)
        UserIllnessAllergy = UserIllnessAllergy.replace({'_p_catalogIllnessAllergy': r'^CatalogIllnessAllergy\$'},
                                                        {'_p_catalogIllnessAllergy': ''}, regex=True)
    else:
        UserIllnessAllergy = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas),
                                               desc="Total itens recebidos:"))
        UserIllnessAllergy = remove_pointers(UserIllnessAllergy)

    print(f'Dataset {mongodb_collection} Criado!')
    return UserIllnessAllergy


def gerar_tabela_user_indicator(filtro=None, colunas=None, mongodb_collection='UserIndicator'):
    # contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        dbUserIndicator = pd.DataFrame(tqdm(db['UserIndicator'].find(filtro, {'_id': 1,
                                                                              '_created_at': 1,
                                                                              'date': 1,
                                                                              '_p_createdBy': 1,
                                                                              '_p_doctorPatient': 1,
                                                                              '_p_user': 1,
                                                                              '_updated_at': 1,
                                                                              'examDate': 1,
                                                                              'indicators': 1,
                                                                              'isDeleted': 1,
                                                                              'interactionId': 1,
                                                                              '_p_userAnamnesis': 1,
                                                                              'type': 1,
                                                                              '_p_appointmentId': 1,
                                                                              '_p_supportId': 1}),
                                            desc="Total itens recebidos:"))

        print(f'Realizando tratamento do Dataset {mongodb_collection}!')

        dbUserIndicator.rename(columns={'date': 'indicator_date', 'type': 'indicator_type'}, inplace=True)
        dbUserIndicator = dbUserIndicator.explode('indicators').reset_index(drop=True)
        dbUserIndicator = pd.concat([dbUserIndicator.drop(['indicators'], axis=1),
                                     pd.json_normalize(dbUserIndicator['indicators'])], axis=1)
        dbUserIndicator['name'] = dbUserIndicator['name'].str.strip()
        dbUserIndicator['measurement'] = dbUserIndicator['measurement'].str.strip()

        dbUserIndicator.drop(columns=['meameasurement',
                                      'measure',
                                      'type',
                                      'date.__type',
                                      'date.iso',
                                      'values'], inplace=True)
        dbUserIndicator = remove_pointers(dbUserIndicator)

    else:
        print('Ainda não é possivel escolher colunas desejadas')
        dbUserIndicator = pd.DataFrame(tqdm(db['UserIndicator'].find(filtro, colunas)))
        dbUserIndicator.rename(columns={'date': 'indicator_date', 'type': 'indicator_type'}, inplace=True)

    print(f'Dataset {mongodb_collection} Criado!')
    return dbUserIndicator


def gerar_tabela_user_anamnesis(filtro=None, colunas=None, mongodb_collection='UserAnamnesis'):
    # contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        dbUserAnamnesis = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {'_id': 1,
                                                                                 '_created_at': 1,
                                                                                 '_p_user': 1,
                                                                                 '_updated_at': 1,
                                                                                 "answers": 1,
                                                                                 'care_plan_file': 1,
                                                                                 'anamnesisCorporation': 1,
                                                                                 "sequence": 1,
                                                                                 'date_finished': 1,
                                                                                 'date_start': 1,
                                                                                 "is_deleted": 1,
                                                                                 'is_finished': 1,
                                                                                 'healthProfile': 1,
                                                                                 '_p_created_by': 1,
                                                                                 'group': 1}),
                                            desc="Total itens recebidos:"))

        print(f'Realizando tratamento do Dataset {mongodb_collection}!')
        dbUserAnamnesis = dbUserAnamnesis.replace({'_p_user': r'^_User\$'}, {'_p_user': ''}, regex=True)
        dbUserAnamnesis = dbUserAnamnesis.replace({'_p_created_by': r'^Staff\$'}, {'_p_created_by': ''}, regex=True)
    else:
        dbUserAnamnesis = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas),
                                            desc="Total itens recebidos:"))
        dbUserAnamnesis = remove_pointers(dbUserAnamnesis)

    print(f'Dataset {mongodb_collection} Criado!')
    return dbUserAnamnesis


def gerar_tabela_scheduled_staff(filtro=None, colunas=None, mongodb_collection='ScheduledStaff'):
    # contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        dbScheduledStaff = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {'_id': 1,
                                                                                  '_created_at': 1,
                                                                                  '_updated_at': 1,
                                                                                  '_p_user': 1,
                                                                                  '_p_staff': 1,
                                                                                  'corporation': 1,
                                                                                  'is_deleted': 1,
                                                                                  'isScheduling': 1,
                                                                                  'isBlocked': 1,
                                                                                  'speciality': 1,
                                                                                  'job': 1}),
                                             desc="Total itens recebidos:"))

        print(f'Realizando tratamento do Dataset {mongodb_collection}!')
        dbScheduledStaff = dbScheduledStaff.replace({'_p_user': r'^_User\$'}, {'_p_user': ''}, regex=True)
        dbScheduledStaff = dbScheduledStaff.replace({'_p_staff': r'^Staff\$'},{'_p_staff': ''},regex=True)
        dbScheduledStaff = dbScheduledStaff.replace({'_p_corporation': r'^Corporation\$'}, {'_p_corporation': ''},
                                                    regex=True)
    else:
        dbScheduledStaff = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas),
                                             desc="Total itens recebidos:"))
        dbScheduledStaff = remove_pointers(dbScheduledStaff)

    print(f'Dataset {mongodb_collection} Criado!')
    return dbScheduledStaff


def gerar_tabela_specialities(filtro=None, colunas=None, mongodb_collection='Specialities'):
    # contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        dbspecialities = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {'_id': 1,
                                                                                '_created_at': 1,
                                                                                '_updated_at': 1,
                                                                                'accessRoles': 1,
                                                                                'corporations': 1,
                                                                                'interval': 1,
                                                                                'name': 1,
                                                                                'cbo': 1,
                                                                                'journeyLabel': 1,
                                                                                'soapType': 1,
                                                                                'journeyCode': 1}),
                                           desc="Total itens recebidos:"))
    else:
        dbspecialities = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas), desc="Total itens recebidos:"))
    print(f'Dataset {mongodb_collection} Criado!')
    return dbspecialities


def gerar_tabela_uo(filtro=None, colunas=None, mongodb_collection='UO'):
    # contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        db_uo = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {'_id': 1,
                                                                       '_created_at': 1,
                                                                       '_p_corporation': 1,
                                                                       '_p_department': 1,
                                                                       '_p_regional': 1,
                                                                       '_updated_at': 1,
                                                                       'address': 1,
                                                                       'cep': 1,
                                                                       'city': 1,
                                                                       'cnpj': 1,
                                                                       'deletedAt': 1,
                                                                       'email': 1,
                                                                       'isDeleted': 1,
                                                                       'neighborhood': 1,
                                                                       'obaCode': 1,
                                                                       'operatingUnit': 1,
                                                                       'smdCode': 1,
                                                                       'uf': 1,
                                                                       'addressCode': 1,
                                                                       '_p_updatedBy': 1,
                                                                       '_p_createdBy': 1}),
                                              desc="Total itens recebidos:"))

        print(f'Realizando tratamento do Dataset {mongodb_collection}!')
        db_uo = db_uo.replace({'_p_corporation': r'^Corporation\$'}, {'_p_corporation': ''}, regex=True)
        db_uo = db_uo.replace({'_p_department': r'^Regionals\$'}, {'_p_department': ''}, regex=True)
        db_uo = db_uo.replace({'_p_regional': r'^Regionals\$'}, {'_p_regional': ''}, regex=True)
        db_uo = db_uo.replace({'_p_updatedBy': r'^_User\$'}, {'_p_updatedBy': ''}, regex=True)
        db_uo = db_uo.replace({'_p_createdBy': r'^User\$'}, {'_p_createdBy': ''}, regex=True)
    else:
        db_uo = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas), desc="Total itens recebidos:"))
        db_uo = remove_pointers(db_uo)

    print(f'Dataset {mongodb_collection} Criado!')
    return db_uo


def gerar_tabela_regionals(filtro=None, colunas=None, mongodb_collection='Regionals'):
    # contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        db_regionals = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {'_id': 1,
                                                                              '_created_at': 1,
                                                                              '_p_corporation': 1,
                                                                              '_updated_at': 1,
                                                                              'address': 1,
                                                                              'addressCode': 1,
                                                                              'cep': 1,
                                                                              'city': 1,
                                                                              'cnpj': 1,
                                                                              'contractEndDate': 1,
                                                                              'department': 1,
                                                                              'drCode': 1,
                                                                              'email': 1,
                                                                              'isDeleted': 1,
                                                                              'neighborhood': 1,
                                                                              'number': 1,
                                                                              'uf': 1,
                                                                              'deletedAt': 1,
                                                                              '_p_updatedBy': 1,
                                                                              '_p_createdBy': 1}),
                                         desc="Total itens recebidos:"))

        print(f'Realizando tratamento do Dataset {mongodb_collection}!')
        db_regionals = db_regionals.replace({'_p_corporation': r'^Corporation\$'}, {'_p_corporation': ''}, regex=True)
        db_regionals = db_regionals.replace({'_p_updatedBy': r'^_User\$'}, {'_p_updatedBy': ''}, regex=True)
        db_regionals = db_regionals.replace({'_p_createdBy': r'^User\$'}, {'_p_createdBy': ''}, regex=True)
    else:
        db_regionals = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas), desc="Total itens recebidos:"))
        db_regionals = remove_pointers(db_regionals)

    print(f'Dataset {mongodb_collection} Criado!')
    return db_regionals


def gerar_tabela_establishment_data(filtro=None, colunas=None, mongodb_collection='EstablishmentData'):
    # contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        db_establishment = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {'_id': 1,
                                                                                  '_created_at': 1,
                                                                                  '_p_companies': 1,
                                                                                  '_p_corporation': 1,
                                                                                  '_p_regional': 1,
                                                                                  '_p_uo': 1,
                                                                                  '_updated_at': 1,
                                                                                  'address': 1,
                                                                                  'addressCode': 1,
                                                                                  'cep': 1,
                                                                                  'city': 1,
                                                                                  'cnae': 1,
                                                                                  'cnpj': 1,
                                                                                  'company': 1,
                                                                                  'contractEndDate': 1,
                                                                                  'email': 1,
                                                                                  'fantasyName': 1,
                                                                                  'focalContact': 1,
                                                                                  'isDeleted': 1,
                                                                                  'neighborhood': 1,
                                                                                  'number': 1,
                                                                                  'uf': 1,
                                                                                  'deletedAt': 1,
                                                                                  '_p_updatedBy': 1,
                                                                                  '_p_createdBy': 1}),
                                             desc="Total itens recebidos:"))

        print(f'Realizando tratamento do Dataset {mongodb_collection}!')
        db_establishment = db_establishment.replace({'_p_corporation': r'^Corporation\$'}, {'_p_corporation': ''},
                                                  regex=True)
        db_establishment = db_establishment.replace({'_p_updatedBy': r'^_User\$'}, {'_p_updatedBy': ''}, regex=True)
        db_establishment = db_establishment.replace({'_p_createdBy': r'^User\$'}, {'_p_createdBy': ''}, regex=True)
        db_establishment = db_establishment.replace({'_p_companies': r'^CompanyData\$'}, {'_p_companies': ''},
                                                    regex=True)
        db_establishment = db_establishment.replace({'_p_regional': r'^Regionals\$'}, {'_p_regional': ''}, regex=True)
        db_establishment = db_establishment.replace({'_p_uo': r'^UO\$'}, {'_p_uo': ''}, regex=True)
        print(f'Dataset {mongodb_collection} Criado!')
    else:
        db_establishment = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas),
                                             desc="Total itens recebidos:"))
        db_establishment = remove_pointers(db_establishment)

    print(f'Dataset {mongodb_collection} Criado!')
    return db_establishment


def gerar_tabela_company_data(filtro=None, colunas=None, mongodb_collection='CompanyData'):
    # contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        db_company = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {'_id': 1,
                                                                            '_created_at': 1,
                                                                            '_p_corporation': 1,
                                                                            '_p_department': 1,
                                                                            '_p_regional': 1,
                                                                            '_p_uo': 1,
                                                                            '_updated_at': 1,
                                                                            'address': 1,
                                                                            'addressCode': 1,
                                                                            'cep': 1,
                                                                            'city': 1,
                                                                            'cnae': 1,
                                                                            'cnpj': 1,
                                                                            'company': 1,
                                                                            'fantasyName': 1,
                                                                            'isDeleted': 1,
                                                                            'neighborhood': 1,
                                                                            'operatingUnit': 1,
                                                                            'uf': 1,
                                                                            'deletedAt': 1,
                                                                            'number': 1,
                                                                            '_p_updatedBy': 1,
                                                                            'department': 1,
                                                                            'email': 1,
                                                                            '_p_createdBy': 1}),
                                       desc="Total itens recebidos:"))

        print(f'Realizando tratamento do Dataset {mongodb_collection}!')
        db_company = db_company.replace({'_p_corporation': r'^Corporation\$'}, {'_p_corporation': ''}, regex=True)
        db_company = db_company.replace({'_p_updatedBy': r'^_User\$'}, {'_p_updatedBy': ''}, regex=True)
        db_company = db_company.replace({'_p_createdBy': r'^User\$'}, {'_p_createdBy': ''}, regex=True)
        db_company = db_company.replace({'_p_regional': r'^Regionals\$'}, {'_p_regional': ''}, regex=True)
        db_company = db_company.replace({'_p_department': r'^Regionals\$'},{'_p_department': ''}, regex=True)
        db_company = db_company.replace({'_p_uo': r'^UO\$'}, {'_p_uo': ''}, regex=True)
    else:
        db_company = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas), desc="Total itens recebidos:"))
        db_company = remove_pointers(db_company)

    print(f'Dataset {mongodb_collection} Criado!')
    return db_company


def gerar_tabela_nps_petrobras(filtro=None, colunas=None, mongodb_collection='NPSPetrobras'):
    # contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        db_nps_petrobras = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {'_id': 1,
                                                                                  '_created_at': 1,
                                                                                  '_p_user': 1,
                                                                                  '_updated_at': 1,
                                                                                  'doctorTeamId': 1,
                                                                                  'rating': 1,
                                                                                  'reason': 1,
                                                                                  'notes': 1}),
                                             desc="Total itens recebidos:"))
        db_nps_petrobras = remove_pointers(db_nps_petrobras)
    else:
        db_nps_petrobras = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas),
                                                 desc="Total itens recebidos:"))
        db_nps_petrobras = remove_pointers(db_nps_petrobras)

    print(f'Dataset {mongodb_collection} Criado!')
    return db_nps_petrobras


def gerar_tabela_doctor_team(filtro=None, colunas=None, mongodb_collection='DoctorTeam'):
    # contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        db_doctor_team = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {'_id': 1,
                                                                                '_created_at': 1,
                                                                                '_updated_at': 1,
                                                                                'doctors': 1,
                                                                                'name': 1}),
                                           desc="Total itens recebidos:"))
        db_doctor_team = remove_pointers(db_doctor_team)
    else:
        db_doctor_team = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas), desc="Total itens recebidos:"))
        db_doctor_team = remove_pointers(db_doctor_team)

    print(f'Dataset {mongodb_collection} Criado!')
    return db_doctor_team


def gerar_tabela_admission_history(filtro=None, colunas=None, mongodb_collection='AdmissionHistory'):
    # contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        admission_history = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {'_id': 1,
                                                                                   '_created_at': 1,
                                                                                   '_p_corporation': 1,
                                                                                   '_p_user': 1,
                                                                                   '_updated_at': 1,
                                                                                   'programType': 1,
                                                                                   'startDate': 1,
                                                                                   'endDate': 1,
                                                                                   'reason': 1}),
                                              desc="Total itens recebidos:"))
        admission_history = remove_pointers(admission_history)
    else:
        admission_history = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas),
                                                 desc="Total itens recebidos:"))
        admission_history = remove_pointers(admission_history)

    print(f'Dataset {mongodb_collection} Criado!')
    return admission_history


def gerar_tabela_user_cookies(filtro=None, colunas=None, mongodb_collection='userCookie'):
    # contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        user_cookie = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {'_id': 1,
                                                                             '_created_at': 1,
                                                                             '_updated_at': 1,
                                                                             'correction_id': 1,
                                                                             'performanceCookie': 1,
                                                                             'slug': 1,
                                                                             'strictlyNecessaryCookie': 1,
                                                                             'thirdPartyCookie': 1,
                                                                             '_p_user': 1,
                                                                             'userId': 1}),
                                        desc="Total itens recebidos:"))
        user_cookie = remove_pointers(user_cookie)
    else:
        user_cookie = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas), desc="Total itens recebidos:"))
        user_cookie = remove_pointers(user_cookie)

    print(f'Dataset {mongodb_collection} Criado!')
    return user_cookie


def gerar_tabela_contractual_data(filtro=None, colunas=None, mongodb_collection='ContractualData'):
    # contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        contractual_data = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {'_id': 1,
                                                                                  '_created_at': 1,
                                                                                  '_updated_at': 1,
                                                                                  '_p_companyId': 1,
                                                                                  '_p_establishmentId': 1,
                                                                                  '_p_regionalId': 1,
                                                                                  '_p_updatedBy': 1,
                                                                                  'isDeleted': 1,
                                                                                  'products': 1}),
                                        desc="Total itens recebidos:"))
        contractual_data = remove_pointers(contractual_data)
    else:
        contractual_data = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas),
                                             desc="Total itens recebidos:"))
        contractual_data = remove_pointers(contractual_data)

    print(f'Dataset {mongodb_collection} Criado!')
    return contractual_data


def gerar_tabela_user_desfecho(filtro=None, colunas=None, mongodb_collection='UserDesfecho'):
    # contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        user_desfecho = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {'_id': 1,
                                                                               '_created_at': 1,
                                                                               '_updated_at': 1,
                                                                               '_p_createdBy': 1,
                                                                               '_p_doctorPatient': 1,
                                                                               '_p_patient': 1,
                                                                               'acompanhamento': 1,
                                                                               'acompanhamentoType': 1,
                                                                               'apsType': 1,
                                                                               'apsValue': 1,
                                                                               'comment': 1,
                                                                               'encaminhamento': 1,
                                                                               'encaminhamentoType': 1,
                                                                               'focal_speciality_type': 1,
                                                                               'isEmergency': 1,
                                                                               'entryCollection': 1,
                                                                               'entryObjectId': 1,
                                                                               '_p_scheduledAppointment': 1,
                                                                               'isCompleted': 1,
                                                                               'returnType': 1,
                                                                               'isDeleted': 1}),
                                        desc="Total itens recebidos:"))
        user_desfecho = remove_pointers(user_desfecho)
    else:
        user_desfecho = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas), desc="Total itens recebidos:"))
        user_desfecho = remove_pointers(user_desfecho)

    print(f'Dataset {mongodb_collection} Criado!')
    return user_desfecho


def gerar_tabela_staff_agenda(filtro=None, colunas=None, mongodb_collection='StaffAgenda'):
    # contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        staff_agenda = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {'_id': 1,
                                                                              '_created_at': 1,
                                                                              '_p_createdBy': 1,
                                                                              '_p_deletedBy': 1,
                                                                              '_p_staff': 1,
                                                                              '_updated_at': 1,
                                                                              'blockHistory': 1,
                                                                              'date': 1,
                                                                              'end_time': 1,
                                                                              'isBlocked': 1,
                                                                              'isDeleted': 1,
                                                                              'scheduledAppointmentHistory': 1,
                                                                              'seriesNumber': 1,
                                                                              'slotDuration': 1,
                                                                              'slotIndex': 1,
                                                                              'speciality': 1,
                                                                              'blockedBy': 1,
                                                                              'dateOfBlock': 1,
                                                                              '_p_scheduledAppointment': 1,
                                                                              'meetingSeries': 1,
                                                                              'time': 1,
                                                                              'type': 1}),
                                         desc="Total itens recebidos:"))
        staff_agenda = remove_pointers(staff_agenda)
    else:
        staff_agenda = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas), desc="Total itens recebidos:"))
        staff_agenda = remove_pointers(staff_agenda)

    print(f'Dataset {mongodb_collection} Criado!')
    return staff_agenda


def gerar_tabela_referral_data(filtro=None, colunas=None, mongodb_collection='ReferralData'):
    # contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        referral_data = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {'_id': 1,
                                                                               '_created_at': 1,
                                                                               '_updated_at': 1,
                                                                               'additionalInformation': 1,
                                                                               'isCanceled': 1,
                                                                               'isCheckExpertLater': 1,
                                                                               'isCompleted': 1,
                                                                               'isDeleted': 1,
                                                                               'outsideAppointment': 1,
                                                                               'outsideAppointmentDate': 1,
                                                                               'outsideStaffName': 1,
                                                                               'referralStatus': 1,
                                                                               'referralType': 1,
                                                                               'counterReferralNotes': 1,
                                                                               'resultFile': 1,
                                                                               'slug': 1,
                                                                               'speciality': 1,
                                                                               'staff': 1,
                                                                               'user': 1,
                                                                               'appointmentId': 1,
                                                                               'scheduledAppointment': 1,
                                                                               'supportId': 1,
                                                                               'interactionId': 1,
                                                                               'clinicDetails': 1}),
                                          desc="Total itens recebidos:"))
        referral_data = remove_pointers(referral_data)
    else:
        referral_data = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas), desc="Total itens recebidos:"))
        referral_data = remove_pointers(referral_data)

    print(f'Dataset {mongodb_collection} Criado!')
    return referral_data


def gerar_tabela_women_health(filtro=None, colunas=None, mongodb_collection='WomenHealth'):
    # contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        women_health = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {}),
                                         desc="Total itens recebidos:"))
        women_health = remove_pointers(women_health)
    else:
        women_health = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas),
                                         desc="Total itens recebidos:"))
        women_health = remove_pointers(women_health)

    print(f'Dataset {mongodb_collection} Criado!')
    return women_health


def gerar_tabela_diabetes_health(filtro=None, colunas=None, mongodb_collection='DiabetesHealth'):
    # contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        diabetes_health = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {}),
                                            desc="Total itens recebidos:"))
        diabetes_health = remove_pointers(diabetes_health)
    else:
        diabetes_health = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas),
                                            desc="Total itens recebidos:"))
        diabetes_health = remove_pointers(diabetes_health)

    print(f'Dataset {mongodb_collection} Criado!')
    return diabetes_health


def gerar_tabela_hypertension_health(filtro=None, colunas=None, mongodb_collection='HypertensionHealth'):
    # contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        hypertension_health = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {}),
                                                desc="Total itens recebidos:"))
        hypertension_health = remove_pointers(hypertension_health)
    else:
        hypertension_health = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas),
                                                desc="Total itens recebidos:"))
        hypertension_health = remove_pointers(hypertension_health)

    print(f'Dataset {mongodb_collection} Criado!')
    return hypertension_health


def gerar_tabela_osteomioarticular_health(filtro=None, colunas=None, mongodb_collection='OsteomioarticularHealth'):
    # contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        osteomioarticular_health = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {}),
                                                     desc="Total itens recebidos:"))
        osteomioarticular_health = remove_pointers(osteomioarticular_health)
    else:
        osteomioarticular_health = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas),
                                                     desc="Total itens recebidos:"))
        osteomioarticular_health = remove_pointers(osteomioarticular_health)

    print(f'Dataset {mongodb_collection} Criado!')
    return osteomioarticular_health


def gerar_tabela_mental_health(filtro=None, colunas=None, mongodb_collection='MentalHealth'):
    # contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        mental_health = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {}),
                                          desc="Total itens recebidos:"))
        mental_health = remove_pointers(mental_health)
    else:
        mental_health = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas),
                                          desc="Total itens recebidos:"))
        mental_health = remove_pointers(mental_health)

    print(f'Dataset {mongodb_collection} Criado!')
    return mental_health


def gerar_tabela_care_plan_data(filtro=None, colunas=None, mongodb_collection='CarePlanData'):
    # contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        care_plan_data = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {}),
                                           desc="Total itens recebidos:"))
        care_plan_data = remove_pointers(care_plan_data)
    else:
        care_plan_data = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas),
                                           desc="Total itens recebidos:"))
        care_plan_data = remove_pointers(care_plan_data)

    print(f'Dataset {mongodb_collection} Criado!')
    return care_plan_data


def gerar_tabela_patient_journey_data(filtro=None, colunas=None, mongodb_collection='PatientJourneyData'):
    # contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        journey = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {'_id': 1,
                                                                         '_created_at': 1,
                                                                         '_p_anamnesisId': 1,
                                                                         '_p_patient': 1,
                                                                         '_p_patientJourneyRuleId': 1,
                                                                         '_updated_at': 1,
                                                                         'completedAppointment': 1,
                                                                         'completedJourney': 1,
                                                                         'data': 1,
                                                                         'healthRisk': 1,
                                                                         'inquiryDate': 1,
                                                                         'isDeleted': 1,
                                                                         'isReportDone': 1,
                                                                         'noPlannedAppointment': 1,
                                                                         'noShowAppointment': 1,
                                                                         'notBookedAppointment': 1,
                                                                         'reportData': 1,
                                                                         'totalAgendaCounts': 1,
                                                                         'journeyFulfillment': 1}),
                                    desc="Total itens recebidos:"))
        journey = remove_pointers(journey)
    else:
        journey = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas), desc="Total itens recebidos:"))
        journey = remove_pointers(journey)

    print(f'Dataset {mongodb_collection} Criado!')
    return journey


def gerar_tabela_patient_journey_rules(filtro=None, colunas=None, mongodb_collection='PatientJourneyRules'):
    # contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        journey_rules = pd.DataFrame(tqdm(db[mongodb_collection].find({}, {}), desc="Total itens recebidos:"))
        journey_rules = remove_pointers(journey_rules)
    else:
        journey_rules = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas), desc="Total itens recebidos:"))
        journey_rules = remove_pointers(journey_rules)

    return journey_rules


def gerar_tabela_logs(filtro=None, colunas=None, mongodb_collection='Logs'):
    # contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        logs = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {'_id': 1,
                                                                      '_created_at': 1,
                                                                      '_updated_at': 1,
                                                                      'collectionName': 1,
                                                                      'corporation': 1,
                                                                      'data': 1,
                                                                      'handle': 1,
                                                                      'madeBy': 1,
                                                                      'method': 1,
                                                                      'userId': 1,
                                                                      'appointment': 1,
                                                                      'support': 1,
                                                                      'createdAt': 1,
                                                                      'objectId': 1,
                                                                      'updatedAt': 1}), desc="Total itens recebidos:"))
        logs = remove_pointers(logs)
    else:
        logs = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas), desc="Total itens recebidos:"))
        logs = remove_pointers(logs)

    print(f'Dataset {mongodb_collection} Criado!')
    return logs


def gerar_tabela_terms_log_during_call(filtro=None, colunas=None, mongodb_collection='TermsLogDuringCall'):
    # contar_itens_collection(filtro, mongodb_collection)
    if colunas is None:
        terms_log_during_call = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, {'_id': 1,
                                                                                       'IP': 1,
                                                                                       '_created_at': 1,
                                                                                       '_p_scheduledAppointment': 1,
                                                                                       '_p_support': 1,
                                                                                       '_p_user': 1,
                                                                                       '_updated_at': 1,
                                                                                       'browser': 1,
                                                                                       'deviceType': 1,
                                                                                       'operationalSystem': 1,
                                                                                       'response': 1,
                                                                                       'type': 1}),
                                                  desc="Total itens recebidos:"))
        terms_log_during_call = remove_pointers(terms_log_during_call)
    else:
        terms_log_during_call = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas),
                                                  desc="Total itens recebidos:"))
        terms_log_during_call = remove_pointers(terms_log_during_call)

    print(f'Dataset {mongodb_collection} Criado!')
    return terms_log_during_call


def gerar_tabela_soap_medication(filtro=None, colunas=None, mongodb_collection='SoapMedication'):
    if colunas is None:
        soap_medication = pd.DataFrame(tqdm(db[mongodb_collection].find({}, {}), desc="Total itens recebidos:"))
        soap_medication = remove_pointers(soap_medication)
    else:
        soap_medication = pd.DataFrame(tqdm(db[mongodb_collection].find(filtro, colunas),
                                            desc="Total itens recebidos:"))
        soap_medication = remove_pointers(soap_medication)

    return soap_medication
