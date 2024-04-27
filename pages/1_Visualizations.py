import streamlit as st
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from scipy.stats import ks_2samp
from scipy.stats import chisquare
from scipy.stats import ttest_ind
from scipy.stats import f_oneway
import os
import glob
st.set_page_config(layout="wide")

st.header("Visualization of the Data")

prompt_text = open("logs/prompt.txt","r").read()
prompts = prompt_text.split("\n\n")
selectedPrompt = st.selectbox("Select a Prompt",prompts)
datetimeSelected = selectedPrompt.split("\n")[0].strip()
fileName = glob.glob("logs/data_at_"+datetimeSelected+"*.txt")
df = pd.read_csv(fileName[0])
# df = pd.read_csv("syntheticGeneratedData.txt",sep=",")
orig_df = pd.read_csv("cleaned_OriginalData.csv")

fig,ax = plt.subplots(nrows=1,ncols=2,figsize=(20,7))
st.write("shape is ",df.shape,df)
cont_cols = ["pktcount","bytecount","dur","flows","tot_kbps","label"]

with st.expander("Statistics of the data"):
    col1, _,col2 = st.columns([2,0.2,2])
    col1.write("Generated Data")
    col1.write(df.describe())
    col2.write("Original Data")
    col2.write(orig_df.describe())
try:
    with st.expander("Correlation map of original and synthetic data"):
        col_corr = st.multiselect("Select multiple columns for correlation",options=df.columns,
                                default=df.columns[0])
        # st.write(col_corr)
        sns.heatmap(df[col_corr].corr(),annot=True,ax=ax[0]).set_title("Synthetic Data")
        sns.heatmap(orig_df[col_corr].corr(),annot=True,ax=ax[1]).set_title("Original Data")
        st.pyplot(fig)
except:
    st.error("Unable to plot Correlation map",icon="🚨")

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
    st.error("Unable to plot Label Distribution",icon="🚨")

try:
    with st.expander("Distribution plot of specific column"):
        column_selected = st.selectbox("Select a column",["pktcount","bytecount","dur","flows","tot_kbps"])
        # plotting the distributions
        fig2,ax2 = plt.subplots(figsize=(20,7))
        sns.distplot(orig_df[column_selected], label='Original',ax=ax2)
        sns.distplot(df[column_selected], label='Synthesized',ax=ax2)
        plt.legend()
        st.pyplot(fig2)
        # checking if the distributions are same or not
        ks_out = ks_2samp(orig_df[column_selected], df[column_selected])
        # stats = pd.DataFrame([ks_out.statistic,ks_out.pvalue,ks_out.statistic_location,ks_out.statistic_sign]).T
        # stats.columns = ["statistic","pvalue","statistic_location","statistic_sign"]
        st.write("Two-sample Kolmogorov-Smirnov test: ")
        st.write(str(ks_out))
        stat, p_value = ttest_ind(orig_df[column_selected], df[column_selected])
        st.write(f"t-test: statistic={stat:.4f}, p-value={p_value:.4f}")
        st.write("F-test",f_oneway(orig_df[column_selected], df[column_selected]))
        st.write("chisquare",chisquare(df[column_selected]))
except:
    st.error("Unable to plot Distribution plot",icon="🚨")


src = "logs/data_at_"+datetimeSelected+".txt"
dst = "logs/data_at_"+datetimeSelected+"_verified.txt"

if "verified" not in fileName[0]:
    if st.button("Verify and mark data as correct"):
        with st.spinner("Marking the Data as Verified..."):
            os.rename(src,dst)
else:
    st.write(fileName[0])
# with st.expander("chisquare for the target variable"):

# with st.expander("Distribution of `bytecount` column"):
#     # plotting the distributions
#     fig2,ax2 = plt.subplots(figsize=(20,7))
#     sns.distplot(orig_df['bytecount'], label='Original',ax=ax2)
#     sns.distplot(df['bytecount'], label='Synthesized',ax=ax2)
#     plt.legend()
#     st.pyplot(fig2)
#     # checking if the distributions are same or not
#     st.write(ks_2samp(orig_df['bytecount'], df['bytecount']))

# with st.expander("Distribution of `bytecount` column"):
#     # plotting the distributions
#     fig2,ax2 = plt.subplots(figsize=(20,7))
#     sns.distplot(orig_df['bytecount'], label='Original',ax=ax2)
#     sns.distplot(df['bytecount'], label='Synthesized',ax=ax2)
#     plt.legend()
#     st.pyplot(fig2)
#     # checking if the distributions are same or not
#     st.write(ks_2samp(orig_df['bytecount'], df['bytecount']))