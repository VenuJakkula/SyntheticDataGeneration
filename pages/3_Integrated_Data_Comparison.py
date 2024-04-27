import streamlit as st
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from scipy.stats import ks_2samp
from scipy.stats import chisquare
import os
import glob
st.set_page_config(layout="wide")

st.header("Comparison of the Integrated Data")

df = pd.read_csv("automate/cleaned_Data.csv")
# df = pd.read_csv("syntheticGeneratedData.txt",sep=",")
orig_df = pd.read_csv("cleaned_OriginalData.csv")

fig,ax = plt.subplots(nrows=1,ncols=2,figsize=(20,7))
st.write("Generated Data shape is ",df.shape,df)
cont_cols = ["pktcount","bytecount","dur","flows","tot_kbps","label"]

with st.expander("Statistics of the data"):
    col1, _,col2 = st.columns([2,0.2,2])
    col1.write("Original Data")
    col1.write(orig_df.describe())
    col2.write("Generated Data")
    col2.write(df.describe())
    

with st.expander("Correlation map of original and synthetic data"):
    col_corr = st.multiselect("Select multiple columns for correlation",options=df.columns,
                              default=df.columns[0])
    # st.write(col_corr)
    sns.heatmap(orig_df[col_corr].corr(),annot=True,ax=ax[0]).set_title("Original Data")
    sns.heatmap(df[col_corr].corr(),annot=True,ax=ax[1]).set_title("Synthetic Data")
    st.pyplot(fig)

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

from scipy.stats import ttest_ind
from scipy.stats import f_oneway
with st.expander("Distribution plot of specific column"):
    column_selected = st.selectbox("Select a column",['dt', 'switch', 'pktcount', 'bytecount', 'dur',
       'dur_nsec', 'tot_dur', 'flows', 'packetins', 'pktperflow',
       'byteperflow', 'pktrate', 'Pairflow', 'port_no', 'tx_bytes',
       'rx_bytes', 'tx_kbps', 'rx_kbps', 'tot_kbps'])
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