# -*- coding: utf-8 -*-
"""
Created on Tue May 27 17:40:11 2025

@author: thoma
"""


from shapefinder import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle
import os

# =============================================================================
# 2D shapes 
# =============================================================================

def test_2D():
    
    # Import dataset Confilct fatalities 
    # Raw data from UCDP, available here : https://ucdp.uu.se/downloads/)

    # Get the path to this test file
    CURRENT_DIR = os.path.dirname(__file__)
    
    # Construct the full path to Conf.csv
    csv_path = os.path.join(CURRENT_DIR, "Conf.csv")
    # Construct the path for output 
    output_dir = os.path.join(CURRENT_DIR, "Output/")
    
    df_conf = pd.read_csv(csv_path,index_col=0,parse_dates=True)
    
    # Init a shape as a W shape 
    shape = Shape()
    shape.set_shape([1,0.5,0,0.5,1,0.5,0]) 
    shape.plot(save=output_dir+'Input.png')
    
    # Init a finder in the conflict fatalities dataset
    find = finder(df_conf,Shape=shape)
    find.find_patterns(min_d=0.35,select=True,metric='dtw',dtw_sel=1)
    find.create_sce(horizon=3,clu_thres=2)
    find.plot_scenario(save=output_dir+'scenario_plot.png')
    
    # Predict the next three points
    pred = find.predict(horizon=3,clu_thres=2)
    
    # Save the results
    dict_save = {'prediction':pred,'similar_sequences':find.sequences}
    with open(output_dir+'2D_store.pkl', 'wb') as f:
        pickle.dump(dict_save, f)
    

# =============================================================================
# 3D shapes 
# =============================================================================

def test_3D():
    
    # Get the path to this test file
    CURRENT_DIR = os.path.dirname(__file__)
    # Construct the path for output 
    output_dir = os.path.join(CURRENT_DIR, "Output/")
    
    # Define a small 3D pattern array `test` (shape: 2x3x4)
    test = np.array([
        [[0.36363636, 0.45454545, 0.18181818, 0.        ],
         [0.27272727, 0.09090909, 0.        , 0.        ],
         [0.        , 0.        , 0.        , 1.        ]],
        [[0.        , 0.        , 0.        , 0.        ],
         [0.18181818, 0.        , 0.90909091, 0.        ],
         [0.        , 0.27272727, 0.        , 0.        ]]
    ])
    
    shape3D = Shape_3D()
    shape3D.set_shape(test)
    
    # Dimensions of the test pattern
    sx, sy, sz = test.shape
    
    # Create a larger 3D array (`target`) filled with mostly zeros
    target_shape = (20, 20, 20)
    target = np.random.rand(*target_shape)
    
    # Create a mask to sparsify the target (80% of values set to 0)
    mask = np.random.rand(*target_shape) < 0.8
    target[mask] = 0
    
    # Insert known patterns into the target at specified locations
    positions = [(4, 10, 10), (8, 6, 4), (12, 1, 4)]
    for i in positions:
        x, y, z = i
        if i == positions[1]:
            # Insert a rotated version (180° around axes 0 and 1)
            test2 = np.rot90(test, k=2, axes=(0, 1))
            target[x:x+sx, y:y+sy, z:z+sz] = test2
        elif i == positions[2]:
            # Insert a modified version with a padded zero row in axis 1
            test_mod = np.concatenate((test[:, :2, :], np.zeros((2, 1, 4)), test[:, 2:, :]), axis=1)
            target[x:x+sx, y:y+sy+1, z:z+sz] = test_mod
        else:
            # Insert a scaled down version (divided by 2)
            target[x:x+sx, y:y+sy, z:z+sz] = test / 2
    
    # Initialize the finder with the target and the reference shape
    finder = finder_3D(target, Shape_3D=shape3D)
    
    # Search for matches using Earth Mover's Distance (EMD) as distance. 
    # Only the patterns with less than 0.1 are classified as similar pattern.
    finder.find_patterns(mode='emd', min_emd=0.1, min_mat=3)
    
    pred = finder.predict(h=3,thres_clu=10)
    
    # Save the results
    dict_save = {'prediction':pred,'similar_sequences':finder.sequences}
    with open(output_dir+'3D_store.pkl', 'wb') as f:
        pickle.dump(dict_save, f)
    