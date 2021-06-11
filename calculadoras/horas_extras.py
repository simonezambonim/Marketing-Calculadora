import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

def form_horas_extras(group, one_employee=False):
    n_employees = 1
    employee_group = 'Funcionário'
    if not one_employee:
        cols = st.beta_columns((5, 5))
        employee_group = cols[0].text_input("Nome do grupo de colaboradores, por ex.: Atendentes",
                                            value=f'Grupo {group}',
                                            key=f'tipo{group}')

    cols = st.beta_columns(3)
    if not one_employee:
        n_employees = cols[0].number_input("Número de funcionários do grupo",
                                           value=1,
                                           min_value=1,
                                           key=f'nfuncionarios{group}')

    salario_classe = cols[1 - int(one_employee)].number_input("Salário base mensal por colaborador / mês",
                                                              value=1100.00,
                                                              key=f'salario{group}'
                                                              )
    horas_semanais = cols[2 - int(one_employee)].number_input("Carga horária (h) por colaborador / semana",
                                                              value=40,
                                                              key=f'hsemanal{group}'
                                                              )

    cols = st.beta_columns(3)
    multiplicador_options = [1.5, 1.6, 1.7, 1.8, 2]
    multiplicador = cols[0].selectbox('Fator multiplicador de horas extras',
                                      options=multiplicador_options,
                                      key=f'multiplicador{group}'
                                      )
    horas_extras = cols[1].number_input("Horas extras (h) por colaborador / mês",
                                        value=10,
                                        key=f'horasextras{group}'
                                        )

    add_faltas = cols[2].checkbox('Adicionar Faltas',
                                  key=f'add_faltas{group}')
    add_fator = cols[2].checkbox('Adicionar horas extras',
                                 key=f'add_he{group}'
                                 )

    horas_extras1 = np.nan
    multiplicador1 = np.nan
    space0 = cols[0].empty()
    space1 = cols[1].empty()
    if add_fator:
        multiplicador_options.remove(multiplicador)
        multiplicador1 = space0.selectbox('Fator multiplicador de horas extras',
                                          options=multiplicador_options,
                                          key=f'multiplicadoradd{group}',
                                          help='''Se os colaboradores trabalharem em domingos e feriados 
                                          o valor da hora extra é igual a 100% da hora normal, ou seja, 
                                          Fator multiplicador de 2.''')
        horas_extras1 = space1.number_input("Horas extras (h) por colaborador / mês",
                                            value=10,
                                            key=f'horasextrasadd{group}'
                                            )

    cols = st.beta_columns(3)
    horas_faltas = np.nan
    if add_faltas:
        horas_faltas = cols[0].number_input("Faltas (h) por colaborador / mês", 0, 220,
                                            value=8,
                                            key=f'horasfaltas{group}'
                                            )

    valor_hora = round(salario_classe / (4 * horas_semanais), 2)
    data = {'Grupo': employee_group,
            'Tipo': ['Regular',
                     f'Horas extras {multiplicador}',
                     f'Horas extras {multiplicador1}',
                     'Faltas'
                     ],
            'Valor hora': [valor_hora,
                           valor_hora * multiplicador,
                           valor_hora * multiplicador1,
                           valor_hora
                           ],
            'Horas por funcionário': [4 * horas_semanais,
                                      horas_extras,
                                      horas_extras1,
                                      - horas_faltas
                                      ],
            'Horas totais': [n_employees * 4 * horas_semanais,
                             n_employees * horas_extras,
                             n_employees * horas_extras1,
                             - n_employees * horas_faltas
                             ],
            'Valor por funcionário': [4 * valor_hora * horas_semanais,
                                      horas_extras * valor_hora * multiplicador,
                                      horas_extras1 * valor_hora * multiplicador1,
                                      - horas_faltas * valor_hora
                                      ],
            'Valor total': [n_employees * 4 * valor_hora * horas_semanais,
                            n_employees * horas_extras * valor_hora * multiplicador,
                            n_employees * horas_extras1 * valor_hora * multiplicador1,
                            -n_employees * horas_faltas * valor_hora
                            ]

            }

    df_group = pd.DataFrame(data).dropna()

    display_localdf(df_group, one_employee)
    dict_employees = {'Grupo': employee_group,
                      'Colaboradores': n_employees}

    return df_group, dict_employees


