import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import requests
from io import BytesIO

st.set_page_config(layout="wide")

st.title("MÉTRICAS - SUPRIMENTOS - AGIR")

# Raw URL of the file on GitHub
raw_github_url = 'https://raw.githubusercontent.com/your_username/your_repository/main/ANALISE-COMPRAS.xlsx'

# Fetch the content of the Excel file from GitHub
response = requests.get(raw_github_url)
content = response.content

# Read the Excel content as a pandas DataFrame with the specified engine
df = pd.read_excel(BytesIO(content), usecols=list(range(34)), engine='openpyxl')  # Specify 'openpyxl' as the engine
df = df.drop_duplicates()

# Convert "DATA OC" column to date
df["DATA OC"] = pd.to_datetime(df["DATA OC"].astype(str), format='%d/%m/%Y às %H:%M', errors='coerce')

# Filter out rows where the date could not be parsed (NaT)
df = df.dropna(subset=["DATA OC"])

# Filter rows where "STATUS OC" column has value "ATIVA"
df = df[df["STATUS OC"] == "ATIVA"]

# Extract year, month, and quarter
df["Year"] = df["DATA OC"].dt.year
df["Month"] = df["DATA OC"].dt.month
df["Quarter"] = df["DATA OC"].dt.quarter
df["Semester"] = np.where(df["DATA OC"].dt.month.isin([1, 2, 3, 4, 5, 6]), 1, 2)

# Create a "Year-Quarter" column
df["Year-Quarter"] = df["Year"].astype(str) + "-T" + df["Quarter"].astype(str)

# If you want to create a "Year-Month" column, you can use the following line
df["Year-Month"] = df["DATA OC"].dt.strftime("%Y-%m")

# Create a "Year-Semester" column
df["Year-Semester"] = df["Year"].astype(str) + "-S" + df["Semester"].astype(str)

# Sort the unique values in ascending order
unique_year_month = sorted(df["Year-Month"].unique())
unique_year_quarter = sorted(df["Year-Quarter"].unique())
unique_year_semester = sorted(df["Year-Semester"].unique())
unique_year = sorted(df["Year"].unique())

# Add "All" as an option for both filters
unique_year_month.insert(0, "Todos")
unique_year_quarter.insert(0, "Todos")
unique_year_semester.insert(0, "Todos")
unique_year.insert(0, "Todos")

# Create a sidebar for selecting filters
month = st.sidebar.selectbox("Mês", unique_year_month)
quarter = st.sidebar.selectbox("Trimestre", unique_year_quarter)
semester = st.sidebar.selectbox("Semestre", unique_year_semester)
year = st.sidebar.selectbox("Ano", unique_year)

# Apply filters to the dataframe
filtered_df = df.copy()

if month != "Todos":
    filtered_df = filtered_df[filtered_df["Year-Month"] == month]

if quarter != "Todos":
    filtered_df = filtered_df[filtered_df["Year-Quarter"] == quarter]

if semester != "Todos":
    filtered_df = filtered_df[filtered_df["Year-Semester"] == semester]

if year != "Todos":
    filtered_df = filtered_df[filtered_df["Year"] == year]

# Get unique values for MARCA and FORNECEDORES columns, handling potential NaN values
unique_marcas = filtered_df["MARCA"].dropna().astype(str).unique()
unique_fornecedores = filtered_df["FORNECEDOR"].dropna().astype(str).unique()

# Add "Todos" as an option for both new filters
unique_marcas = ['Todos'] + sorted(unique_marcas)
unique_fornecedores = ['Todos'] + sorted(unique_fornecedores)

# Create new sidebar selectboxes for MARCA and FORNECEDORES
marca_selected = st.sidebar.selectbox("Marcas", unique_marcas)
fornecedor_selected = st.sidebar.selectbox("Fornecedores", unique_fornecedores)

# Apply filters to the dataframe based on new selections
if marca_selected != "Todos":
    filtered_df = filtered_df[filtered_df["MARCA"] == marca_selected]

