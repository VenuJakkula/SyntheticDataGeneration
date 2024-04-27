import streamlit as st
import openai
import os
import pandas as pd
import datetime
import seaborn as sns
from matplotlib import pyplot as plt
from scipy.stats import ks_2samp
import random  
st.set_page_config(layout="wide")

st.header("Synthetic Data Generation")
#Open AI Credentials
openai.api_type="azure"
openai.api_base = "https://dotdotdot.openai.azure.com/"
openai.api_key = "15343426346"
openai.api_version="2022-12-01"
orig_df = pd.read_csv("outlier_removed_data.csv")
col1 , col2 = st.columns([4,5])

n_rows = col1.text_input("No.of rows to consider from original data","10")

def distribution(df,n_rows=10):
  # df = df.drop(["src","dst"],axis=1)
  class_0 = df[df.label == 0]
  class_1 = df[df.label == 1]
  class0_indices = random.sample(range(len(class_0)), n_rows//2)  
  class1_indices = random.sample(range(len(class_1)), n_rows//2)
  class0Df = class_0.iloc[class0_indices] 
  class1Df = class_1.iloc[class1_indices]
  all_rows = ""
  # ",".join(df.columns.values)+"\n"
  for i,row in class0Df.iterrows():
    all_rows += ",".join([str(i) for i in row.values])+"\n"
  for i,row in class1Df.iterrows():
    all_rows += ",".join([str(i) for i in row.values])+"\n"
  return all_rows

st.code(",".join(orig_df.columns.values))
st.write(f"{n_rows} Examples from Original Data")
co = st.code(distribution(orig_df,int(n_rows)))

def getStats(df):
  tempDf = pd.DataFrame(df.drop(["src","dst","label"],axis=1).describe()).reset_index()
  all_rows = ",".join(tempDf.columns)+"\n"
  for i,row in tempDf.iterrows():
    all_rows += ",".join([str(i).split(".")[0] for i in row.values])+"\n"
  return all_rows[5:]

st.write("Stats from Original Data")
st.code(getStats(orig_df))
max_token = int(st.text_input("Enter max_token for chatGPT","1200"))
triple_quotes = '"""'
col_line = ",".join(orig_df.columns)
stats = getStats(orig_df)
prompt_dynamic = "consider the columns in triple backticks ```"+col_line+"```\nand its statistics in triple quotes\n"+triple_quotes+stats+triple_quotes+"\nand consider the following examples in triple quotes\n"+triple_quotes+distribution(orig_df,10)+triple_quotes+"\nGenerate a 10000 rows of a data in csv format, label including 0 and 1 classes with equal distribution, consider the max token as 4000 - input tokens after calculation."
        
prompt = st.text_area("Enter Prompt for chatGPT",value=prompt_dynamic,height=2)
def chatGPT_Response(user_prompt,max_token):
  max_token = max_token 
  Modified_response = openai.Completion.create(engine ="TD3",prompt=user_prompt,
                                               max_tokens=max_token,temperature=0.5)
  return Modified_response.choices[0].text.lstrip(), Modified_response
if st.button("Get Response"):
  with st.spinner("Processing Results....."):
    with st.expander("Prompt is: "):
      st.write(prompt)
    current_date_time = datetime.datetime.now()
    current_date_time = current_date_time.strftime("%Y_%m_%d_%H_%M_%S")
    with open("logs/prompt.txt","a") as pmt:
      pmt.write(str(current_date_time)+"\n"+prompt+"\n\n")
    output,res = chatGPT_Response(prompt,max_token)
    with st.expander("Tokens Count:"):
      st.write("Input token count is:{}, output token count is {}".format(res['usage']['prompt_tokens'],
                                                                          res['usage']['completion_tokens']))
    with st.expander("ChatGPT Output: "):
      st.text_area("",output,height=200)
    with open("logs/data_at_"+str(current_date_time)+".txt","w") as dataf:
      dataf.write(output)
    with open("temp_syntheticGeneratedData.txt","w") as tempf:
      tempf.write(output)
    st.write("Data generated and it shape is: ",pd.read_csv("temp_syntheticGeneratedData.txt",sep=",").shape)

    df = pd.read_csv("temp_syntheticGeneratedData.txt",sep=",")

    try:
      fig,ax = plt.subplots(nrows=1,ncols=2,figsize=(20,7))
      with st.expander("Correlation map of original and synthetic data"):
          cont_cols = ["pktcount","bytecount","dur","flows","tot_kbps","label"]
          sns.heatmap(df[cont_cols].corr(),annot=True,ax=ax[0]).set_title("Synthetic Data")
          sns.heatmap(orig_df[cont_cols].corr(),annot=True,ax=ax[1]).set_title("Original Data")
          st.pyplot(fig)
    except:
      st.error("Unable to plot Correlation Map",icon="🚨")

    try:
      with st.expander("Label Distribution"):
          labelCompDf = pd.DataFrame()
          labelCompDf["original_labels_count"] = orig_df.label.value_counts()
          labelCompDf["original_labels%"] = orig_df.label.value_counts(normalize=True)
          labelCompDf["sythentic_labels_count"] = df.label.value_counts()
          labelCompDf["sythentic_labels%"] = df.label.value_counts(normalize=True)
          st.write(labelCompDf)
          labels = '0', '1'
          explode = (0, 0.1) 
          fig1, ax1 = plt.subplots(nrows=1,ncols=2,figsize=(20,7))
          ax1[0].pie(labelCompDf["original_labels_count"].values, explode=explode, labels=labels, autopct='%1.1f%%',
                  shadow=True, startangle=90)
          ax1[0].set_title("Original Data Labels")
          ax1[1].pie(labelCompDf["sythentic_labels_count"].values, explode=explode, labels=labels, autopct='%1.1f%%',
                  shadow=True, startangle=90)
          ax1[1].set_title("Synthetic Data Labels")
          st.pyplot(fig1)
    except:
      st.error("Unable to Label Distribution",icon="🚨")

    try:
      with st.expander("Distribution plot of specific column"):
          # column_selected = st.selectbox("Select a column",["pktcount","bytecount","dur","flows","tot_kbps"])
          for column_selected in ["pktcount","bytecount","dur","flows","tot_kbps"]:
            fig2,ax2 = plt.subplots(figsize=(20,7))
            sns.distplot(orig_df[column_selected], label='Original',ax=ax2)
            sns.distplot(df[column_selected], label='Synthesized',ax=ax2)
            plt.legend()
            plt.title(column_selected)
            st.pyplot(fig2)
    except:
      st.error("Unable to Distribution plot",icon="🚨")
      # plotting the distributions
      # fig2,ax2 = plt.subplots(figsize=(20,7))
      # sns.distplot(orig_df[column_selected], label='Original',ax=ax2)
      # sns.distplot(df[column_selected], label='Synthesized',ax=ax2)
      # plt.legend()
      # st.pyplot(fig2)
      # checking if the distributions are same or not
      # st.write(ks_2samp(orig_df[column_selected], df[column_selected]))