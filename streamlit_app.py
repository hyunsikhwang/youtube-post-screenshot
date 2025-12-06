import os
os.system("playwright install")
os.system("playwright install chromium")
os.system("playwright install-deps")

import streamlit as st
from playwright.sync_api import Playwright, sync_playwright, expect


st.write("# YouTube Post Screenshot App")