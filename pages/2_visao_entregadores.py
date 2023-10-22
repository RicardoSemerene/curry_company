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
def top_delivers (df1,top_asc):
        df_aux = ((df1.loc[:,['Time_taken(min)','Delivery_person_ID', 'City']  ]
                      .groupby(['City', 'Delivery_person_ID'])
                      .mean()
                      .sort_values(['City', 'Time_taken(min)'], ascending=top_asc))
                      .reset_index())

        df_aux1 = df_aux.loc[df_aux['City'] == 'Metropolitian', :].head(10)
        df_aux2 = df_aux.loc[df_aux['City'] == 'Urban', :].head(10)
        df_aux3 = df_aux.loc[df_aux['City'] == 'Semi-Urban', :].head(10)

        df3 = pd.concat([df_aux1, df_aux2, df_aux3]).reset_index()

        df6 = pd.merge(df3, df4, how='inner').sort_values('Time_taken(min)' ).reset_index()
        df6 = df6.drop(['level_0', 'index'],axis=1)	

        return df6
    
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

#Import Dataset
df = pd.read_csv('dataset/train.csv')

df1 = clean_code(df)

#==========================================#
# =============BARRA LATERAL===============
#==========================================#
st.header('Marketplace - Visão Entregadores')

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

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title('Overall Metrics')

        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            # A maior idade dos entregadores
            idade_maxima = df1.loc[: , 'Delivery_person_Age'].max()
            col1.metric('Idade Máxima',idade_maxima)
            
        with col2:
            #A menor idade dos entregadores
            idade_minima = df1.loc[: , 'Delivery_person_Age'].min()
            col2.metric('Idade Mínima',idade_minima)
            
        with col3:
            #a melhor condição de veículos
            melhor_condicao = df1.loc[: , 'Vehicle_condition'].max() 
            col3.metric('Melhor Condição',melhor_condicao)

        
        with col4:
           #a pior condição de veículos
           pior_condicao = df1.loc[: , 'Vehicle_condition'].min() 
           col4.metric('Pior Condição',pior_condicao)

    with st.container():
        st.markdown('''---''')
        st.title('Avaliações')
        
        col1,col2 = st.columns(2)
        
        with col1:
            st.markdown('##### Avaliação Média por entregador')
            cols = ['Delivery_person_ID', 'Delivery_person_Ratings']

            df_avg_ratings_per_deliver = (df1.loc[:, cols]
                                              .groupby('Delivery_person_ID')
                                              .mean()
                                              .reset_index())
            st.dataframe(df_avg_ratings_per_deliver)
            
        with col2:
            st.markdown('##### Avaliação Média por tipo de tráfego')
            cols = ['Delivery_person_Ratings','Road_traffic_density' ]

            df_avg_ratings_by_traffic = (df1.loc[:, cols]
                                            .groupby('Road_traffic_density')
                                            .agg({'Delivery_person_Ratings':['mean', 'std']})
                                            .reset_index())
            
            df_avg_ratings_by_traffic.columns = ['Road_traffic_density','Delivery_Mean', 'Delivery_std']
            df_avg_ratings_by_traffic.sort_values('Delivery_Mean').reset_index()
            st.dataframe(df_avg_ratings_by_traffic)
            
            
            st.markdown('##### Avaliação Média por tipo de clima')
            cols = ['Weatherconditions', 'Delivery_person_Ratings']

            df_avg_ratings_by_traffic = (df1.loc[:, cols]
                                         .groupby('Weatherconditions')
                                         .agg({'Delivery_person_Ratings':['mean', 'std']})
                                         .reset_index())
            
            df_avg_ratings_by_traffic.columns = ['Weatherconditions','Delivery_Mean', 'Delivery_std']
            df_avg_ratings_by_traffic.sort_values('Delivery_Mean').reset_index()

            st.dataframe(df_avg_ratings_by_traffic)

    with st.container():
        st.markdown('''---''')
        st.title('Velocidade de Entrega')

        col1,col2 = st.columns(2)
        #Quantidade de Entregas por Entregador
        df4 = (df1.loc[:,['ID', 'Delivery_person_ID']]
                   .groupby('Delivery_person_ID')
                   .count().sort_values('ID', ascending=False)
                   .reset_index())       

        with col1:
            st.markdown('##### Os 10 entregadores mais rápidos')
            df6 = top_delivers (df1, top_asc=True)
            st.dataframe(df6)
            
        with col2:
            st.markdown('##### Os 10 entregadores mais lentos')
            df6 = top_delivers (df1, top_asc=False)
            st.dataframe(df6)