if fornecedor_selected != "Todos":
    filtered_df = filtered_df[filtered_df["FORNECEDOR"] == fornecedor_selected]

# Display the filtered DataFrame
st.write("Dados Selecionados:")
st.dataframe(filtered_df)

col1, col2, col3 = st.columns(3)
col4, col5 = st.columns(2)
col6, col7 = st.columns(2)
col8 = st.columns(1)

# Remove commas and periods from the "VALOR TOTAL (R$)" column
filtered_df["VALOR TOTAL (R$)"] = filtered_df["VALOR TOTAL (R$)"].str.replace('.', '')
filtered_df["VALOR TOTAL (R$)"] = filtered_df["VALOR TOTAL (R$)"].str.replace(',', '.')

# Convert the column to numeric format
filtered_df["VALOR TOTAL (R$)"] = pd.to_numeric(filtered_df["VALOR TOTAL (R$)"])

# Calculate the sum of the "VALOR TOTAL (R$)" column
sum_valor_total = filtered_df["VALOR TOTAL (R$)"].sum()

# Format the sum to display as Brazilian Real currency
formatted_sum = "R${:,.2f}".format(sum_valor_total)

# Display the sum of "VALOR TOTAL (R$)" in a metric display
col1.subheader('Total Valor 💰')
col1.metric(label='Valor Total (R$)', value=formatted_sum, delta=None)

# Count the number of unique values in the "MARCA" column
unique_marcas_count = filtered_df["MARCA"].nunique()

# Display the count of unique "MARCA" values in a metric display
col2.subheader('Quantidade de Marcas 🚀')
col2.metric(label='Número de Marcas', value=unique_marcas_count, delta=None)

# Count the number of unique values in the "FORNECEDOR" column
unique_fornecedores_count = filtered_df["FORNECEDOR"].nunique()

# Display the count of unique "FORNECEDOR" values in a metric display
col3.subheader('Quantidade de Fornecedores 🛒')
col3.metric(label='Número de Fornecedores', value=unique_fornecedores_count, delta=None)

# Group by "MARCA" and calculate the sum of "VALOR TOTAL (R$)" for each
marca_sum = filtered_df.groupby("MARCA")["VALOR TOTAL (R$)"].sum().reset_index()

# Sort values by the sum of "VALOR TOTAL (R$)" in descending order and get the top 10
top_10_marcas = marca_sum.sort_values(by="VALOR TOTAL (R$)", ascending=False).head(10)

# Create a bar chart using Plotly Express
fig = px.bar(top_10_marcas, x="MARCA", y="VALOR TOTAL (R$)", title="Top 10 Marcas por Valor Total",
             labels={"MARCA": "Marca", "VALOR TOTAL (R$)": "Valor Total (R$)"})

# Customize layout if needed
fig.update_layout(xaxis_title='Marca', yaxis_title='Valor Total (R$)')

# Display the bar chart in col4
col4.plotly_chart(fig)

# Group by "FORNECEDOR" and calculate the sum of "VALOR TOTAL (R$)" for each
fornecedor_sum = filtered_df.groupby("FORNECEDOR")["VALOR TOTAL (R$)"].sum().reset_index()

# Sort values by the sum of "VALOR TOTAL (R$)" in descending order and get the top 10
top_10_fornecedores = fornecedor_sum.sort_values(by="VALOR TOTAL (R$)", ascending=False).head(10)

# Create a bar chart using Plotly Express for FORNECEDORES
fig_fornecedores = px.bar(top_10_fornecedores, x="FORNECEDOR", y="VALOR TOTAL (R$)", title="Top 10 Fornecedores por Valor Total",
                           labels={"FORNECEDOR": "Fornecedor", "VALOR TOTAL (R$)": "Valor Total (R$)"})

# Customize layout if needed
fig_fornecedores.update_layout(xaxis_title='Fornecedor', yaxis_title='Valor Total (R$)')

# Display the bar chart in col5
col5.plotly_chart(fig_fornecedores)

