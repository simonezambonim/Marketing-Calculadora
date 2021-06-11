import streamlit as st
from calculadoras.cost_hiring import cost_hiring_page
from calculadoras.turnover import turnover_page
from calculadoras.horas_extras import horas_extras_page


def main():

    st.sidebar.image("./images/Logo-Ahgora.png")

    options = ['Horas extras', 'Custo por contratação', 'Turnover']
    menu = st.sidebar.selectbox("Menu options", options)

    if menu == 'Horas extras':
        horas_extras_page()

    if menu == 'Custo por contratação':
        cost_hiring_page()

    if menu == 'Turnover':
        turnover_page()


if __name__ == '__main__':
    st.set_page_config(layout='wide')
    main()
