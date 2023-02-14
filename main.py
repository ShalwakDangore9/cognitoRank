import streamlit as st
import boto3
import json
from argparse import ArgumentParser

import requests
from bs4 import BeautifulSoup

st.title('CognitoRank - Text Summarizer')


st.text_input("Access Key", key="key",
              help="Please find the access key on the last page of the presentation in google drive")
accessKey = st.session_state.key

sm = boto3.client('sagemaker-runtime', region_name='us-east-1', aws_access_key_id=accessKey,
                  aws_secret_access_key='OYDggYlMNQCPQls/f1ol5Hzea+RtcpbXykIdja85')

parser = ArgumentParser()
parser.add_argument('--endpoint_name')
args = parser.parse_args()


def predict(texts, min_length, endpoint_name='huggingface-pytorch-inference-2023-02-13-20-03-36-544'):
    global summary
    try:
        response = sm.invoke_endpoint(EndpointName=endpoint_name,
                                      Body=json.dumps({
                                          'inputs': texts,
                                          'parameters': {
                                              'min_length': min_length
                                          }
                                      }),
                                      ContentType='application/json'
                                      )
        response_text = json.loads(response['Body'].read().decode())
        for texts in response_text:
            summary = texts['summary_text']
        return summary
    except Exception:
        st.error('Please provide correct access key')


radio = st.sidebar.radio('Summary size', ['Short', 'Long'])
if radio == 'Long':
    min_len = 100
else:
    min_len = 10

fulltext = st.text_area('Enter the article url that you want to summarize',
                        value="https://www.medpagetoday.com/infectiousdisease/vaccines/103058?trw=no",
                        help="Copy the entire url including 'https://'")

html_content = requests.get(fulltext)
soup = BeautifulSoup(html_content.text, "html.parser")
text = []

for content in soup.select('#js-main-content-region > p'):
    text.append(content.text)

stringText = ' '.join(map(str, text))
truncText = [' '.join(stringText.split()[:610])]

if st.button('Summarize'):
    with st.spinner():
        summary = predict(truncText, min_len)
        st.success('Done!')
        st.info(summary)
