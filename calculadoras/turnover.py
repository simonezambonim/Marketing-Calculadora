import streamlit as st


def turnover_page():
    number_employees = st.sidebar.number_input('Número de colaboradores', value=1, key='tne')
    employees_admission = st.sidebar.number_input('Número de admissões', value=0, key='ne')
    voluntary_temination = st.sidebar.number_input('Número de desligamentos voluntários', value=0, key='vt')
    disciplinary_termination = st.sidebar.number_input('Número de desligamentos involuntários ', value=0, key='dt')
    # unavoidable_termination = st.sidebar.number_input('Número de desligamentos inevitáveis ', value=0, key='ut')

    st.header("Turnover")
    cols = st.beta_columns(3)
    cols[0].markdown('''
                       $$
                       \\frac{\\frac{TA+TD}{2}}{TC} 
                       $$

                       - $TA$ - Número de admissões
                       - $TD$ - Número de desligamentos (voluntários+involuntários)
                       - $TC$ - Número de colaboradores ativos

                       ''')
    turnover = 100 * (
            (employees_admission + (voluntary_temination + disciplinary_termination)) / 2) / number_employees
    cols[0].write(f'Turnover = {turnover:.2f} %')

    cols = st.beta_columns(3)
    cols[0].subheader("Taxa de desligamento")
    cols[0].markdown('''
                       $$
                       \\frac{TDI+TDV}{TC} 
                       $$

                       - $TDI$ - Número de desligamentos involuntários
                       - $TDV$ - Número de desligamentos voluntários
                       - $TC$ - Número de colaboradores ativos

                       ''')
    td = 100 * (voluntary_temination + disciplinary_termination) / number_employees
    cols[0].write(f'Taxa de desligamento = {td:.2f} %')
    st.write('Índice de turnover considerável é de X% ao ano.')

    # https://solides.com.br/ferramentas/calculadora-de-rotatividade/