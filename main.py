from models.connection_azure import ConnectionAzure
from models.data_cleaning import DataCleaning
from models.data_statistics import DataStatistics
from models.data_plotting import DataPlotting
from models.config import Config
import pandas as pd
import sys

sys.tracebacklimit = 0

print('''                                                                                                  
                 _                _      
 _ __  _   _  __| | ___ _ __ ___ (_) ___ 
| '_ \| | | |/ _` |/ _ \ '_ ` _ \| |/ __|
| |_) | |_| | (_| |  __/ | | | | | | (__ 
| .__/ \__, |\__,_|\___|_| |_| |_|_|\___|
|_|    |___/                             

Olá, seja bem vindo! Escolha uma opção:

  1 - Métricas
  2 - Configurações
  3 - Sair
''')
option = input('Opção: ')

while not option.isdigit() or not int(option) in [1, 2, 3]:
    option = input("Favor informar uma opção válida: ")

option = int(option)

if option == 3:
    print('1 - Encerrando o Pydemic..................[OK]')
else:
    print('1 - Carregando as Configurações...........', end='')
    read_config = Config()
    customer = read_config.get_customer()
    credentials = read_config.get_credentials()
    board = read_config.get_board()
    paths = read_config.get_paths()
    config_type = read_config.get_types()
    transitions = read_config.get_transitions_map()
    transitions_steps = read_config.get_initial_and_last_map()
    iterations = read_config.get_iterations()
    holidays = read_config.get_holidays()
    print('[OK]')

    print('2 - Conectando no Azure DevOps............', end='')
    connection_azure = ConnectionAzure(credentials['personal_access_token'], credentials['organization_url'],
                                       board['project'], board['area_path'], config_type['config_type'])
    connection_azure.run_connection()
    print('[OK]')

    print('3 - Coletando os Works Items..............', end='')
    connection_azure.get_work_items()
    df_revisions = connection_azure.get_work_items_revisions()
    print('[OK]')

    if option == 1:
        print('4 - Efetuando a Limpeza dos Dados.........', end='')
        data_cleaning = DataCleaning(df_revisions, transitions['transitons_map'], transitions['transitions_steps'],
                                     iterations['iterations_sprints'], transitions['last_step_transitions'],
                                     transitions_steps['initial_step_transitions_leadtime'],
                                     transitions_steps['last_step_transitions_leadtime'],
                                     transitions_steps['initial_step_transitions_cycletime'],
                                     transitions_steps['last_step_transitions_cycletime'], holidays)
        df_revisions = data_cleaning.run()
        print('[OK]')

        print('5 - Efetuando Cálculos Estatísticos.......', end='')
        for i in df_revisions:
            data_revisions = DataStatistics(i[0])
            revisions = data_revisions.run()
            path = paths[i[1]]

            revisions['revisions'].to_csv(
                path + '/detalhado_' + i[1] + '_' + customer + '.csv', sep='|', index=False, header=True,
                encoding='utf-8-sig')
            revisions['efficiency'].to_csv(
                path + '/eficiencia_' + i[1] + '_' + customer + '.csv', sep='|', index=False, header=True,
                encoding='utf-8-sig')
            revisions['throughput'].to_csv(
                path + '/throughput_' + i[1] + '_' + customer + '.csv', sep='|', index=False, header=True,
                encoding='utf-8-sig')
            revisions['measures'].to_csv(
                path + '/medidas_' + i[1] + '_' + customer + '.csv', sep='|', index=False, header=True,
                encoding='utf-8-sig')
            revisions['interval'].to_csv(
                path + '/estimativas_' + i[1] + '_' + customer + '.csv', sep='|', index=False, header=True,
                encoding='utf-8-sig')
        print('[OK]')

        print('7 - Criando os gráficos...................[OK]')
        for i in df_revisions:
            data_plotting = DataPlotting(i[0], paths[i[1]])
            plotting = data_plotting.run()

        print('8 - Fim do processamento..................[OK]')
        input("Pressione ENTER para finalizar")

    elif option == 2:
        print('4 - Salvando o Arquivo....................', end='')
        df_transitions = df_revisions.boardColumn.unique()
        df_transitions = pd.DataFrame(df_transitions)
        df_transitions.columns = ['boardColumn']
        df_transitions.dropna(subset=['boardColumn'], inplace=True)
        df_transitions.to_csv(paths['root'] + '/config_transicoes_' + customer + '.csv',
                              index=False, header=False, encoding='utf-8-sig')
        print('[OK]')

        print('5 - Fim do processamento..................[OK]')
        input("Pressione ENTER para finalizar")
