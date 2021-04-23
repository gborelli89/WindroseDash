import base64
import io

import pandas as pd
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px

# Velocity conversion table
convel = pd.DataFrame(data={'m/s':[1.0, 1/3.6, 1/2.237, 1/1.944], 'km/h':[3.6, 1.0, 1.609, 1.852],
                    'mph':[2.237, 1/1.609, 1.0, 1.151], 'knots':[1.944, 1/1.852, 1/1.151, 1.0]})
convel.index = ['m/s', 'km/h', 'mph', 'knots']

# Upload function
def parse_contents(contents, filename, delim, dec, velcol,dircol, dirlabels, 
                    vlim, unit_from, unit_to, valid_data):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')), delimiter=delim, decimal=dec)
            wr, dfcomp, N, n = processcsv(df,velcol,dircol,dirlabels,vlim,unit_from, unit_to,bool(valid_data))
            msg = infomsg(N,n)
            fig = px.bar_polar(wr, r='Freq', theta='Dir', color='V', width=1200, height=900,
                    color_discrete_sequence=px.colors.sequential.Viridis)
            fig.update_layout(font_size=22, font_color="black", legend_title='V(' + unit_to + ')')
        #elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            #df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        #html.H5(filename),
        dcc.Graph(
            figure = fig
        ),
        html.Hr(),
        html.Div(msg)
    ])


# Processing function
def processcsv(df, vcol, dcol, dlabel, vlim, unit_from, unit_to, onlyvalid):
    # Spliting data
    vcol = vcol - 1
    v = df.iloc[:,vcol]
    fac = convel.loc[unit_from, unit_to]
    v = v*fac
    dcol= dcol - 1
    d = df.iloc[:,dcol]
    df_new = pd.DataFrame(data={'V':v, 'Vrange':'X', 'Dir':d, 'Dirlabel':'X'})
     

    # Total number of measurements
    N = df_new.shape[0]

    # Defining dlabels
    if dlabel == 0:
        dlabel = ['N','E','S','W']
    elif dlabel == 1:
        dlabel = ['N','NE','E','SE','S','SW','W','NW']
    else:
        dlabel = ['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW']

    # Angular step for wind headings
    deltad = 360/len(dlabel)

    # Define wind heading labels
    df_new.loc[df_new['Dir'] >= 0, 'Dirlabel'] = dlabel[0]
    for k in range(1,len(dlabel)):
        i = k - 1
        df_new.loc[df_new['Dir'] >= 0.5*deltad + i*deltad, 'Dirlabel'] = dlabel[k]
    
    # Working with the velocity ranges
    vlim1 = vlim.split(';')
    vlim2 = vlim1.copy()
    vlim2[0] = '0-' + vlim1[0]
    vlim2.append(vlim1[-1] + '-Inf')
    for k in range(1,len(vlim1)):
        i = k-1
        vlim2[k] = vlim1[i] + '-' + vlim1[k]

    vlim_float = [float(i) for i in vlim1]
    
    df_new.loc[df_new['V'] >= 0, 'Vrange'] = vlim2[0]
    for i in range(0,len(vlim_float)):
        k = i+1
        df_new.loc[df_new['V'] >= vlim_float[i], 'Vrange'] = vlim2[k]

    # Valid measurements
    df_complete = df_new.copy()
    df_complete.dropna(axis=0, how='any', inplace=True)
    n = df_complete.shape[0]

    # Grouping data
    countevents = df_complete.groupby(['Dirlabel','Vrange'])['V'].count()

    if onlyvalid:
        freq = 100*(countevents/n)
    else:
        freq = 100*(countevents/N)
    
    # Generating wr dataframe
    wr = pd.DataFrame()
    for i in dlabel:
        df_temp = pd.DataFrame(data={'Dir':list(np.repeat(i,len(freq[i]))),'V':list(freq[i].index), 'Freq':list(freq[i])})
        wr = pd.concat([wr,df_temp])
    
    return wr, df_complete, N, n

def infomsg(N,n):
    info_total = 'Total number of measurements: ' + str(N)
    info_valid = 'Number of valid measurements: ' + str(n)
    p_na = 100*(1-(n/N))
    info_na = 'NA percentual: ' + str(np.round(p_na,2)) + '%'
    return html.Div([
        html.H5(info_total),
        html.H5(info_valid),
        html.H5(info_na)
    ])


app = dash.Dash(__name__)

server = app.server

