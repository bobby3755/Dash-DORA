#Name: DORA Dashboard
#purpose: create a dashboard wherein the csv file choosen is graphed
#Last working on: DASH components is giving me an error called Quota exceeded. trying to see which part of the code is giving me this error. 
# Thread: dff_json is not always filled when intiated and that causes a class error or something? 
# Thread: dff_json is passing to 
# Thread: dff_json DCC  STORE needs to be reset to clear the storage between different intensities? 
# Thread: dff can be cleared via a call back https://stackoverflow.com/questions/55574925/i-cannot-figure-out-how-to-clear-the-local-store-when-using-dcc-store



# LOAD Modules
import os
import base64
import io
import sys
import numpy as np
import pandas as pd     #(version 1.0.0)
import plotly           #(version 4.5.4) pip install plotly==4.5.4
import plotly.express as px

import dash             #(version 1.9.1) pip install dash==1.9.1
from dash import dcc
import dash_bootstrap_components as dbc
from dash import html
from dash.dependencies import Input, Output, State

#USER IMPORT DORA FROM folder
sys.path.append(r'C:\Users\jerry\Desktop\Research\Kosuri\Rotor_Data_Interpretation\Jerry_Time_to_shine\DORA_Visualization-main\OMMxDORA-main\OMMxDORA-main\sma') #if you are not amanda, change to your sma file path (found in zipfile downloaded from github)
import DORA

### USER INPUT REQUIRED ############################################################
# DORA.find_center Parameters
# USER EDIT
time_step = 2  # miliseconds per frame in trajectory movie
exp_tag = 'OrbitBiotin500Hz100Lz_1k'
unit = "pixel"
pixel_size = 154  # in nanometers (or nm per pixel or nm/px )
frame_start = 0  # enter 0 to start from beginning of dataset
frame_end = -1 # enter -1 to end at the last value of the data set
cmap = "spring_r" # enter a color map string from this https://matplotlib.org/2.0.2/examples/color/colormaps_reference.html


#downsampling parameters
bin_size = 20  # bin size for downsample/filter processing
processing = "none"  # enter downsample, moving average, or none

#Plot Parameters

#Which Graph?
plot_type = "2D"
#plot_type = "2D"
#Graphing options:
    #Trajectory Maps:
        #2D: Colorful 2D visulization of the rotor from above
        #2D_LocPres: 2D plot now with Localization precision

##### Trajectory Maps Parameters:

# "yes" enables center display of center coordinates if 2D or Find err angle
display_center = "yes"

#Labels
x_axis_label = "x (nm)"
y_axis_label = "y (nm)"
z_axis_label = "Time (ms)"  
unit = "nm"  # enter pixel or nm

#Formatting parameters
pixel_min = -0.75  # setting min/max axis range (pixel)
pixel_max = 0.75

# change axis increments for nicely fitting tick marks (pixel)
axis_increment_pixel = 7
# change axis increments for nicely fitting tick marks (nm)
axis_increment_nm = 7
nm_min = -150  # setting min/max axis range (nm)
nm_max = 150
#Do you want to save your plot?
save_plot = 'no'


app = dash.Dash(__name__)

### Choose theme _______________________________________________________

# https://www.bootstrapcdn.com/bootswatch/
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MINTY],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                )

# Organize all the csv's in the data folder--------------------------------------------------------------- 

#INPUT data folder name
folder_name = r"C:\Users\jerry\Desktop\Research\Kosuri\Dashboards\Dash-DORA\data"

#Take all files in the current folder(the one we just switched to) and store it in a list through which we will iterate
my_files = os.listdir(folder_name)

#for all the files, get me the ones that end with .csv
my_csvs = [x for x in my_files if x.endswith(".csv")]

#add data folder to path
sys.path.append(folder_name)

# get current path
path_OG = os.getcwd()

# LAYOUT ---------------------------------------------------------------