def display_localdf(df, one_employee=False):
    df_display = df.copy()
    df_display = df_display.set_index(['Tipo']).drop(columns='Grupo')
    df_display.loc['Total'] = df_display.sum()
    df_display.loc['Total', 'Valor hora'] = df_display.loc['Total', 'Valor total'] / df_display.loc[
        'Total', 'Horas totais']

    if one_employee:
        st.table(df_display[['Valor hora', 'Horas totais', 'Valor total']].style.format({'Valor hora': "R$ {:.2f} /h",
                                                                                         'Horas totais': "{:.1f} h",
                                                                                         'Horas por funcionário': "{:.1f} h",
                                                                                         'Valor por funcionário': "R$ {:.2f}",
                                                                                         'Valor total': "R$ {:.2f}"
                                                                                         }, na_rep="-"))
    else:
        st.table(df_display.style.format({'Valor hora': "R$ {:.2f} /h",
                                          'Horas totais': "{:.1f} h",
                                          'Horas por funcionário': "{:.1f} h",
                                          'Valor por funcionário': "R$ {:.2f}",
                                          'Valor total': "R$ {:.2f}"
                                          }, na_rep="-"))


@st.cache(allow_output_mutation=True)
def get_data(file, cols):
    return pd.read_excel(file, names=cols)


def lista_horas_extras(df):
    df["Valor hora base"] = df['salario base'] / (4 * df.iloc[:, 1])
    df['tipo'] = df['fator horas extras'].map(lambda x: f"Horas extras {x:.1f}")
    horas_df = df.groupby(['id', 'tipo']).agg({'horas extras (h)': "sum"})
    horas_df = horas_df.unstack(fill_value=0, level=1)
    horas_df.columns = [col[1] for col in horas_df.columns.values]
    horas_df['Faltas'] = df.groupby(['id']).agg({'faltas (h)': "sum"})
    horas_df['Regular'] = 4 * df[['id', 'carga horaria (h)']].drop_duplicates().set_index('id')

    valor_df = df.groupby(['id', 'tipo']).agg({'fator horas extras': "sum"})
    valor_df = valor_df.unstack(fill_value=0, level=1)
    valor_df.columns = [col[1] for col in valor_df.columns.values]
    valor_df['Faltas'] = -1
    valor_df['Regular'] = 1
    valor_hora = df[["id", "Valor hora base"]].drop_duplicates().set_index('id')
    valor_df = valor_df.apply(lambda x: x.mul(valor_hora["Valor hora base"]))

    total = valor_df * horas_df
    total['Total'] = total.sum(axis=1)
    total.loc['Total', :] = total.sum(axis=0)
    horas_df['Total'] = horas_df.sum(axis=1)
    horas_df.loc['Total', :] = horas_df.sum(axis=0)
    valor_df['Total'] = total['Total'] / horas_df['Total']

    st.header("Seu resultado")
    my_expander = st.beta_expander("Horas Totais", expanded=False)
    with my_expander:
        st.subheader("Horas Totais")
        st.table(horas_df.style.format('{:.1f} h'))
    my_expander = st.beta_expander("Valor Hora", expanded=False)
    with my_expander:
        st.subheader("Valor Hora")
        st.table(valor_df.drop(columns=['Faltas']).style.format('R$ {:.2f} /h'))
    my_expander = st.beta_expander("Valor Total", expanded=False)
    with my_expander:
        st.subheader("Valor Total")
        st.table(total.style.format('R$ {:.2f}'))

    return total