app.layout = html.Div([

    html.Div([
        html.H2("WIND ROSE GENERATOR"),
        html.H4("CSV parameters"),
        html.Div(
            dcc.Dropdown(
                id='delim',
                options=[
                    {'label':';', 'value':';'},
                    {'label':',', 'value':','},
                    {'label':'tab', 'value':'\t'}
                ],
                style={'width':'90%'},
                placeholder='Delimiter'
            ), style={'width': '48%', 'display': 'inline-block'}
        ),
        html.Div(
            dcc.Dropdown(
                id='dec',
                options=[
                    {'label':'.', 'value':'.'},
                    {'label':',', 'value':','}
                ],
                style={'width':'90%'},
                placeholder='Decimal'
            ),style={'width': '48%', 'display': 'inline-block'}
        ),

        html.Div([
            html.H4("Velocity column"),
            dcc.Input(
                id='velcolumn',
                type='number',
                min=1,
                style={'width':'70%'}
            )], style={'width': '45%', 'display': 'inline-block'}
        ),
        html.Div([
            html.H4("Wind heading column"),
            dcc.Input(
                id='dircolumn',
                type='number',
                min=1,
                style={'width':'70%'}
            )], style={'width': '50%', 'display': 'inline-block'}
        ),
        html.H4("Heading labels"),
        dcc.Dropdown(
            id='headinglabel',
            options=[
                {'label':'4 directions', 'value':0},
                {'label':'8 directions', 'value':1},
                {'label':'16 directions', 'value':2}
            ],
            value= 1
        ),
        html.H4("Velocity breaks delimited by semicolon"),
        dcc.Input(
            id='velbreak',
            type='text',
            placeholder='Eg. 1;2;3;4;5;6'
        ),

        #html.H4("Conversion"),

        html.Div([
            html.H4("From"),
            dcc.Dropdown(
                id='unit-from',
                options=[
                    {'label':'m/s', 'value':'m/s'},
                    {'label':'km/h', 'value':'km/h'},
                    {'label':'mph', 'value':'mph'},
                    {'label':'knots', 'value':'knots'}
                ],
                style={'width':'90%'},
                value='m/s'
            )], style={'width': '48%', 'display': 'inline-block'}
        ),
        html.Div([
            html.H4("To"),
            dcc.Dropdown(
                id='unit-to',
                options=[
                    {'label':'m/s', 'value':'m/s'},
                    {'label':'km/h', 'value':'km/h'},
                    {'label':'mph', 'value':'mph'},
                    {'label':'knots', 'value':'knots'}
                ],
                style={'width':'90%'},
                value='m/s'
            )], style={'width': '48%', 'display': 'inline-block'}
        ),

        html.H4("Frequency considering only valid measurements?"),
        dcc.Dropdown(
            id='valid-data',
            options=[
                {'label': 'Yes', 'value': 1},
                {'label': 'No, consider everything', 'value': 0}
            ],
            value='No, consider everything'
        ),

        html.Hr(),

        dcc.Upload(
            id='upload-data',
                children=html.Div([
                'Drag and Drop or ',
                html.A('Select CSV File')
            ]),
            style={
                'width': '70%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            # Allow multiple files to be uploaded
            multiple=False
        ),

        html.Div(id='output-filename')


    ], style={'width':'25%','display':'inline-block'} 
    ),

    html.Div(id='output-data-upload', style={'width':'75%', 'float':'right'})
    
])

@app.callback(
    Output('output-data-upload', 'children'),
    [Input('delim','value'), Input('dec','value'), Input('upload-data','contents'), 
    Input('velcolumn','value'), Input('dircolumn','value'), Input('headinglabel','value'), 
    Input('velbreak','value'), Input('unit-from','value'), Input('unit-to','value'), Input('valid-data','value')],
    State('upload-data','filename')
)
def update_output(delim_value, dec_value, file_content, velcol, dircol, 
                    dirlabels, vlim, ufrom, uto, valid_data, file_name):
    

    if file_content is not None:
        #children = "processed data from file " + file_name
        children = [parse_contents(file_content, file_name, delim_value, dec_value, 
                velcol, dircol, dirlabels, vlim, ufrom, uto, bool(valid_data))]
        #wr, dfcomp, N, n = processcsv(df,velcol,dircol,dirlabels,vlim,bool(valid_data))
        #fig = px.bar_polar(wr, r='Freq', theta='Dir', color='V', color_discrete_sequence=px.colors.sequential.Viridis)
        #children = infomsg(N,n)
        return children
   

if __name__ == '__main__':
    app.run_server(debug=False)

