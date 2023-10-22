#Libraries

from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

#Bibliotecas Necessárias
import folium 
import pandas as pd
import datetime
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static

#==========================================#
# =============FUNÇÕES===============
#==========================================#
def county_maps (df1):
    
    cols = ["City", 'Road_traffic_density', 'Delivery_location_latitude','Delivery_location_longitude']
    df_aux = (df1.loc[:, cols].groupby(["City", 'Road_traffic_density']).median().reset_index())

    map = folium.Map()

    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'],
                       location_info['Delivery_location_longitude']],
                       popup=location_info[["City", 'Road_traffic_density']] ).add_to(map)

    folium_static(map, width=1200, height=600)
        
    return None
    
def order_share_by_week(df1):
    # quantidade de pedidos por cada semana / quantidade de entregadores da semana
    cols1 = ['ID','week_of_year']
    cols2 = ['Delivery_person_ID',	'week_of_year']
    
    df_aux1 = df1.loc[:, cols1].groupby('week_of_year').count().reset_index()
    df_aux2 = df1.loc[:, cols2].groupby('week_of_year').nunique().reset_index()
    df_aux = pd.merge(df_aux1, df_aux2, how='inner')
    
    df_aux['Order_by_deliver'] = df_aux['ID']/df_aux['Delivery_person_ID']
    
    fig = px.line(df_aux,x='week_of_year', y='Order_by_deliver')

    return fig
    
def order_by_week (df1):
    
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    df_aux = df1.loc[:, ['ID','week_of_year']].groupby('week_of_year').count().reset_index()
    fig = px.line(df_aux,x='week_of_year', y='ID')
    
    return fig
    
def traffic_order_city(df1):
    cols =['ID', 'City', 'Road_traffic_density']
    
    df_aux = df1.loc[:, cols].groupby(['City','Road_traffic_density' ]).count().reset_index()
    fig = px.scatter(df_aux, x='City', y = 'Road_traffic_density', size='ID', color='City')

    return fig
    
def traffic_order_share (df1):        
    cols = ['ID','Road_traffic_density']
    
    df_aux = df1.loc[:, cols].groupby('Road_traffic_density').count().reset_index()
    df_aux['percent'] = (df_aux['ID']/df_aux['ID'].sum())*100
    fig = px.pie(df_aux, values= 'percent', names='Road_traffic_density')

    return fig
    
def order_metric(df1):
    cols = ['ID', 'Order_Date']
    
    df_aux = df1.loc[:, cols].groupby('Order_Date').count().reset_index() 
    fig = px.bar(df_aux, x = 'Order_Date', y = "ID")

    return fig
    
def clean_code(df1):
    '''Esta função tem a responsabilidade de limpar o dataframe

        Tipos de Limpeza:
        1. Remoção dos dados Nan
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços das variáveis de textos
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo (Remoção do texto da variável numérica)

        Input: DataFrame
        Output: DataFrame
    '''
    # Limpeza de Dados
    # Remover espaco da string
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Delivery_person_Age'] = df1.loc[:, 'Delivery_person_Age'].str.strip()
    df1.loc[:, 'Delivery_person_ID'] = df1.loc[:, 'Delivery_person_ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'multiple_deliveries'] = df1.loc[:, 'multiple_deliveries'].str.strip()
    
    # Excluir as linhas com a idade dos entregadores vazia
    linhas_nvazias = df1['Delivery_person_Age'] != 'NaN'
    df1 = df1.loc[linhas_nvazias, :]
    
    linhas_nvazias2 = df1['Weatherconditions'] != "conditions NaN"
    df1 = df1.loc[linhas_nvazias2, :]
    
    linhas_nvazias3 = df1['City'] != "NaN"
    df1 = df1.loc[linhas_nvazias3, :]
    
    linhas_nvazias4 = df1['multiple_deliveries'] != "NaN"
    df1 = df1.loc[linhas_nvazias4, :]
    
    linhas_nvazias5 = df1['Festival'] != "NaN"
    df1 = df1.loc[linhas_nvazias5, :]
    
    # Conversao de texto/categoria/string para numeros inteiros
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int )
    
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )
    
    # Conversao de texto/categoria/strings para numeros decimais
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype( float )
    
    # Conversao de texto para data
    df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format='%d-%m-%Y' )
    
    # Comando para remover o texto de números
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype( str )
    
    
    df1 ['Time_taken(min)'] = df1 ['Time_taken(min)'].apply( lambda x: x.split( '(min) ') [1])
    df1 ['Time_taken(min)'] = df1 ['Time_taken(min)'].astype(int)

    return df1

# --------------------------------- INÍCIO DA ESTRUTURA LÓGICA DO CÓDIGO -----------------------------------#
# ================================================================================================

#Import Dataset
df = pd.read_csv('dataset/train.csv')

#Limpando os dados
df1 = clean_code(df)


#==========================================#
# =============BARRA LATERAL===============
#==========================================#
st.header('Marketplace - Visão Cliente')

image = Image.open('logo.jpg')
st.sidebar.image(image,width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown('''---''')

st.sidebar.markdown('## Selecione uma data limite')

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value = datetime.datetime(2022,4,13),
    min_value = datetime.datetime(2022, 2, 11),
    max_value = datetime.datetime(2022, 4, 6),
    format='DD-MM-YYYY'
)

traffic_options = st.sidebar.multiselect (
    ' Selecione as condições de trânsito', 
    ['Low', 'Medium', 'High', 'Jam'],
    default= ['Low', 'Medium', 'High', 'Jam']
)

st.sidebar.markdown('''---''')
st.sidebar.markdown('#### Powered by Comunidade DS')

#Filtro de Data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas,:]

#Filtro de Trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas,:]

#==========================================#
# ========== LAYOUT NO STREAMLIT ===========
#==========================================#

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        st.markdown('# Orders by Day')
        fig = order_metric(df1)
        st.plotly_chart (fig, use_container_width=True)
            
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('# Traffic Order Share')
            fig = traffic_order_share (df1)
            st.plotly_chart (fig, use_container_width=True)

        with col2:
            st.markdown('# Traffic Order City')
            fig = traffic_order_city(df1)
            st.plotly_chart (fig, use_container_width=True)

with tab2:
    with st.container():
        st.markdown('# Order by Week')
        fig = order_by_week (df1)
        st.plotly_chart (fig, use_container_width=True)
        
    
    with st.container():
        st.markdown('# Order Share by Week')
        fig = order_share_by_week(df1)
        st.plotly_chart (fig, use_container_width=True)

with tab3:
    st.markdown('# County Maps')
    county_maps (df1)
    
    
    






