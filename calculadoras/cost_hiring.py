import streamlit as st
import numpy as np

def cost_hiring_page():
    st.header('Calculadora de custo por contratação')
    cc_ad = st.number_input('Custo com Propaganda', value=0, key='cc_ad')
    cc_er = st.number_input('Custos de indicação do funcionário', value=0, key='cc_er')
    cc_af = st.number_input('Custo com taxas de agência', value=0, key='cc_af')
    cc_relo = st.number_input('Custo com realocação', value=0, key='cc_relo')
    cc_t = st.number_input('Custo com viagem', value=0, key='cc_t')
    cc_rc = st.number_input('Custo com tempo dos recrutadores', value=0, key='cc_rc')
    cc_adm = st.number_input('Custos adm relacionados a contratação (%)',
                             min_value=0.0,
                             max_value=100.0,
                             value=0.0,
                             step=1.0,
                             key='cc_adm')

    total_cc = np.sum([cc_ad, cc_er, cc_af, cc_relo, cc_t, cc_rc]) * (1 + cc_adm / 100)
    st.write(f"\n\nCusto total de Contratação: {total_cc:.2f}")