app.layout = dbc.Container([ 

    ### Load Data
    dcc.Store(
            id='csv-data',
            storage_type='session',
            data=None,
        ),
    
    ### Load Storage for Data filtered for Frames
    dcc.Store(
            id='csv-data-frame',
            storage_type='session',
            data=None,
        ),

    ### Load Storage for Data filtered for Intensity
    dcc.Store(
            id='csv-data-frame-intensity',
            storage_type='session',
            data=None,
        ),

    ### Title Row
    dbc.Row([
        dbc.Col(html.H1("DORAxOMM Dashboard", 
            className= 'text-center text-primary, mb-4'),
            width = 9
        )
    ]),

    # #Row Upload
    # dbc.Row([
    #     dcc.Upload(
    #         id='data-table-upload',
    #         children=html.Div(
    #             [
    #                 html.Button('Upload File')
    #             ],
    #             style={
    #                 'width': '49%', 'height': "60px", 'borderWidth': '1px',
    #                 'borderRadius': '5px',
    #                 'textAlign': 'center',
    #             }
    #         ),
    #         multiple=False
    #     ),
    # ]), # end Row upload

    ### Row 1
    dbc.Row([

        #selecting column
        dbc.Col([ 
            html.Label(['Choose column:'],style={'font-weight': 'bold', "text-align": "center"}),
        
            dcc.Dropdown(id='my_dropdown',
                options=[
                        {'label': i, 'value': i} for i in my_csvs
                ],
                optionHeight=35,                    #height/space between dropdown options
                value= my_csvs[0],                    #dropdown value selected automatically when page loads
                disabled=False,                     #disable dropdown value selection
                multi=False,                        #allow multiple dropdown values to be selected
                searchable=True,                    #allow user-searching of dropdown values
                search_value='',                    #remembers the value searched in dropdown
                placeholder='Please select csv...',     #gray, default text shown when no option is selected
                clearable=False,                     #allow user to removes the selected value
                style={'width':"100%"},             #use dictionary to define CSS styles of your dropdown
                # className='select_box',           #activate separate CSS document in assets folder
                # persistence=True,                 #remembers dropdown value. Used with persistence_type
                # persistence_type='memory'         #remembers dropdown value selected until...
                ),                                  #'memory': browser tab is refreshed
                                                    #'session': browser tab is closed
                                                    #'local': browser cookies are deleted
            html.Label(id='output_container', children = []),
            
            
            # #frame Range Slider
            # dbc.Col([
            #       
            # ]),
            
        ], width = 3), #end col 1

        #col 2 
        dbc.Col([
            html.Label(['Choose Times (ms):'],style={'font-weight': 'bold', "text-align": "center"}),

            dcc.RangeSlider(min = 0, max = 1, id = 'frame-slider', marks = None, tooltip={"placement": "bottom", "always_visible": True}) 

        ], width = 3), # end col 2 

        #col 3 
        dbc.Col([
            html.Label(['From Choosen Frames, Choose Intensity:'],style={'font-weight': 'bold', "text-align": "center"}),

            dcc.RangeSlider(min = 0, max = 1, id = 'intensity-slider', marks = None, tooltip={"placement": "bottom", "always_visible": True}) 

        ], width = 3) # end col 3

    ]), #end row 1

    ### Row 2
    dbc.Row([
        #graph choosen
        dbc.Col([
            html.Label(['Old Graph'],style={'font-weight': 'bold', "text-align": "center"}),
            dcc.Graph(id='our_graph')

            ],width=6),

    ]), # end row 2

    ### Row 3
    dbc.Row([
        #graph choosen
        dbc.Col([
            html.Label(['Modular Graph'],style={'font-weight': 'bold', "text-align": "center"}),
            dcc.Graph(id='2D_graph')

            ],width=6),

    ]), # end row 3
])


# CALLBACKs---------------------------------------------------------------

##################### CB 1: Dropdown Callback
@app.callback([Output('output_container', 'children'),
               Output('our_graph', 'figure'),
               Output('csv-data','data')],
              [Input('my_dropdown', 'value')],
)

# Output(component_id = 'my-frame-range-slider', component_property = 'max')

def update_graph(fileChosen):
    print(fileChosen)
    print(type(fileChosen))

    #tell user what is happening
    container = f"The .csv chosen by the user was: {fileChosen}"
    
    file_name = fileChosen

    #Change the folder directory to be the current folder's 
    os.chdir(folder_name)
    
    #generate figure
    #run DORA.find_center

    #Hard code these initial parameters 
    first_zero_end='no'
    graph_centers='no'
    save_plot='no'
    
    initial_parameters = [file_name, time_step, frame_start, frame_end, cmap, exp_tag, first_zero_end, graph_centers, save_plot]
    center, data, _, _, _ = DORA.find_center(*initial_parameters)
    

    # run DORA.downsampling
    downsample_parameters = [bin_size, processing, data, center, time_step, pixel_size, frame_start, frame_end]
    down_sampled_df = DORA.downsample(*downsample_parameters)
    df = down_sampled_df
    
    # Here the code determines the units of the graph, only for cartesian graphs
    if unit == "pixel":
        x = "X displacement (pixels)"
        y = "Y displacement (pixels)"
    if unit == "nm":
        x = "X displacement (nm)"
        y = "Y displacement (nm)"
    z = df["Time (ms)"]

    # make a plotly 2D graph
    pk = os.path.splitext(file_name)[0]
    # graph_type = '2D_Map'
    # change title order!!! 
    list_of_strings = [exp_tag,pk]
    #in quotes is the the delimiter between the items in the string
    # by default it is a _ 
    my_title = "_".join(list_of_strings)

    fig = px.scatter(df, x = x ,y = y,color = z, title = my_title)

    #Change the folder directory to the original folder
    os.chdir(path_OG)

    df_json = df.to_json(date_format='iso', orient='split')

    return container, fig, df_json