def charts_views(df_data, df_colaboradores):
    cols = st.beta_columns((8, 4))
    chart_data = df_data[['Grupo', 'Tipo', 'Valor total', 'Horas totais']].groupby(
        ['Grupo', 'Tipo']).sum().reset_index().sort_values(by=['Grupo', 'Tipo'])
    domain = df_data.Tipo.unique().tolist()

    range_ = ['#6666bb', '#f35082', '#42b6f0',"#22bb44",
              '#ffcd44', '#ff8244', '#3388ee',
              '#9d9dae', '#aaaaaa']

    map_colors = {'Regular': "#1166cc",
                  'Faltas': '#ec4d4d'
                  }
    i = 0
    range_colors = []
    for x in domain:
        try:
            pick = map_colors[x]
        except:
            pick = range_[i]  # random.choice([x for x in range_ if x not in range_colors])
            i += 1
        range_colors.append(pick)

    fig = alt.Chart(chart_data).mark_bar(
        cornerRadiusTopLeft=3,
        cornerRadiusTopRight=3
    ).encode(
        x=f'{chart_data.columns[0]}:N',
        y=f'{chart_data.columns[2]}:Q',
        color=f'{chart_data.columns[1]}:N',#alt.Color(f'{chart_data.columns[1]}:N', scale=alt.Scale(domain=domain, range=range_colors)),

        tooltip=['Grupo', 'Tipo', 'Valor total', 'Horas totais']
    ).properties(
        height=500
    )

    cols[0].subheader('Valor Total')
    cols[0].altair_chart(fig, use_container_width=True)
    cols[1].subheader('Headcount')
    cols[1].vega_lite_chart(df_colaboradores, spec={
        "height": 400,
        "mark": {"type": "arc", "innerRadius": 100, 'tooltip': True},
        "encoding": {
            "theta": {"field": "Colaboradores", "type": "quantitative"},
            "color": {"field": "Grupo", "type": "nominal"}
        },
        "view": {"stroke": None}
    },
                            use_container_width=True)


def charts_views_one(df_data):
    cols = st.beta_columns((2, 8, 2))
    chart_data = df_data[['Grupo', 'Tipo', 'Valor total', 'Horas totais', 'Valor hora']].groupby(
        ['Grupo', 'Tipo']).sum().reset_index().sort_values(by=['Grupo', 'Tipo'])

    fig = alt.Chart(chart_data).mark_bar(
        cornerRadiusTopLeft=3,
        cornerRadiusTopRight=3
    ).encode(
        x=alt.X(f'{chart_data.columns[1]}:N', sort='-y'),
        y=f'{chart_data.columns[2]}:Q',
        color=alt.condition(
            alt.datum[f'{chart_data.columns[2]}'] > 0,
            alt.value('#1166cc'),  # The positive color
            alt.value('#ec4d4d')  # The negative color
        ),
        tooltip=['Grupo', 'Tipo', 'Valor hora', 'Valor total', 'Horas totais']
    ).properties(
        height=500
    )

    cols[1].subheader('Valor Total')
    cols[1].altair_chart(fig, use_container_width=True)


def he_oneemployee():

    entry_blockone = st.beta_container()
    with entry_blockone:
        my_expander = st.beta_expander("Dados do Funcionário", expanded=True)
        with my_expander:
            df_data, _ = form_horas_extras(200, True)

        st.header("Resultado:")
        charts_views_one(df_data)

