import pandas as pd 
import numpy as np
import calendar
import geopandas as gpd



############################# Funciones usadas en el primer script ############################# 

def verificar_base(df:pd.DataFrame) -> pd.DataFrame:
    """
    Valida y procesa una tabla de secuestros, generando agregados por municipio y departamento.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame de entrada que debe contener exactamente las columnas:
        ['FECHA HECHO', 'COD_DEPTO', 'DEPARTAMENTO',
         'COD_MUNI', 'MUNICIPIO', 'TIPO DELITO', 'CANTIDAD'].

    Returns
    -------
    secuestros_departamentos : pandas.DataFrame
        DataFrame agrupado por fecha y departamento, con las columnas:
        ['FECHA HECHO', 'COD_DEPTO', 'DEPARTAMENTO', 'N_SIMPLE', 'N_EXTORSIVO'].
    secuestros_municipios : pandas.DataFrame
        DataFrame agrupado por fecha, departamento y municipio, con las columnas:
        ['FECHA HECHO', 'COD_DEPTO', 'DEPARTAMENTO', 'COD_MUNI',
         'MUNICIPIO', 'N_SIMPLE', 'N_EXTORSIVO'].
    df1 : pandas.DataFrame
        Copia del DataFrame original, con:
        - Columna 'FECHA HECHO' convertida a datetime (coerce para formatos inválidos).
        - Columnas auxiliares 'N_SIMPLE' y 'N_EXTORSIVO' con conteos por tipo de secuestro.
    """

    df1 = df.copy()

    columnas = ['FECHA HECHO', 'COD_DEPTO', 'DEPARTAMENTO', 'COD_MUNI', 'MUNICIPIO',
       'TIPO DELITO', 'CANTIDAD']

    if not df1.columns.equals(pd.Index(columnas)):
        return 'Ingreso la base incorrecta'
    
    #Verificar y convertir la columna de fecha
    df1['FECHA HECHO'] = pd.to_datetime(df1['FECHA HECHO'],
        format='%d/%m/%Y',dayfirst=True,errors='coerce')
    
    # Verificar fechas invalidas
    invalid_dates = df1['FECHA HECHO'].isna().sum()
    print(f'Fechas inválidas: {invalid_dates}')

    # Dado que tenemos dos tipos de secuestro, separameslas para desagregar por tipo de secuestro 
    df1['N_SIMPLE'] = np.where(df1['TIPO DELITO'] == 'SECUESTRO SIMPLE',df1['CANTIDAD'],0)
    df1['N_EXTORSIVO'] = np.where(df1['TIPO DELITO'] == 'SECUESTRO EXTORSIVO',df1['CANTIDAD'],0)

    # Agrupemos la base por municipios 
    secuestros_municipios = (df1.groupby(['FECHA HECHO', 'COD_DEPTO', 'DEPARTAMENTO', 'COD_MUNI', 'MUNICIPIO'],
        as_index=False)[['N_SIMPLE', 'N_EXTORSIVO']].sum().sort_values(['MUNICIPIO', 'FECHA HECHO']))

    # Agrupemos la base por deartamentos 
    secuestros_departamentos = (df1.groupby(['FECHA HECHO', 'COD_DEPTO', 'DEPARTAMENTO'],
        as_index=False)[['N_SIMPLE', 'N_EXTORSIVO']].sum().sort_values(['DEPARTAMENTO', 'FECHA HECHO']))
    
    return secuestros_departamentos , secuestros_municipios , df1 


