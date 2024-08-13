import commune as c
import json
import numpy as np
import os
import streamlit as st
import plotly.express as px
import datetime
import arena as a

class App(c.Module):
    logo_path = __file__.replace('app/app.py', 'logo.png')
    def __init__(self):
        # set wide
        # compress the height
        st.set_page_config(layout="wide")
        st.image(self.logo_path)
        self.arena = a.Arena()
        self.games = self.arena.games()

    def sidebar(self):
        st.title("Arena")
        user = st.sidebar.text_input("Username", 'user')
        password = st.sidebar.text_input("Password", '12345', type='password')
        self.login(user, password)
        st.write(f"Account")
        st.code( self.account.ss58_address)
        game = st.sidebar.selectbox('Select Game', self.games)
        self.game = self.arena.get_game( game)

    def login(self, user, password, role='owner'):
        self.account = a.Account(user=user, password=password, role='user')
        return self.account

    def app(self):
        with st.sidebar:
            self.sidebar()
        tab_names = ['Play', 'Leaderboard']
        tabs = st.tabs(tab_names)
        with tabs[0]:
            self.play(self.game)
        with tabs[1]:
            self.leaderboard(self.game)
    def play(self, game):
        game_state = game.start_game()
        game_state = self.account.sign(game_state)
        show_game_state = c.copy(game_state)
        show_game_state.pop('signatures')
        with st.expander('WTF do I do?', expanded=False):
            st.write(show_game_state['description'])
        game_state['input'] = st.text_area('Game', 'Say something crazy')
        # dragon emoji 🐉
        button_name = f'🐉 Submit :: {game_state["model"]} 🐉'
        submit = st.button(button_name, use_container_width=True)
        if submit:
            output = game.submit_game(game_state)
            st.write(output)

    def leaderboard(self, game):
        df = game.leaderboard()
        st.write(df)
        fig = px.scatter(df, x='timestamp', y='score', color='address')
        st.plotly_chart(fig)
App.run(__name__)