def he_listemployees():
    entry_blocktwo = st.beta_container()
    with entry_blocktwo:
        st.write("Construa um arquivo _excel_ no seguinte formato:")
        cols = st.beta_columns((2, 8, 2))
        cols[1].markdown('''                
                    |id  |carga horaria (h) |salario base |horas extras (h)| fator horas extras |faltas (h)|
                    |---------|----|---------|---|-----|----|
                    |José V.  |  40|1100,00  |5  |1,5  |1	|
                    |Maria L. |  40|2500,00  |8  |1,5  |2,5	|
                    |         |    |         |   |     |    |
                    |Luiz A.¹ |  40|3000,00  |5  |1,5  |8	|
                    |Luiz A.  |  40|3000,00  |8  |2,0  |0	|
                    ''')

        st.write('''¹ O colaborador _Luiz A._ aparece em duas entradas no arquivo acima, 
                             isto porque ele trabalhou em dois tipos de horas extras (por _ex._: 5h com fator de 1.5x, 
                             e 8h no DSR com fator de 2x). No entanto, 
                             observe que o registro de faltas aparece apenas uma única vez por colaborador. ''')
        file = st.file_uploader('Carregue seu arquivo xls')

        if file is not None:
            cols = ['id', 'carga horaria (h)', 'salario base',
                    'horas extras (h)', 'fator horas extras', 'faltas (h)']
            df_input = get_data(file, cols)
            df_total = lista_horas_extras(df_input)

            fig = alt.Chart(df_total.iloc[:-1].reset_index()).mark_bar().encode(
                x='id',
                y='Total'
            ).properties(
                height=500
            )
            st.altair_chart(fig, use_container_width=True)


def he_groups():
    cols = st.beta_columns((3, 6))
    number_of_groups = cols[0].number_input('Insira o número de grupos de funcionários:', value=1, max_value=10,
                                            key='ngroups', help='''Considere um grupo
                                            como um conjunto de funcionários  com um 
                                            salário base similar, bem como 
                                            o comportamento de horas extras realizadas 
                                            e faltas no período mensal. 
                                            ''')
    entry_block = st.beta_container()
    with entry_block:
        colaboradores = list()
        df_data = pd.DataFrame()
        for group in range(0, number_of_groups):
            to_expand = True if (group == 0) else False
            my_expander = st.beta_expander(f"Grupo {group}", expanded=to_expand)
            with my_expander:
                df_group, colabs = form_horas_extras(group)
                colaboradores.append(colabs)
                df_data = pd.concat([df_data, df_group], axis=0)

    df_total = pd.crosstab(index=df_data["Tipo"],
                           columns=df_data["Grupo"],
                           values=df_data["Valor total"],
                           aggfunc=np.sum,
                           normalize=False,
                           margins=True,
                           margins_name='Total')

    df_total_percent = pd.crosstab(index=df_data.Tipo.str.replace(r'[1-9]+\.*', "", regex=True),
                                   columns=df_data["Grupo"],
                                   values=df_data["Valor total"],
                                   aggfunc=np.sum,
                                   normalize=True,
                                   margins=True,
                                   margins_name='Total')

    df_colaboradores = pd.DataFrame.from_dict(colaboradores)

    st.header("Resultado:")
    st.table(df_total.style.format("R$ {:.2f}", na_rep="-"))
    charts_views(df_data, df_colaboradores)

    # for x in df_total_percent.T.columns:
    #     if x != 'Total':
    #         st.write(
    #             f'Custo de {x} representa {df_total_percent.loc["Total", x] * 100:.2f} % da sua folha de pagamento.')

    # norm = st.checkbox("Visualizar os resultados em %?", key='normalize')
    # if norm:
    st.table(df_total_percent.T.style.format("{:.2%}", na_rep="-"))


def horas_extras_page():
    type_calc = st.sidebar.radio('Selecione uma das opções:',
                                 ['Apenas um funcionário', 'Grupos de Funcionários', 'Lista de funcionários'])

    st.title('Calculadora de Horas Extras')
    st.markdown('Use esta calculadora para simular o quanto você gasta com horas extras!')
    ad = '''
    Quer reduzir os custos com folha de pagamento, sem ter que desligar colaboradores? 
    \nEntão primeiro é necessário identificar onde é preciso fechar a torneira: as _horas extras_. 
    \n\nAcesse [www.ahgora.com.br](www.ahgora.com.br) 
    e descubra como fazer gestão inteligente da jornada de trabalho do seu time.
    \n\n[Saiba mais](https://pages.ahgora.com.br/orcamento)        
    '''

    st.sidebar.markdown(ad)

    if type_calc == 'Apenas um funcionário':
        he_oneemployee()

    if type_calc == "Lista de funcionários":
        he_listemployees()

    if type_calc == 'Grupos de Funcionários':
        he_groups()
