import streamlit as st
import pandas as pd
import random
import re

title = 'BPH Arena'
st.set_page_config(page_title=title, layout='wide')
st.title(title)


CATEGORIES = ['General', 'Medical', 'Surgical', 'Decision x1', 'Decision x2']
MODELS = ['ChatGPT 4o - No KB', 'ChatGPT 4o - RAG', 'ChatBPH']
FILEPATH = 'llmdatab.csv'

def parse_csv(file_path):
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip()
    output = []
    current_category = None
    for _, row in df.iterrows():
        if row.iloc[0] in CATEGORIES:
            current_category = row.iloc[0]
        elif row.iloc[0] not in CATEGORIES and current_category:
            question = row.iloc[0]
            eau = row['EAU']
            aua = row['AUA']
            responses = [{model: row[model]} for model in MODELS]
            output.append({'category': current_category, 'question': question, 'eau': eau, 'aua': aua, 'responses': responses, 'picked_model': ''})
    return output

if 'curr_q_pos' not in st.session_state:
    st.session_state.curr_q_pos = -1
if 'curr_q' not in st.session_state:
    st.session_state.curr_q = None
if 'questions' not in st.session_state:
    st.session_state.questions = parse_csv(FILEPATH)
    random.shuffle(st.session_state.questions)
if 'scores' not in st.session_state:
    _tmp = {model: 0 for model in MODELS}
    st.session_state.scores = {category: _tmp.copy() for category in ['Overall']+CATEGORIES}
if 'need_to_update' not in st.session_state:
    st.session_state.need_to_update = False
if 'picked_index' not in st.session_state:
    st.session_state.picked_index = None


# -------------------------------------

total_qs = len(st.session_state.questions)

if st.session_state.curr_q_pos < total_qs:

    if st.session_state.curr_q_pos == -1:
        st.session_state.curr_q_pos += 1
        st.session_state.curr_q = st.session_state.questions[st.session_state.curr_q_pos]
        random.shuffle(st.session_state.curr_q['responses'])

    if st.session_state.need_to_update:
        q = st.session_state.curr_q
        category = q['category']
        winner = [i for i in q['responses'][st.session_state.picked_index].keys()][0]
        st.session_state.scores[category][winner] += 1
        st.session_state.scores['Overall'][winner] += 1

        
        st.session_state.picked_index = None
        st.session_state.need_to_update = False
        st.session_state.curr_q_pos += 1
        if st.session_state.curr_q_pos == total_qs:
            st.rerun()
        st.session_state.curr_q = st.session_state.questions[st.session_state.curr_q_pos]
        random.shuffle(st.session_state.curr_q['responses'])

    remaining_qs = total_qs - st.session_state.curr_q_pos
    st.sidebar.write(f"Questions evaluated: {st.session_state.curr_q_pos}")
    st.sidebar.write(f"Questions left: {remaining_qs}")
    slider = st.sidebar.toggle('Show Scores')

    '---'

    if slider:
        st.sidebar.subheader("Overall")
        for model in MODELS:
            score = st.session_state.scores['Overall'][model]
            st.sidebar.write(f"{model}: {score}")
        
        for category in CATEGORIES:
            st.sidebar.subheader(category)
            for model in MODELS:
                score = st.session_state.scores[category][model]
                st.sidebar.write(f"{model}: {score}")
        
    question = st.session_state.curr_q
    category = question['category']
    question_text = question['question']
    eau = question['eau']
    aua = question['aua']
    responses = question['responses']
    

    st.header(f"Question: {question_text}")
    with st.expander("Show Ground Truth"):
        st.subheader("EAU Information")
        st.markdown(eau)
        st.subheader("AUA Information")
        st.markdown(aua)

    cols1 = st.columns(3)
    cols2 = st.columns(3)

    upper_display = st.container()
    with upper_display:
        for i, response in enumerate(responses):
            for model, response in response.items():
                with cols1[i]:
                    _reformatted = re.sub(r'#+', '######', response)
                    _reformatted = re.sub(r'【.*?】', '', _reformatted)
                    st.subheader(f"Response {i+1}")
                    st.markdown(_reformatted)
    '---'
    for i in range(len(responses)):
        with cols2[i]:
            if st.button(f"Response {i+1} is best", key=f"{i}"):
                    st.session_state.need_to_update = True
                    st.session_state.picked_index = i
                    st.rerun()
                    

else:
    st.write("All questions have been evaluated!")
    st.sidebar.header("Final Scores")
    st.sidebar.subheader("Overall")
    for model in MODELS:
        score = st.session_state.scores['Overall'][model]
        st.sidebar.write(f"{model}: {score}")
    
    st.sidebar.markdown("---")
    
    for category in CATEGORIES:
        st.sidebar.subheader(category)
        for model in MODELS:
            score = st.session_state.scores[category][model]
            st.sidebar.write(f"{model}: {score}")