# Count occurrences of each MARCA
marca_counts = filtered_df['MARCA'].value_counts().reset_index()
marca_counts.columns = ['MARCA', 'Count']

# Get top 10 MARCAS by count
top_10_marcas_count = marca_counts.head(10)

# Create a bar chart for top 10 MARCAS by count
fig_marcas_count = px.bar(top_10_marcas_count, x="MARCA", y="Count", title="Top 10 Marcas por Quantidade de itens",
                          labels={"MARCA": "Marca", "Count": "Contagem"})

# Customize layout if needed
fig_marcas_count.update_layout(xaxis_title='Marca', yaxis_title='Qtd de itens')

# Display the bar chart in col6
col6.plotly_chart(fig_marcas_count)


# Count occurrences of each FORNECEDOR
fornecedor_counts = filtered_df['FORNECEDOR'].value_counts().reset_index()
fornecedor_counts.columns = ['FORNECEDOR', 'Count']

# Get top 10 FORNECEDORES by count
top_10_fornecedores_count = fornecedor_counts.head(10)

# Create a bar chart for top 10 FORNECEDORES by count
fig_fornecedores_count = px.bar(top_10_fornecedores_count, x="FORNECEDOR", y="Count", title="Top 10 Fornecedores por Quantidade de itens",
                                labels={"FORNECEDOR": "Fornecedor", "Count": "Contagem"})

# Customize layout if needed
fig_fornecedores_count.update_layout(xaxis_title='Fornecedor', yaxis_title='Qtd de itens')

# Display the bar chart in col7
col7.plotly_chart(fig_fornecedores_count)

# Group by Year-Month and calculate the sum of "VALOR TOTAL (R$)" for each period
valor_total_over_time = filtered_df.groupby("Year-Month")["VALOR TOTAL (R$)"].sum().reset_index()

# Create a line chart using Plotly Express for VALOR TOTAL (R$) over time
fig_valor_over_time = px.line(valor_total_over_time, x="Year-Month", y="VALOR TOTAL (R$)",
                              title="Valor Total (R$) ao Longo do Tempo",
                              labels={"Year-Month": "Ano-Mês", "VALOR TOTAL (R$)": "Valor Total (R$)"})

# Customize layout if needed
fig_valor_over_time.update_layout(xaxis_title='Ano-Mês', yaxis_title='Valor Total (R$)')

# Display the line chart in col8 (assuming col8 is the third column in the row)
st.plotly_chart(fig_valor_over_time)


# Count the number of unique MARCAS for each Year-Month
marcas_over_time = filtered_df.groupby("Year-Month")["MARCA"].nunique().reset_index()

# Create a line chart for the number of unique MARCAS over time
fig_marcas_over_time = px.line(marcas_over_time, x="Year-Month", y="MARCA",
                               title="Número de Marcas ao Longo do Tempo",
                               labels={"Year-Month": "Ano-Mês", "MARCA": "Número de Marcas"})

# Customize layout if needed
fig_marcas_over_time.update_layout(xaxis_title='Ano-Mês', yaxis_title='Número de Marcas')

# Display the line chart in col9 (or the desired column)
st.plotly_chart(fig_marcas_over_time)



# Count the number of unique FORNECEDORES for each Year-Month
fornecedores_over_time = filtered_df.groupby("Year-Month")["FORNECEDOR"].nunique().reset_index()

# Create a line chart for the number of unique FORNECEDORES over time
fig_fornecedores_over_time = px.line(fornecedores_over_time, x="Year-Month", y="FORNECEDOR",
                                     title="Número de Fornecedores ao Longo do Tempo",
                                     labels={"Year-Month": "Ano-Mês", "FORNECEDOR": "Número de Fornecedores"})

# Customize layout if needed
fig_fornecedores_over_time.update_layout(xaxis_title='Ano-Mês', yaxis_title='Número de Fornecedores')

# Display the line chart in col10 (or the desired column)
st.plotly_chart(fig_fornecedores_over_time)




