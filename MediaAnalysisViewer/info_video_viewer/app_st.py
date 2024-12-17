import urllib.parse
import streamlit as st
import pandas as pd
import requests
import io
import re
import numpy as np
import webbrowser
import os
import urllib
#To run :
#streamlit run http://mntdaniel:8502/?src=//mntdaniel/movies/benGvir.mp4&tsrt=benGvir_20230719_172724.tsrt.csv&start=39&end=44


offset_options = {
        "onload": 0,
        "person": 1,
        "org": 2,
        "date": 3,
        "money": 4,
        "location": 5,
        "geopolitical": 6,
        "event": 7,
        "work_of_art": 8,
        "language": 9,
        "persons": 10,
        "time": 11,
        "product": 12,

    }
def load_video(path, offset):
    ph = st.empty()
    ph_audio = st.empty()
    if path.startswith("http"):
       st.video(path,  start_time=offset)
    else:
        with open(path, "rb") as file:
            video_bytes = file.read()
            ph.video(video_bytes, start_time=offset)
            #ph_audio.audio(video_bytes, start_time=offset)

    return

def set_rtl() :
    st.markdown("""<style> * {direction: RTL;}</style>""", unsafe_allow_html=True)


def remove_footer():
    st.markdown("""<style>#MainMenu{visibility:hidden;}footer{visibility:hidden}</style>""", unsafe_allow_html=True)


def extract_query_string_parameter(url, parameter) :
    if url=='blank' : return -1
    parsed_url = urllib.parse.urlparse(url)
    query_params = urllib.parse.parse_qs(parsed_url.query)
    return query_params[parameter][0]

def get_choices(df,entity) :
    try :
        #entity_p = df[df[entity].str.strip() != ""]
        entity_p = df[df[entity].astype(str).str.strip() != ""]
        entity_p = entity_p.drop(entity_p.columns.difference([entity, "movieurl"]), axis=1)
        entity_p = entity_p.dropna(axis=0)
        entity_p = entity_p.set_index("movieurl")

        choices = entity_p.to_dict()
        choices = choices[entity]
        choices = {'blank': '--', **choices}
        return choices
    except KeyError:
        return None


def main():
    set_rtl()
    remove_footer()

    #st.title("SharePoint Media Analysis ")
   
    #root_path = "//mntdaniel/movies/"

    tsrt_path = "d:/projects/movies/tsrt/"
    tsrt_path = "D:/Projects/MediaAnalysis/MediaAnalysisViewer/tsrt/"
    video_params =(st.experimental_get_query_params())

    video = video_params["src"][0].split("/")[-1]


