#Libraries

from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

#Bibliotecas Necessárias
import folium 
import numpy as np
import pandas as pd
import datetime
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static

#==========================================#
# =============FUNÇÕES===============
#==========================================#
def avg_time_city_traffic (df1):

    cols = ['Time_taken(min)', 'City', 'Road_traffic_density']

    time_avg_type_traffic = (df1.loc[:, cols]
                                    .groupby(['City', 'Road_traffic_density'])
                                    .agg({'Time_taken(min)': ['mean', 'std']})
                                    .reset_index())
        
    time_avg_type_traffic.columns = ['City','Road_traffic_density', 'Time_taken_mean', 'Time_taken_std']

    fig = px.sunburst(time_avg_type_traffic, path=['City','Road_traffic_density'], values='Time_taken_mean', color='Time_taken_std', color_continuous_scale='RdBu', color_continuous_midpoint=np.average( time_avg_type_traffic['Time_taken_std']))

    return fig

def avg_std_time_graph (df1):

    time_avg = df1.loc[:, ['Time_taken(min)', 'City' ]].groupby('City').agg({'Time_taken(min)': ['mean', 'std']}).reset_index()
    time_avg.columns = ['City','Time_taken_mean', 'Time_taken_std']

    fig = go.Figure()
    fig.add_trace( go.Bar (name='Control', x=time_avg['City'], y = time_avg['Time_taken_mean'],error_y =dict(type='data', array= time_avg['Time_taken_std'])))
    fig.update_layout(barmode='group')

    return fig
  
def avg_std_time_delivery_festival(df1, x, op):

    '''Esta função calcula o tempo médio e o desvio padrão de entrega em festivais
        Parâmetros:
        Input: 
            - df: Dataframe com os dados necessários para o cálculo
            - op: Tipo de operação que precisa ser calculada
                    'Time_taken_mean': calcula o tempo médio
                    'Time_taken_std': calcula o desvio padrão do tempo

            - x: 0: Sem festival
                 1: Com festival

        Output: dataframe com 2 colunas e 1 linha
    '''
    time_festival = (df1.loc[:, ['Time_taken(min)', 'Festival']]
                     .groupby(['Festival'])
                     .agg({'Time_taken(min)': ['mean', 'std']})
                     .reset_index())
    time_festival.columns = ['Festival', 'Time_taken_mean', 'Time_taken_std']
    time_festival = np.round(time_festival.loc[x:x,op],2)

    return time_festival
    
def distance(df1):
            
   cols = ['Restaurant_latitude',	'Restaurant_longitude',	'Delivery_location_latitude',	'Delivery_location_longitude']

   df1['Distance'] = df1.loc[:, cols].apply(lambda x: haversine
( (x['Restaurant_latitude'],x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])),axis=1)
    
   avg_distance = np.round(df1['Distance'].mean(),2)

   return avg_distance

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
#----------------------------------------------------------------------
#Import Dataset
df = pd.read_csv('dataset/train.csv')

df1 = clean_code(df)



#==========================================#
# =============BARRA LATERAL===============
#==========================================#
st.header('Marketplace - Visão Restaurantes')

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

with st.container():
    st.title('Overal Metrics')

    col1, col2, col3, col4, col5, col6 = st.columns (6)
    with col1:
        delivery_unique = df1['Delivery_person_ID'].nunique()
        col1.metric('Entregadores', delivery_unique)
    
    with col2:
        avg_distance = distance(df1)
        col2.metric('A distância média', avg_distance)
           
    with col3:
        time_festival = avg_std_time_delivery_festival(df1,1, 'Time_taken_mean')
        col3.metric("Tempo Festival", time_festival)

    with col4:
        time_festival = avg_std_time_delivery_festival(df1,1, 'Time_taken_std')
        col4.metric("STD Festival", time_festival)

    with col5:
        time_festival = avg_std_time_delivery_festival(df1,0, 'Time_taken_mean')
        col5.metric("Tempo Festival", time_festival)

    with col6:
        time_festival = avg_std_time_delivery_festival(df1,0, 'Time_taken_std')
        col6.metric("STD Festival", time_festival)

with st.container():
    st.markdown('''___''')
    st.markdown('### Distribuição do tempo por cidade e tipo de tráfego')
    fig = avg_time_city_traffic (df1)
    st.plotly_chart(fig)
    
with st.container():
    st.markdown('''___''')
    st.markdown('### Distribuição do tempo e seu desvio padrão por cidade')
    fig = avg_std_time_graph (df1)
    st.plotly_chart(fig)
                               
with st.container():
    st.markdown('''___''')
    st.markdown('### Distribuição da distância por cidade')

    cols = ['Restaurant_latitude',	'Restaurant_longitude',	'Delivery_location_latitude',	'Delivery_location_longitude']

    df1['Distance'] = df1.loc[:, cols].apply(lambda x: haversine( (x['Restaurant_latitude'],x['Restaurant_longitude']),(x['Delivery_location_latitude'], x['Delivery_location_longitude'])),axis=1)
    
    avg_distance = df1.loc[:,['Distance', 'City']].groupby('City').mean().reset_index()

    fig = px.bar(avg_distance, x = 'City', y = "Distance")
    st.plotly_chart(fig)





