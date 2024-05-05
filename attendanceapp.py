import streamlit as st
import pandas as pd
import pygsheets
import os
import json

from google.oauth2 import service_account

# Recreate the JSON credentials from environment variables


st.write("""
ANALYZER - AI ATTENDANCE APPLICATION""", unsafe_allow_html=True)

st.image('title.png', caption='This cat represents the coolness that the AI Team wishes to achieve. '
                              'We look up to this cat.', width=300)

st.markdown("""
<style>
.big-font {
    font-size:20px !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">Use this app to update your tasksheet and attendance.</p>',
            unsafe_allow_html=True)


class AttendanceControl:
    def __init__(self):

        creds_dict = {
            'type': st.secrets['TYPE'],
            'project_id': st.secrets['PROJECT_ID'],
            'private_key_id': st.secrets['PRIVATE_KEY_ID'],
            'private_key': st.secrets['PRIVATE_KEY'],
            'client_email': st.secrets['CLIENT_EMAIL'],
            'client_id': st.secrets['CLIENT_ID'],
            'auth_uri': st.secrets['AUTH_URI'],
            'token_uri': st.secrets['TOKEN_URI'],
            'auth_provider_x509_cert_url': st.secrets['AUTH_PROVIDER_X509_CERT_URL'],
            'client_x509_cert_url': st.secrets['CLIENT_X509_CERT_URL']
        }

        # Use the dictionary to authenticate
        creds_json = json.dumps(creds_dict)
        cjson = json.loads(creds_json)
        print(json.loads(creds_json))
        SCOPES = ('https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive')
        self.gc = pygsheets.authorize(
            custom_credentials=service_account.Credentials.from_service_account_info(cjson, scopes=SCOPES))

        self.team_member = None
        self.team_name = st.selectbox(
            "Team Name",
            ("Choose Team", "AI-VR", "AI-Mechanical"))
        self.current_team_member = None
        # gc = pygsheets.authorize(service_account_env_var=os.environ["service_account_env_var"])
        self.s = self.gc.open_by_url(
            'https://docs.google.com/spreadsheets/d/1D4Jiy15GghqpKtEWFxXMtEBYk-lpcXzfuE4Bpe9Oop8/edit#gid=792410941')
        ws = self.s.worksheet_by_title("Main")
        self.team_names = list(ws.get_values("B2", 'B20000'))
        self.team_members = list(ws.get_values("A2", 'A20000'))

        self.get_names_from_team()

        self.attendance_type = st.selectbox(
            "Attendance Type",
            ("P", "P/2", "Off", "CO", "CO/2", "-CO", "-CO/2", "PH"))

        self.title = st.text_area("Task Description", "")

        self.submit_data()

    def get_names_from_team(self):
        self.team_member = st.selectbox(
            "Employee Name",
            [self.team_members[i][0] for i, team_namez in enumerate(self.team_names) if
             self.team_name == team_namez[0]])
        try:
            self.current_team_member = \
            [i for i, team_membez in enumerate(self.team_members) if self.team_member == team_membez[0]][0] + 2
            print(self.current_team_member)
        except IndexError:
            'No value'

    def submit_data(self):
        if st.button("Send"):
            s = self.gc.open_by_url(
                'https://docs.google.com/spreadsheets/d/1D4Jiy15GghqpKtEWFxXMtEBYk-lpcXzfuE4Bpe9Oop8/edit#gid=792410941')
            ws = s.worksheet_by_title("Main")

            ws.update_value("C2", f"=TODAY()")
            ws.update_value("D2", f'=TEXT(C2, "MMMM")')
            ws.update_value("E2", f'=day(TODAY())')

            ws_att = s.worksheet_by_title(ws.get_value("D2"))
            ws_presence = s.worksheet_by_title(f'{ws.get_value("D2")}-P')

            ws_att.update_value((self.current_team_member, int(ws.get_value("E2")) + 1),
                                f"{self.title}")
            ws_presence.update_value((self.current_team_member, int(ws.get_value("E2")) + 1),
                                     f"{self.attendance_type}")


AttendanceControl()