# src is in the following forward slash format : src=//mntdaniel/movies/meron01.mp4
    video_path = video_params["src"][0]

    csv_filename = tsrt_path + video_params["tsrt"][0]

    try:
        df = pd.read_csv(csv_filename, delimiter='#')
    except FileNotFoundError:
        print("file not found")
        st.write("file not found")
        df = pd.DataFrame()
        exit()


    def set_selected_flag(offset_option):
        st.session_state.offset_selected_flag = offset_option
    logo_url = 'http://danieldev/sites/hebsearch/SiteAssets/lighthouse.jpg'
    logo_url = "lighthouse-nobgp.png"
    st.sidebar.image(logo_url, width=80)
    st.sidebar.markdown("<span style='font-size:20px; color:rgb(0, 114, 198)'/> מגדלור </span><span style='font-size:14px; color:rgb(0, 114, 200)'> מערכת גילוי דיגטלית למיצוי ופענוח ראייתי </span>" , unsafe_allow_html=True)

    st.sidebar.header("מיצוי ישויות " )



    choices_person = get_choices(df,"EntityPerson")
    #print(type(choices_person), choices_person)
    if choices_person is not None:
        option_person = st.sidebar.selectbox("אנשים המופיעם בסרט", key="select_person_entity",
                                             options=list(choices_person.keys()),
                                             format_func=lambda x:choices_person[x], on_change=set_selected_flag,
                                             args=(offset_options["person"],))

    choices_org = get_choices(df, "EntityOrganization")
    if choices_org is not None:
        option_org = st.sidebar.selectbox("ארגונים \ קבוצת אנשים המופיעם בסרט", key="select_organization_entity",
                                          options=list(choices_org.keys()),
                                          format_func=lambda x:choices_org[x],  on_change=set_selected_flag,
                                          args=(offset_options["org"],))

    choices_date = get_choices(df, "EntityDate")
    if choices_date is not None:
        option_date = st.sidebar.selectbox("תאריכים המופיעם בסרט", key="select_date_entity",
                                          options=list(choices_date.keys()),
                                          format_func=lambda x: choices_date[x], on_change=set_selected_flag,
                                          args=(offset_options["date"],))

    choices_money = get_choices(df, "EntityMoney")
    if choices_money is not None :
        option_money = st.sidebar.selectbox("התייחסות לכסף  בסרט", key="select_money_entity",
                                           options=list(choices_money.keys()),
                                           format_func=lambda x: choices_money[x], on_change=set_selected_flag,
                                           args=(offset_options["money"],))

    choices_location = get_choices(df, "EntityLocation")
    if choices_location is not None:
        option_location = st.sidebar.selectbox("אזורים \ מיקומים המופיעים בסרט", key="select_location_entity",
                                        options=list(choices_location.keys()),
                                        format_func=lambda x: choices_location[x], on_change=set_selected_flag,
                                        args=(offset_options["location"],))

    choices_geopolitical = get_choices(df, "EntityGeoPolitical")
    if choices_geopolitical is not None:
        option_geopolitical = st.sidebar.selectbox(" מיקום גאו-פוליטי", key="select_geopolitical_entity",
                                               options=list(choices_geopolitical.keys()),
                                               format_func=lambda x: choices_geopolitical[x],
                                               on_change=set_selected_flag,
                                               args=(offset_options["geopolitical"],))
    choices_language = get_choices(df, "EntityLanguage")
    if choices_language is not None:
        option_language = st.sidebar.selectbox("שפה", key="select_language_entity",
                                               options=list(choices_language.keys()),
                                               format_func=lambda x: choices_language[x],
                                               on_change=set_selected_flag,
                                               args=(offset_options["language"],))

    choices_time = get_choices(df, "EntityTime")
    if choices_time is not None:
        option_time = st.sidebar.selectbox("זמן", key="select_time_entity",
                                               options=list(choices_time.keys()),
                                               format_func=lambda x: choices_time[x],
                                               on_change=set_selected_flag,
                                               args=(offset_options["time"],))
    choices_workofart = get_choices(df, "EntityWorkOfArt")
    if choices_workofart is not None:
        option_workofart = st.sidebar.selectbox("יצירת אומנות", key="select_workofart_entity",
                                               options=list(choices_workofart.keys()),
                                               format_func=lambda x: choices_workofart[x],
                                               on_change=set_selected_flag,
                                               args=(offset_options["work_of_art"],))
    choices_product = get_choices(df, "EntityProduct")
    if choices_product is not None:
        option_product = st.sidebar.selectbox("מוצר", key="select_product_entity",
                                               options=list(choices_product.keys()),
                                               format_func=lambda x: choices_product[x],
                                               on_change=set_selected_flag,
                                               args=(offset_options["product"],))
    choices_event = get_choices(df, "EntityEvent")
    if choices_event is not None:
        option_event = st.sidebar.selectbox("ארוע", key="select_event_entity",
                                              options=list(choices_event.keys()),
                                              format_func=lambda x: choices_event[x],
                                              on_change=set_selected_flag,
                                              args=(offset_options["event"],))


    if 'offset_selected_flag' not in st.session_state:
        offset = int(video_params["start"][0])
        load_video(video_path, offset)
        st.session_state.offset_selected_flag = 0
    else:
        if st.session_state.offset_selected_flag == offset_options["person"]:
            offset = int(extract_query_string_parameter(option_person, "start"))
        if st.session_state.offset_selected_flag == offset_options["org"]:
            offset = int(extract_query_string_parameter(option_org, "start"))
        if st.session_state.offset_selected_flag == offset_options["date"]:
            offset = int(extract_query_string_parameter(option_date, "start"))
        if st.session_state.offset_selected_flag == offset_options["money"]:
            offset = int(extract_query_string_parameter(option_money, "start"))
        if st.session_state.offset_selected_flag == offset_options["location"]:
            offset = int(extract_query_string_parameter(option_location, "start"))
        if st.session_state.offset_selected_flag == offset_options["geopolitical"]:
            offset = int(extract_query_string_parameter(option_geopolitical, "start"))
        if st.session_state.offset_selected_flag == offset_options["work_of_art"]:
            offset = int(extract_query_string_parameter(option_workofart, "start"))
        if st.session_state.offset_selected_flag == offset_options["language"]:
            offset = int(extract_query_string_parameter(option_language, "start"))
        if st.session_state.offset_selected_flag == offset_options["time"]:
            offset = int(extract_query_string_parameter(option_time, "start"))
        if st.session_state.offset_selected_flag == offset_options["product"]:
            offset = int(extract_query_string_parameter(option_product, "start"))
        if st.session_state.offset_selected_flag == offset_options["event"]:
            offset = int(extract_query_string_parameter(option_event, "start"))


        if "offset" in locals() :
            st.experimental_set_query_params(start=offset, src=video_path, tsrt=video_params["tsrt"][0])
            load_video(video_path, offset)
        else :
            offset=0
            st.experimental_set_query_params(start=0, src=video_path,tsrt=video_params["tsrt"][0])
            load_video(video_path, offset)

        st.session_state.offset_selected_flag = 0


if __name__ =='__main__':
   main()