###################### CB 2: Frame Slider
@app.callback([Output("frame-slider",'min'),
               Output("frame-slider",'max')],
             [Input('csv-data', 'data')],
             [State('csv-data', 'data')]

)

def update_frame_slider(_,data):

    # if there is no initally selected data, don't give me anything 
    if not data:
        print("[df--> frame slider CallBack]no intially selected data --> don't give me anything")
        return dash.no_update, dash.no_update

    # if there is something, go into the data frame and export the min_v and max_v

    df = pd.read_json(data, orient='split')
    min_frame = df["Time (ms)"].iloc[0]
    max_frame = df["Time (ms)"].iloc[-1]
    
    return min_frame, max_frame

###################### Update Data Filtered for Frames
@app.callback([Output('csv-data-frame','clear_data'),
               Output('csv-data-frame','data')],
              [Input('frame-slider','value')],
              [State('csv-data', 'data')]
)

def update_selected_frames(frame_range,data):

    # if there is no initally selected data, don't give me anything 
    if not data:
        print("[Update dataframe from selected frames CallBack] No Intial data. Dash will not update")
        return dash.no_update

    # if there is no initally selected data, don't give me anything 
    if not frame_range:
        print("[no frame range]. I'm not gonna give you anything")
        return dash.no_update


    # if there is something, go into the data frame and export the relevant frames as a new dataframe

    df = pd.read_json(data, orient='split')

    # extract frame start and end from frame_range
    
    startFrame = frame_range[0]
    endFrame = frame_range[1]

    print(f"my frame range is  {frame_range}, my start frame is {startFrame}, my end frame is , {endFrame}")
    # section out the relevant frames
    fmin = df.index.min()
    id_low = startFrame - fmin
    fdiff = endFrame - startFrame
    id_high = id_low + fdiff
    dff = df.copy()
    dff = dff.iloc[id_low:id_high]
    print("dff is filtered for new frames")

    # Package dff into Json for export

    dff_json = dff.to_json(date_format='iso', orient='split')
    print(dff_json)

    return True, dff_json


    
###################### Intensity Slider Update with Frames
@app.callback([Output('intensity-slider','min'),
               Output('intensity-slider','max')],
              [Input('csv-data-frame', 'data')],
              [State('csv-data-frame', 'data')]
)

def update_intensity_slider_minMax(__,data):
    
    # if there is no initally selected data, don't give me anything 
    if not data:
        print("[dff to intensity slider is empty] .No Intial data. I'm not gonna give you anything")
        return dash.no_update, dash.no_update

    # if there is something, unpack the dataframe
    print(data)
    dff = pd.read_json(data, orient='split')
    
    print("")
    #frame the relevant frames add in the minimum and the maximum intensity values
    min_int = dff["Intensity"].min()
    max_int = dff["Intensity"].max()
    print(f"new intensity in is [{min_int}, {max_int}]")
    
    
    return min_int, max_int

##################### If the min and max change, change the intensity slider value to the min and max
@app.callback(Output('intensity-slider','value'),
              [Input('intensity-slider','min'),
               Input('intensity-slider','max')]
)

def update_intensity_slider_value(minInt, maxInt):
    
    # if there is no initally selected data, don't give me anything 
    if not minInt or maxInt:
        print("[Min and max intensities are not loading] No Intial data. I'm not gonna give you anything")
        return dash.no_update

    # if the min and max are adjusted, reset the value to be the min and the max

    valueInt = [minInt,maxInt]
    print(f"my Intensity Value is {valueInt}")
    
    return valueInt



### --------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)

    
    
# https://youtu.be/UYH_dNSX1DM

