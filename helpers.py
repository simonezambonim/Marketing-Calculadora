import streamlit as st
import SessionState

session_state = SessionState.get(email=False, count_group=0)


def validate_email(number_of_groups):
    if number_of_groups > 1:
        with st.form(key='my-form'):

            st.write('Para ter acesso ao cálculo completo, informe seu e-mail:')
            email = st.text_input(label='Digite seu email:')
            submit_button = st.form_submit_button('Enviar')

        if submit_button or session_state.email:
            session_state.email = True


def analise_cenarios(df_data):
    if session_state.email:

        st.header("Análise de Cenários")
        df_he = df_data.copy().reset_index(drop=True)
        df_he['Tipo de Horas Extras'] = df_he.loc[df_he['Tipo'].str.startswith('Horas extras'), 'Tipo']

        s = None
        for x in df_he[['Grupo', 'Tipo de Horas Extras']].dropna().drop_duplicates().iterrows():

            if x[1][0] != s:
                st.subheader(f'{x[1][0]}')

            cols = st.beta_columns((1.5, 3, 6))
            cols[0].markdown(f'{x[1][1]}')
            he_reduce = cols[1].slider("Redução em % de horas extras realizadas",
                                       min_value=0,
                                       max_value=100,
                                       step=5,
                                       value=10,
                                       key=f'{x[1][0]} e {x[1][1]}')

            df_he.loc[x[0], 'Redução'] = he_reduce / 100
            s = x[1][0]

        df_he['Horas totais com controle'] = df_he['Horas totais'] * (1 - df_he['Redução'])
        df_he['Horas totais com controle'].fillna(df_he['Horas totais'], inplace=True)
        df_he['Valor total com controle'] = df_he['Horas totais com controle'] * df_he['Valor hora']
        df_he['Valor total com controle'].fillna(df_he['Valor total'], inplace=True)

        df_he_cross = pd.crosstab(index=df_he["Tipo"],
                                  columns=df_he["Grupo"],
                                  values=df_he["Valor total com controle"],
                                  aggfunc=np.sum,
                                  margins=True,
                                  margins_name='Total')

        st.table(df_he_cross)
        df_he_display = df_he[['Grupo', 'Tipo', 'Redução', 'Horas totais', 'Horas totais com controle',
                               'Valor total', 'Valor total com controle']].style.format({'Redução': "{:.0%}",
                                                                                         'Horas totais': "{:.1f} h",
                                                                                         'Horas totais com controle': "{:.1f} h",
                                                                                         'Valor total com controle': "R$ {:.2f}",
                                                                                         'Valor total': "R$ {:.2f}"},
                                                                                        na_rep="-")

        st.table(df_he_display)

