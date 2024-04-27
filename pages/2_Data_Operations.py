import streamlit as st
import glob
import pandas as pd
import os
st.set_page_config(layout="wide")

st.header("Data write/Delete operations")
datasets = glob.glob("logs/data_at_2023_*verified.txt")
selectedDate = st.selectbox("Select",datasets)
try:
    tempDf = pd.read_csv(selectedDate,sep=",")
except:
    tempDf=pd.DataFrame(["Temp is clean"])
synth_Df = pd.read_csv("syntheticGeneratedData.txt",sep=",")

col1, _,col2 = st.columns([2,0.4,2])
with col1:
    st.write("Data Generated with shape ",tempDf.shape,tempDf)

with col2:
    st.write("Existing Data with shape ",synth_Df.shape,synth_Df)

if st.button("Save the data!"):
    with st.spinner("Saving the Data....."):
        old_shape = synth_Df.shape
        concatDf = pd.concat([synth_Df,tempDf],ignore_index=True)
        new_shape = concatDf.shape
        st.write("Data saved and its shape is now changed from {} to {}".format(old_shape,new_shape))
        st.write(concatDf)
        concatDf.to_csv("C:/Users/2205854/OneDrive - TCS COM PROD/WorkBench/SyntheticDataGeneration/syntheticGeneratedData.txt",index=False)
        with open("temp_syntheticGeneratedData.txt","w") as tempF:
            tempF.write("")
        os.rename(selectedDate,selectedDate[:-4]+"_added.txt")