def crear_series_de_tiempo(f, df:pd.DataFrame) -> pd.DataFrame:
    """
    Genera series temporales agregadas de secuestros a nivel de municipio, departamento y nacional.

    Parameters
    ----------
    f : callable
        Función que recibe el DataFrame original y devuelve una tupla de tres elementos:
        (secuestros_departamentos, secuestros_municipios, df1), donde:
        - secuestros_departamentos: DataFrame agrupado por fecha y departamento
        - secuestros_municipios: DataFrame agrupado por fecha, departamento y municipio
        - df1: DataFrame procesado con fechas y contadores por tipo de secuestro
    df : pandas.DataFrame
        DataFrame original con las columnas procesadas por `f`.

    Returns
    -------
    municipios_mensual : pandas.DataFrame
        Panel mensual de secuestros por municipio, con columnas:
        ['MES', 'COD_DEPTO', 'DEPARTAMENTO', 'COD_MUNI', 'MUNICIPIO',
         'N_SIMPLE', 'N_EXTORSIVO', 'TOTAL'].
        El índice ‘MES’ corresponde al último día de cada mes (`freq='ME'`).
    departamentos_mensual : pandas.DataFrame
        Panel mensual de secuestros por departamento, con columnas:
        ['MES', 'COD_DEPTO', 'DEPARTAMENTO', 'N_SIMPLE', 'N_EXTORSIVO', 'TOTAL'].
    municipios_anual : pandas.DataFrame
        Panel anual de secuestros por municipio, con columnas:
        ['AÑO', 'COD_DEPTO', 'DEPARTAMENTO', 'COD_MUNI', 'MUNICIPIO',
         'N_SIMPLE', 'N_EXTORSIVO', 'TOTAL'].
        El índice ‘AÑO’ corresponde al último día de cada año (`freq='YE'`).
    departamentos_anual : pandas.DataFrame
        Panel anual de secuestros por departamento, con columnas:
        ['AÑO', 'COD_DEPTO', 'DEPARTAMENTO', 'N_SIMPLE', 'N_EXTORSIVO', 'TOTAL'].
    serie_colombia_mensual : pandas.DataFrame
        Serie mensual agregada para todo el país, con columnas:
        ['AÑO', 'N_SIMPLE', 'N_EXTORSIVO', 'TOTAL'].
        Aquí ‘AÑO’ es en realidad la última fecha del mes, usada como etiqueta.
    """

    # Obtengamos los datos de la funcion creada arriba
    secuestros_departamentos , secuestros_municipios , df1 = f(df)

    # Crear Panel Mensual para municipios 
    municipios_mensual = (secuestros_municipios.set_index('FECHA HECHO').groupby([
        pd.Grouper(freq='ME'),
        'COD_DEPTO', 'DEPARTAMENTO',
        'COD_MUNI', 'MUNICIPIO'])[['N_SIMPLE', 'N_EXTORSIVO']].sum().reset_index().rename(columns={'FECHA HECHO': 'MES'}))
    municipios_mensual['TOTAL'] = municipios_mensual['N_SIMPLE'] + municipios_mensual['N_EXTORSIVO']


    # Crear Panel Mensual para departamentos 
    departamentos_mensual = (secuestros_departamentos.set_index('FECHA HECHO').groupby([
        pd.Grouper(freq='ME'),
        'COD_DEPTO', 'DEPARTAMENTO'])[['N_SIMPLE', 'N_EXTORSIVO']].sum().reset_index().rename(columns={'FECHA HECHO': 'MES'}))
    departamentos_mensual['TOTAL'] = departamentos_mensual['N_SIMPLE'] + departamentos_mensual['N_EXTORSIVO']


    # Crear Panel Anual para municipios
    municipios_anual = (secuestros_municipios.set_index('FECHA HECHO').groupby([
        pd.Grouper(freq='YE'),
        'COD_DEPTO', 'DEPARTAMENTO',
        'COD_MUNI', 'MUNICIPIO'])[['N_SIMPLE', 'N_EXTORSIVO']].sum().reset_index().rename(columns={'FECHA HECHO': 'AÑO'}))
    municipios_anual['TOTAL'] = municipios_anual['N_SIMPLE'] + municipios_anual['N_EXTORSIVO']

    # Crear Panel Anual para departamentos 
    departamentos_anual = (secuestros_departamentos.set_index('FECHA HECHO').groupby([
        pd.Grouper(freq='YE'),
        'COD_DEPTO', 'DEPARTAMENTO'])[['N_SIMPLE', 'N_EXTORSIVO']].sum().reset_index().rename(columns={'FECHA HECHO': 'AÑO'}))
    departamentos_anual['TOTAL'] = departamentos_anual['N_SIMPLE'] + departamentos_anual['N_EXTORSIVO']

    # Crear la serie total de secuestros para Colombia 
    serie_colombia_mensual = (df1.set_index('FECHA HECHO').resample('ME')[['N_SIMPLE', 'N_EXTORSIVO']]
    .sum().reset_index().rename(columns={'FECHA HECHO': 'AÑO'}))
    serie_colombia_mensual['TOTAL'] = serie_colombia_mensual['N_SIMPLE'] + serie_colombia_mensual['N_EXTORSIVO']

    return municipios_mensual , departamentos_mensual , municipios_anual , departamentos_anual  , serie_colombia_mensual


############################# Funciones para el scrpt 2 ############################# 


def concatenar_poblacion(df_sec , df_pop , periodo , ubicacion):
    """
    Combina datos de secuestros con datos de población según año y nivel geográfico.

    Esta función toma un DataFrame de secuestros (`df_sec`) que contiene una columna de fechas,
    y un DataFrame de población (`df_pop`) con conteos poblacionales por municipio o departamento.
    Extrae el año de la columna de fecha en `df_sec`, ajusta los nombres de clave en `df_pop`
    y realiza un merge para incorporar la población correspondiente a cada registro de secuestro.

    Parámetros
    ----------
    df_sec : pandas.DataFrame
        DataFrame con los registros de secuestros. Debe contener una columna de tipo datetime
        identificada por el argumento `periodo`.
    df_pop : pandas.DataFrame
        DataFrame con los datos de población. Para `ubicacion='MUN'` debe tener la columna 'MPIO',
        y para `ubicacion='DEP'` la columna 'DP'.
    periodo : str
        Nombre de la columna en `df_sec` que contiene la fecha del hecho (tipo datetime).
    ubicacion : {'MUN', 'DEP'}
        Nivel geográfico para el merge:
        - 'MUN': se unirá por municipio (código COD_MUNI).
        - 'DEP': se unirá por departamento (código COD_DEPTO).

    Retorna
    -------
    pandas.DataFrame
        DataFrame resultante de unir `df_sec` con la columna de población.
        Incluye todas las columnas originales de `df_sec` más:
        - 'AÑO': año extraído de la fecha de `df_sec`.
        - 'Población': correspondiente al nivel geográfico y año del registro.
    """
    if ubicacion == 'MUN':
        df_pop = df_pop.rename(columns={'MPIO': 'COD_MUNI'})

        df_sec['AÑO'] = df_sec[periodo].dt.year.astype(int)
        df_pop['COD_MUNI'] = df_pop['COD_MUNI'].astype(int)
        df_final = df_sec.merge(df_pop[[ 'Población' ,'AÑO' , 'COD_MUNI']], 
                              on=['AÑO' , 'COD_MUNI'], how='left' ,suffixes=('','_agg'))
        
    elif ubicacion == 'DEP':
        df_pop = df_pop.rename(columns={'DP': 'COD_DEPTO'})
        
        df_sec['AÑO'] = df_sec[periodo].dt.year.astype(int)
        df_pop['COD_DEPTO'] = df_pop['COD_DEPTO'].astype(int)
        df_final = df_sec.merge(df_pop[[ 'Población' ,'AÑO' , 'COD_DEPTO']], 
                              on=['AÑO' , 'COD_DEPTO'], how='left' ,suffixes=('','_agg'))
        
    return df_final 



def depurar_base(df , columnas):
    """
    Limpia y prepara la base de datos de violencia, generando una columna de fecha
    y construyendo un GeoDataFrame con geometrías válidas.

    Esta función realiza los siguientes pasos:
    1. Selecciona solo las columnas especificadas.
    2. Reemplaza valores inválidos de mes (0) y día (0) por 1.
    3. Elimina filas donde el año sea 0.
    4. Ajusta el día al último día válido del mes en caso de estar fuera de rango.
    5. Construye una columna `fecha` de tipo datetime en formato YYYY-MM-DD.
    6. Elimina las columnas originales de año, mes, día y la columna auxiliar `Día_clip`.
    7. Convierte la columna WKT `latitud-longitud` en geometrías de Shapely.
    8. Filtra y descarta geometrías con coordenadas (0, 0).

    Parámetros
    ----------
    df : pandas.DataFrame
        DataFrame original que contiene las columnas de año, mes, día y WKT de coordenadas.
    columnas : list of str
        Lista con los nombres de columnas a mantener antes de la depuración.

    Retorna
    -------
    df1 : pandas.DataFrame
        DataFrame limpio con la nueva columna `fecha` (string YYYY-MM-DD) y sin las columnas de año, mes, día ni WKT.
    gdf : geopandas.GeoDataFrame
        GeoDataFrame con las mismas filas de `df1` (filtradas) y una columna `geometry` válida (EPSG:4326).
    def clip_day(row):
        year, month, day = row['Año'], row['Mes'], row['Día']
        last = calendar.monthrange(year, month)[1]
        return min(day, last)
    """
    # Función auxiliar para ajustar días fuera de rango
    def clip_day(row):
        year, month, day = row['Año'], row['Mes'], row['Día']
        last = calendar.monthrange(year, month)[1]
        return min(day, last)
    
    df1 = df[columnas]
    df1['Mes'] = df1['Mes'].replace(0, 1)
    df1['Día'] = df1['Día'].replace(0, 1)
    df1 = df1[df1['Año'] != 0]
    df1['Día_clip'] = df1.apply(clip_day, axis=1)

    df1['fecha'] = pd.to_datetime({
        'year':  df1['Año'],
        'month': df1['Mes'],
        'day':   df1['Día_clip']})

    df1['fecha'] = df1['fecha'].dt.strftime('%Y-%m-%d')
    df1['Día'] = df1['Día'].replace(0, 1)
    df1 = df1.drop(columns=['Año' , 'Mes' , 'Día' ,'Día_clip'])

    # Crear Geo DataFrame 
    gdf = gpd.GeoDataFrame(df1, geometry=gpd.GeoSeries.from_wkt(df1['latitud-longitud']) , crs="EPSG:4326")
    gdf = gdf.drop(columns=['latitud-longitud'])
    mask = ~((gdf.geometry.x == 0) & (gdf.geometry.y == 0))
    gdf = gdf[mask]
    return df1 , gdf



