# -*- coding: utf-8 -*-
"""
Created on Mon Jul 24 17:52:04 2023

@author: Thomas Schincariol
"""

import tkinter as tk
import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.widgets import Cursor, Button
import numpy as np
from dtaidistance import dtw,ed
import bisect
import math
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial import distance
from scipy.sparse.csgraph import minimum_spanning_tree
import matplotlib.colors as mcolors
import matplotlib.cm as cm
import plotly.graph_objects as go
from plotly.offline import plot
import ot
from math import tanh
from scipy.spatial.distance import pdist, squareform

# =============================================================================
# ShapeFinder for Time series Autoregressive
# =============================================================================

def int_exc(seq_n, win):
    """
    Create intervals and exclude list for the given normalized sequences.

    Args:
        seq_n (list): A list of normalized sequences.
        win (int): The window size for pattern matching.

    Returns:
        tuple: A tuple containing the exclude list, intervals, and the concatenated testing sequence.
    """
    n_test = []  # List to store the concatenated testing sequence
    to = 0  # Variable to keep track of the total length of concatenated sequences
    exclude = []  # List to store the excluded indices
    interv = [0]  # List to store the intervals

    for i in seq_n:
        n_test = np.concatenate([n_test, i])  # Concatenate each normalized sequence to create the testing sequence
        to = to + len(i)  # Calculate the total length of the concatenated sequence
        exclude = exclude + [*range(to - win, to)]  # Add the excluded indices to the list
        interv.append(to)  # Add the interval (end index) for each sequence to the list

    # Return the exclude list, intervals, and the concatenated testing sequence as a tuple
    return exclude, interv, n_test

class Shape():
    """
    A class to set custom shape using a graphical interface, user-provided values or random values.

    Attributes:
        time (list): List of x-coordinates representing time.
        values (list): List of y-coordinates representing values.
        window (int): The window size for the graphical interface.
    """

    def __init__(self, time=len(range(10)), values=[0.5]*10, window=10):
        """
        Args:
            time (int): The initial number of time points.
            values (list): The initial values corresponding to each time point.
            window (int): The window size for the graphical interface.
        """
        self.time = time
        self.values = values
        self.window = window

    def draw_shape(self, window):
        """
        Opens a graphical interface for users to draw a custom shape.

        Args:
            window (int): The window size for the graphical interface.

        Notes:
            The user can draw the shape by clicking on the graph using the mouse.
            The Save button stores the drawn shape data in self.time and self.values.
            The Quit button closes the graphical interface.
        """
        root = tk.Tk()
        root.title("Please draw the wanted Shape")

        # Initialize the plot
        fig, ax = plt.subplots()
        fig.subplots_adjust(bottom=0.2)
        time_data = list(range(window))
        value_data = [0] * window
        line, = ax.plot(time_data, value_data)
        ax.set_xlim(0, window - 1)
        ax.set_ylim(0, 1)
        ax.set_title("Please draw the wanted Shape")

        def on_button_click(event):
            """
            Callback function for the Save button click event.

            Stores the drawn shape data in self.time and self.values and closes the window.

            Args:
                event: The button click event.
            """
            root.drawn_data = (time_data, value_data)
            root.destroy()

        def on_mouse_click(event):
            """
            Callback function for the mouse click event on the plot.

            Updates the plot when the user clicks on the graph to draw the shape.

            Args:
                event: The mouse click event.
            """
            if event.inaxes == ax:
                index = int(event.xdata + 0.5)
                if 0 <= index < window:
                    time_data[index] = index
                    value_data[index] = event.ydata
                    line.set_data(time_data, value_data)
                    fig.canvas.draw()

        def on_quit_button_click(event):
            """
            Callback function for the Quit button click event.

            Closes the graphical interface.

            Args:
                event: The button click event.
            """
            root.destroy()

        # Add buttons and event listeners
        ax_save_button = plt.axes([0.81, 0.05, 0.1, 0.075])
        button_save = Button(ax_save_button, "Save")
        button_save.on_clicked(on_button_click)

        ax_quit_button = plt.axes([0.7, 0.05, 0.1, 0.075])
        button_quit = Button(ax_quit_button, "Quit")
        button_quit.on_clicked(on_quit_button_click)

        # Connect mouse click event to the callback function
        fig.canvas.mpl_connect('button_press_event', on_mouse_click)
        cursor = Cursor(ax, useblit=True, color='red', linewidth=1)

        # Create and display the Tkinter canvas with the plot
        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Add toolbar and protocol for closing the window
        toolbar = NavigationToolbar2Tk(canvas, root)
        toolbar.update()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        root.protocol("WM_DELETE_WINDOW", on_quit_button_click)

        # Start the Tkinter main loop
        root.mainloop()

        # Update the shape data with the drawn shape
        value_data=pd.Series(value_data)
        value_data=(value_data - value_data.min()) / (value_data.max() - value_data.min())
        self.time = time_data
        self.values = value_data.tolist()
        self.window = len(time_data)

        # Close the figure to avoid multiple figures being opened
        plt.close(fig)

    def set_shape(self,input_shape):
        try:
            input_shape=pd.Series(input_shape)
            input_shape=(input_shape-input_shape.min())/(input_shape.max()-input_shape.min())
            self.time=list(range(len(input_shape)))
            self.values = input_shape.tolist()
            self.window=len(input_shape.tolist())
        except: 
            print('Wrong format, please provide a compatible input.')
        
    def set_random_shape(self,window):
        value_data=pd.Series(np.random.uniform(0, 1,window))
        value_data=(value_data - value_data.min()) / (value_data.max() - value_data.min())
        self.time=list(range(window))
        self.values = value_data.tolist()
        self.window=len(np.random.uniform(0, 1,window).tolist())

    def plot(self,save=None):
        plt.plot(self.time,self.values,marker='o')
        plt.xlabel('Timestamp')
        plt.ylabel('Values')
        plt.title('Shape wanted')
        plt.ylim(-0.05,1.05)
        if save is not None:
            plt.savefig(save, dpi=300, bbox_inches='tight')
        plt.show()

        
class finder():
    """
    A class to find and predict custom patterns in a given dataset using an interactive shape finder.

    Attributes:
        data (DataFrame): The dataset containing time series data.
        Shape (Shape): An instance of the Shape class used for interactive shape finding.
        sequences (list): List to store the found sequences matching the custom shape.
    """
    def __init__(self,data,Shape=Shape(),sequences=[]):
        """
        Initializes the finder object with the given dataset and Shape instance.

        Args:
            data (DataFrame): The dataset containing time series data.
            Shape (Shape, optional): An instance of the Shape class for shape finding. Defaults to Shape().
            sequences (list, optional): List to store the found sequences matching the custom shape. Defaults to [].
        """
        self.data=data
        self.Shape=Shape
        self.sequences=sequences
        
    def find_patterns(self, metric='euclidean', min_d=0.5, dtw_sel=0, select=True, min_mat=0):
        """
        Finds custom patterns in the given dataset using the interactive shape finder.
    
        Args:
            metric (str, optional): The distance metric to use for shape matching. 'euclidean' or 'dtw'. Defaults to 'euclidean'.
            min_d (float, optional): The minimum distance threshold for a matching sequence. Defaults to 0.5.
            dtw_sel (int, optional): The window size variation for dynamic time warping (Only for 'dtw' mode). Defaults to 0.
            select (bool, optional): Whether to include overlapping patterns. Defaults to True.
            min_mat (int, optional): The minimum number of matching sequences. Defaults to 0.
        """
        # Clear any previously stored sequences
        self.sequences = []
        
        # Check if dtw_sel is zero when metric is 'euclidean'
        if metric=='euclidean':
            dtw_sel=0
    
        # Extract individual columns (time series) from the data
        seq = []
        for i in range(len(self.data.columns)): 
            seq.append(self.data.iloc[:, i])
    
        # Normalize each column (time series)
        seq_n = []
        for i in seq:
            seq_n.append((i - i.mean()) / i.std())
    
        # Get exclude list, intervals, and a testing sequence for pattern matching
        exclude, interv, n_test = int_exc(seq, self.Shape.window)
    
        # Convert custom shape values to a pandas Series and normalize it
        seq1 = pd.Series(data=self.Shape.values)
        if seq1.var() != 0.0:
            seq1 = (seq1 - seq1.min()) / (seq1.max() - seq1.min())
        else :    
            seq1 = [0.5]*len(seq1)
        seq1 = np.array(seq1)
    
        # Initialize the list to store the found sequences that match the custom shape
        tot = []
    
        if dtw_sel == 0:
            # Loop through the testing sequence
            for i in range(len(n_test)):
                # Check if the current index is not in the exclude list
                if i not in exclude:
                    seq2 = n_test[i:i + self.Shape.window]
                    if seq2.var() != 0.0:
                        seq2 = (seq2 - seq2.min()) / (seq2.max() - seq2.min())
                    else:
                        seq2 = np.array([0.5]*len(seq2))
                    try:
                        if metric == 'euclidean':
                            # Calculate the Euclidean distance between the custom shape and the current window
                            dist = ed.distance(seq1, seq2)
                        elif metric == 'dtw':
                            # Calculate the Dynamic Time Warping distance between the custom shape and the current window
                            dist = dtw.distance(seq1, seq2,use_c=True)
                        tot.append([i, dist, self.Shape.window])
                    except:
                        # Ignore any exceptions (e.g., divide by zero)
                        pass
        else:
            # Loop through the range of window size variations (dtw_sel)
            for lop in range(int(-dtw_sel), int(dtw_sel) + 1):
                # Get exclude list, intervals, and a testing sequence for pattern matching with the current window size
                exclude, interv, n_test = int_exc(seq_n, self.Shape.window + lop)
                for i in range(len(n_test)):
                    # Check if the current index is not in the exclude list
                    if i not in exclude:
                        seq2 = n_test[i:i + int(self.Shape.window + lop)]
                        if seq2.var() != 0.0:
                            seq2 = (seq2 - seq2.min()) / (seq2.max() - seq2.min())
                        else:
                            seq2 = np.array([0.5]*len(seq2))
                        try:
                            # Calculate the Dynamic Time Warping distance between the custom shape and the current window
                            dist = dtw.distance(seq1, seq2)
                            tot.append([i, dist, self.Shape.window + lop])
                        except:
                            # Ignore any exceptions (e.g., divide by zero)
                            pass
    
        # Create a DataFrame from the list of sequences and distances, sort it by distance, and filter based on min_d
        tot = pd.DataFrame(tot)
        tot = tot.sort_values([1])
        tot_cut = tot[tot[1] < min_d]
        toti = tot_cut[0]
    
        if select:
            n = len(toti)
            diff_data = {f'diff{i}': toti.diff(i) for i in range(1, n + 1)}
            diff_df = pd.DataFrame(diff_data).fillna(self.Shape.window)
            diff_df = abs(diff_df)
            tot_cut = tot_cut[diff_df.min(axis=1) >= (self.Shape.window / 2)]
    
        if len(tot_cut) > min_mat:
            # If there are selected patterns, store them along with their distances in the 'sequences' list
            for c_lo in range(len(tot_cut)):
                i = tot_cut.iloc[c_lo, 0]
                win_l = int(tot_cut.iloc[c_lo, 2])
                exclude, interv, n_test = int_exc(seq_n, win_l)
                col = seq[bisect.bisect_right(interv, i) - 1].name
                index_obs = seq[bisect.bisect_right(interv, i) - 1].index[i - interv[bisect.bisect_right(interv, i) - 1]]
                obs = self.data.loc[index_obs:, col].iloc[:win_l]
                self.sequences.append([obs, tot_cut.iloc[c_lo, 1]])
        else:
            flag_end=False
            min_mat_loop=min_mat
            while flag_end==False:
                tot_cut = tot.iloc[:min_mat_loop,:]
                toti = tot_cut[0]
                if select:
                    n = len(toti)
                    diff_data = {f'diff{i}': toti.diff(i) for i in range(1, n + 1)}
                    diff_df = pd.DataFrame(diff_data).fillna(self.Shape.window)
                    diff_df = abs(diff_df)
                    tot_cut = tot_cut[diff_df.min(axis=1) >= (self.Shape.window / 2)]
                if len(tot_cut) > min_mat:
                    for c_lo in range(len(tot_cut)):
                        i = tot_cut.iloc[c_lo, 0]
                        win_l = int(tot_cut.iloc[c_lo, 2])
                        exclude, interv, n_test = int_exc(seq_n, win_l)
                        col = seq[bisect.bisect_right(interv, i) - 1].name
                        index_obs = seq[bisect.bisect_right(interv, i) - 1].index[i - interv[bisect.bisect_right(interv, i) - 1]]
                        obs = self.data.loc[index_obs:, col].iloc[:win_l]
                        self.sequences.append([obs, tot_cut.iloc[c_lo, 1]])
                    flag_end=True
                else:
                    min_mat_loop=min_mat_loop+1

        
    def plot_sequences(self,how='units',save=None):
        """
        Plots the found sequences matching the custom shape.

        Args:
            how (str, optional): 'units' to plot each sequence separately or 'total' to plot all sequences together. Defaults to 'units'.

        Raises:
            Exception: If no patterns were found, raises an exception indicating no patterns to plot.
        """
        # Check if any sequences were found, otherwise raise an exception
        if len(self.sequences) == 0:
            raise Exception("Sorry, no patterns to plot.")
    
        if how == 'units':
            # Plot each sequence separately
            for i in range(len(self.sequences)):
                plt.plot(self.sequences[i][0], marker='o')
                plt.xlabel('Date')
                plt.ylabel('Values')  # Corrected typo in xlabel -> ylabel
                plt.suptitle(str(self.sequences[i][0].name), y=1.02, fontsize=15)
                plt.title("d = " + str(self.sequences[i][1]), style='italic', color='grey')
                plt.show()
    
        elif how == 'total':
            # Plot all sequences together in a grid layout
            num_plots = len(self.sequences)
            grid_size = math.isqrt(num_plots)  # integer square root
            if grid_size * grid_size < num_plots:  # If not a perfect square
                grid_size += 1
    
            subplot_width = 7
            subplot_height = 5
            fig, axs = plt.subplots(grid_size, grid_size, figsize=(subplot_width * grid_size, subplot_height * grid_size))
    
            if num_plots > 1:
                axs = axs.ravel()
            if not isinstance(axs, np.ndarray):
                axs = np.array([axs])
    
            for i in range(num_plots):
                axs[i].plot(self.sequences[i][0], marker='o')
                axs[i].set_xlabel('Date')
                axs[i].set_title(f"{self.sequences[i][0].name}\nd = {self.sequences[i][1]}", style='italic', color='grey')
    
            if grid_size * grid_size > num_plots:
                # If there are extra subplot spaces in the grid, remove them
                for j in range(i + 1, grid_size * grid_size):
                    fig.delaxes(axs[j])
    
            plt.tight_layout()
            if save is not None:
                plt.savefig(save, dpi=300, bbox_inches='tight')
            plt.show()

    def create_sce(self,horizon=6,clu_thres=3):
        """
        Creates scenarios based on matched series in historical data.
        
        Args:
            horizon (int): The number of future time steps to consider for scenario creation.
            clu_thres (int): The threshold for clustering, influencing the number of clusters.
        
        """
        # Ensure sequences exist before proceeding
        if len(self.sequences) == 0:
            raise Exception('No shape found, please fit before predict.')
    
        # Extract key stats from stored sequences
        tot_seq = [
            [series.name, series.index[-1], series.min(), series.max(), series.sum()] 
            for series, weight in self.sequences]
    
        pred_seq = []
        # Generate future sequences for each stored sequence
        for col, last_date, mi, ma, somme in tot_seq:
            date = self.data.index.get_loc(last_date)  # Get index position of the last known date
            # Ensure there are enough future values for the specified horizon
            if date + horizon < len(self.data):
                # Extract future values for the given column
                seq = self.data.iloc[date + 1 : date + 1 + horizon, self.data.columns.get_loc(col)].reset_index(drop=True)
                # Normalize sequence using min-max scaling
                seq = (seq - mi) / (ma - mi)
                pred_seq.append(seq.tolist())
    
        # Convert sequences to a DataFrame
        tot_seq = pd.DataFrame(pred_seq)
        # Perform hierarchical clustering
        linkage_matrix = linkage(tot_seq, method='ward')
        clusters = fcluster(linkage_matrix, horizon / clu_thres, criterion='distance')
        # Assign clusters to the sequences
        tot_seq['Cluster'] = clusters
        # Compute mean values per cluster
        val_sce = tot_seq.groupby('Cluster').mean()
        # Set the index to the relative frequency of each cluster
        val_sce.index = round(pd.Series(clusters).value_counts(normalize=True).sort_index(), 2)
        # Store the computed scenarios
        self.val_sce = val_sce
        
    def plot_scenario(self,save=None):
        """
        Plots the scenarios associated with their probability.

        """
        # ensure there is data to plot
        if len(self.val_sce) == 0:
            raise Exception('No scenarios found, please create them before plotting.')
        # Calculate vertical (y-axis) and horizontal (x-axis) bounds
        h_max = max(1,self.val_sce.max().max())
        h_min = max(0,self.val_sce.min().min())
        w_min=0
        w_max= len(self.Shape.values)+len(self.val_sce.columns)-1
        # Determine figure size dynamically based on the data span
        width_span = w_max - w_min
        height_span = h_max - h_min
        fig_width = width_span
        fig_height = height_span * 3

        plt.figure(figsize=(fig_width, fig_height))
        # Plot each scenario
        for sce in range(len(self.val_sce)):
            seq = pd.Series([self.Shape.values[-1]]+self.val_sce.iloc[sce,:].tolist())
            seq.index = range(len(self.Shape.values)-1,len(self.Shape.values)+len(seq)-1)
            plt.plot(seq,label=f'P={self.val_sce.index[sce]}',marker='o')
        # Plot input shape
        plt.plot(pd.Series(self.Shape.values),color='grey',marker='o')
        plt.legend()
        plt.title("Scenarios")
        if save is not None:
            plt.savefig(save, dpi=300, bbox_inches='tight')
        plt.show()
        
    def predict(self, horizon=6, clu_thres=3):
        """
        Predicts future values based on historical sequences using hierarchical clustering.
    
        Args:
            horizon (int): The number of future time steps to predict.
            clu_thres (int): The threshold for clustering, affecting the number of clusters.
    
        Returns:
            pd.Series: The final predicted sequence.
        """
        # Ensure sequences exist before proceeding
        if len(self.sequences) == 0:
            raise Exception('No shape found, please fit before predict.')
        # Extract key statistics from stored sequences
        tot_seq = [
            [series.name, series.index[-1], series.min(), series.max(), series.sum()] 
            for series, weight in self.sequences]
    
        pred_seq = []
        # Generate future sequences for each stored sequence
        for col, last_date, mi, ma, somme in tot_seq:
            date = self.data.index.get_loc(last_date)  # Get index position of the last known date
            if date + horizon < len(self.data):
                # Extract future values for the given column
                seq = self.data.iloc[date + 1 : date + 1 + horizon, self.data.columns.get_loc(col)].reset_index(drop=True)
                # Normalize sequence using min-max scaling
                seq = (seq - mi) / (ma - mi)
                pred_seq.append(seq.tolist())

        tot_seq = pd.DataFrame(pred_seq)
        # Perform hierarchical clustering
        linkage_matrix = linkage(tot_seq, method='ward')
        clusters = fcluster(linkage_matrix, horizon / clu_thres, criterion='distance')
        # Assign clusters to the sequences
        tot_seq['Cluster'] = clusters
        # Compute mean values per cluster
        val_sce = tot_seq.groupby('Cluster').mean()
        # Determine the most frequent cluster
        pr = round(pd.Series(clusters).value_counts(normalize=True).sort_index(), 2)
        # Extract the cluster with the highest frequency
        pred_ori = val_sce.loc[pr == pr.max(), :]
        # Compute the mean prediction across sequences in the most frequent cluster
        pred_ori = pred_ori.mean(axis=0)
        # Retrieve original shape values for denormalization
        seq1 = pd.Series(data=self.Shape.values)
        # Denormalize predictions back to original scale
        preds = pred_ori * (seq1.max() - seq1.min()) + seq1.min()
    
        return preds




# =============================================================================
# ShapeFinder for 3D dataset Autoregressive
# =============================================================================

def compute_overlap(row1, row2):
    # Initialize the overlap and union volumes to 1 (to multiply values in each dimension)
    overlap = 1
    union = 1
    # Loop over each of the 3 dimensions (x, y, z)
    for i in range(3):
        # Extract the low and high bounds of row1 and row2 in the current dimension
        low1, high1 = row1[2*i], row1[2*i+1]
        low2, high2 = row2[2*i], row2[2*i+1]
        # Compute the overlap (intersection) interval in the current dimension
        intersect_low = max(low1, low2)
        intersect_high = min(high1, high2)
        # Compute the union (combined) interval in the current dimension
        union_low = min(low1, low2)
        union_high = max(high1, high2)
        # If there is an overlap in this dimension
        if intersect_high > intersect_low:
            overlap *= (intersect_high - intersect_low)
        else:
            # No overlap in this dimension means the total overlap is zero
            overlap = 0
            break
        # Compute union volume contribution for this dimension
        union *= (union_high - union_low)
    # Return the ratio of the overlapping volume to the union volume (IoU-like measure)
    return overlap / union if union > 0 else 0


def filter_overlaps(df):
    # Repeatedly remove rows until there are no overlaps above the threshold
    while True:
        to_drop = set()  # Keep track of row indices to drop in this iteration
        # Compare each pair of rows in the DataFrame
        for i, row1 in df.iterrows():
            for j, row2 in df.iterrows():
                if i < j:  # Avoid redundant and self-comparisons
                    # Compute the overlap ratio between the two boxes
                    overlap_ratio = compute_overlap(row1[:6], row2[:6])
                    # If the overlap is greater than the threshold (0.25)
                    if overlap_ratio > 0.25:
                        # Drop the one with the lower priority (based on the EMD value)
                        # Keep the one with the smaller value in column 6
                        to_drop.add(i if row1[6] > row2[6] else j)
        # If no rows need to be dropped, we're done
        if not to_drop:
            break
        # Drop the identified rows from the DataFrame
        df = df.drop(index=to_drop)
    # Return the filtered DataFrame with overlaps reduced
    return df

def dtw_distance(x, y):
    return dtw.distance(x, y)

def cluster_based_on_threshold(array_list, threshold):
    # Extract the past futures from each matching cases
    last_column = np.array([arr[:, 3] for arr in array_list])
    # Compute pairwise Euclidean distances between past futures
    distances = squareform(pdist(last_column, metric='euclidean'))
    # Initialize all cluster labels as -1 (unassigned)
    cluster_labels = np.full(len(array_list), -1)
    current_cluster = 0  # Start assigning cluster IDs from 0
    # Iterate through each element to assign cluster labels
    for i in range(len(array_list)):
        if cluster_labels[i] == -1:
            # Assign a new cluster ID to the unassigned element
            cluster_labels[i] = current_cluster
            # Check all following elements for closeness
            for j in range(i + 1, len(array_list)):
                # If the distance is below or equal to the threshold, assign the same cluster
                if distances[i, j] <= threshold:
                    cluster_labels[j] = current_cluster
            # Move to the next cluster label for future elements
            current_cluster += 1
    # Return the cluster labels for all elements
    return cluster_labels


class Shape_3D():
    """
    A class to represent and visualize a 3D shape based on a 3D numpy array.
    
    Attributes:
    -----------
    coordinates : np.array
        Normalized (x, y, z) coordinates of the non-zero elements.
    weights : np.array
        Normalized weights (intensity values) of the non-zero elements.
    dim : tuple
        Original shape (dimensions) of the input 3D array.

    Methods:
    --------
    set_shape(input_shape):
        Parses a 3D numpy array to extract non-zero voxel coordinates and weights.
    
    plot(axis=True, mini_b=0.01):
        Plots the 3D shape using Plotly with a minimum spanning tree overlay.
    """

    def __init__(self, coordinates=None, weights=None, dim=None):
        self.coordinates = coordinates  # Normalized voxel coordinates
        self.weights = weights          # Normalized intensity values
        self.dim = dim                  # Dimensions of the original input array

    def set_shape(self, input_shape):
        """
        Converts a 3D numpy array into a normalized shape representation.
        Non-zero voxels become points with associated weights (intensity values).
        """
        try:
            sub_array = np.array(input_shape)  # Convert input to numpy array (if not already)
            bound_1 = np.array([[0, 0, 0], list(sub_array.shape)])  # Shape bounds for normalization

            # Get indices of non-zero voxels
            non_zero_indices = np.argwhere(sub_array != 0)

            # Convert indices into normalized 3D coordinates
            coordinates = np.array([(idx[0], idx[1], idx[2]) for idx in non_zero_indices])
            coordinates = (coordinates - bound_1.min(axis=0)) / (
                bound_1.max(axis=0) - 1 - bound_1.min(axis=0)
            )

            # Check if there is more than one non-zero element
            if len(non_zero_indices) > 1:
                weights = sub_array[sub_array != 0]

                # Normalize weights to [0, 1]
                weights = weights / np.sum(weights)
            else:
                raise Exception("Please provide Input with more than 1 non-zero value.")

            # Save processed data
            self.coordinates = coordinates
            self.weights = weights
            self.dim = sub_array.shape

        except:
            print('Wrong format, please provide a 3D numpy array input.')

    def plot(self, axis=True, mini_b=0.01):
        """
        Plots the 3D shape using Plotly:
        - Points are colored by weight intensity
        - Minimum spanning tree (MST) connects the points to show structure
        
        Parameters:
        -----------
        axis : bool
            If False, hides the plot axes.
        mini_b : float
            Minimum weight value used for color normalization.
        """
        if self.coordinates is None:
            raise Exception('Please first set the Shape with "set_shape" to then plot it.')

        # Compute pairwise distances between points
        dist_matrix = distance.cdist(self.coordinates, self.coordinates)

        # Generate the Minimum Spanning Tree from the distance matrix
        mst = minimum_spanning_tree(dist_matrix)
        edges = np.transpose(mst.nonzero())  # Get indices of edges in the MST

        # Extract coordinates and weights for plotting
        x, y, z = self.coordinates[:, 0], self.coordinates[:, 1], self.coordinates[:, 2]
        flat_indices = self.weights

        # Set up color mapping using logarithmic normalization
        cmap = cm.get_cmap('Reds')
        norm = mcolors.LogNorm(vmin=mini_b, vmax=flat_indices.max())
        marker_colors = cmap(norm(flat_indices))

        # Plot non-zero points as markers
        fig = go.Figure(data=[
            go.Scatter3d(
                x=x, y=y, z=z,
                mode='markers',
                marker=dict(size=10, color=marker_colors)
            )
        ])

        # Add MST edges as grey lines
        for edge in edges:
            fig.add_trace(go.Scatter3d(
                x=[self.coordinates[edge[0], 0], self.coordinates[edge[1], 0]],
                y=[self.coordinates[edge[0], 1], self.coordinates[edge[1], 1]],
                z=[self.coordinates[edge[0], 2], self.coordinates[edge[1], 2]],
                mode='lines',
                line=dict(color='grey', width=2)
            ))

        # Configure layout
        fig.update_layout(
            scene=dict(
                xaxis_title='x',
                yaxis_title='y',
                zaxis_title='time'
            ),
            title='Shape',
            showlegend=False
        )

        # Optionally hide axes
        if axis == False:
            fig.update_layout(scene=dict(
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                zaxis=dict(visible=False)
            ))

        # Display the plot
        plot(fig, auto_open=True)


class finder_3D():
    """
    A class to identify and predict 3D spatial-temporal patterns
    comparisons between a input shape and historical data.

    Attributes:
    -----------
    data : np.ndarray
        The 3D historical data array to search for patterns.
    Shape_3D : Shape_3D
        An instance of the Shape_3D class used as the input shape.
    sequences : list
        A list to store matched similar patterns.
    df_pred : pd.DataFrame
        DataFrame to store prediction results.
    """

    def __init__(self, data, Shape_3D=Shape_3D(), sequences=[], df_pred=None):
        self.data = data
        self.Shape_3D = Shape_3D
        self.sequences = sequences
        self.df_pred = df_pred

    def find_patterns(self, flex=2, window='half', mode='both', min_emd=0.15,
                      min_ratio=0.15, select=True, min_mat=0):
        """
        Identify subvolumes in the data that closely resemble the Shape_3D pattern.

        Parameters:
        -----------
        flex : int
            Flexibility parameter for stretching/shrinking the window.
        window : str
            Determines the step size ('half' of shape dimension or 'none').
        mode : str
            'both' considers EMD and size similarity; otherwise EMD only.
        min_emd : float
            Minimum threshold for EMD similarity.
        min_ratio : float
            Minimum threshold for size ratio similarity.
        select : bool
            Whether to filter overlapping subvolumes.
        min_mat : int
            Minimum number of matches to retain.
        """

        # Set step sizes based on window mode
        if window == 'half':
            r1 = int(self.Shape_3D.dim[0] / 2)
            r2 = int(self.Shape_3D.dim[1] / 2)
            r3 = int(self.Shape_3D.dim[2] / 2)
        else:
            r1 = r2 = r3 = 1

        dist_arr = []
        # Iterate through 3D data with sliding windows and flexible offsets
        for x in range(0, self.data.shape[0] - int(self.Shape_3D.dim[0] / flex) - self.Shape_3D.dim[0], r1):
            for y in range(0, self.data.shape[1] - int(self.Shape_3D.dim[1] / flex) - self.Shape_3D.dim[1], r2):
                for z in range(0, self.data.shape[2] - int(self.Shape_3D.dim[2] / flex) - self.Shape_3D.dim[2], r3):
                    for x_r in [-int(self.Shape_3D.dim[0] / flex), 0, int(self.Shape_3D.dim[0] / flex)]:
                        for y_r in [-int(self.Shape_3D.dim[1] / flex), 0, int(self.Shape_3D.dim[1] / flex)]:
                            for z_r in [-int(self.Shape_3D.dim[2] / flex), 0, int(self.Shape_3D.dim[2] / flex)]:

                                # Extract subvolume
                                sub_array_2 = self.data[x:x + x_r + self.Shape_3D.dim[0],
                                                        y:y + y_r + self.Shape_3D.dim[1],
                                                        z:z + z_r + self.Shape_3D.dim[2]]
                                # Check if subvolume contains non-zero values
                                if not (sub_array_2.flatten() == 0).all():
                                    bound=np.array([[0,0,0],list(sub_array_2.shape)])
                                    zero_indices_2 = np.argwhere(sub_array_2!=0)
                                    coordinates_2 = [(idx[0],idx[1],idx[2]) for idx in zero_indices_2]
                                    coordinates_2 = np.array(coordinates_2)
                                    coordinates_2 = (coordinates_2 - bound.min(axis=0)) / (bound.max(axis=0)-1 - bound.min(axis=0))
                                    coordinates_2 = np.nan_to_num(coordinates_2, nan=0.5)
                                    if len(zero_indices_2)>1:
                                        weights_2 = sub_array_2[sub_array_2!=0]
                                        weights_2 = weights_2 / np.sum(weights_2)
                                    else:
                                        weights_2=np.array([1])
                                    # Compute Earth Mover’s Distance (EMD)
                                    d_met = ot.dist(self.Shape_3D.coordinates, coordinates_2, metric='euclidean')
                                    d_min = ot.emd2(self.Shape_3D.weights, weights_2, d_met)

                                    # Rotate subvolume for better match (0–3 rotations)
                                    best_rota = 0
                                    for i in range(3):
                                        sub_array_3 = np.rot90(sub_array_2, k=i+1, axes=(0, 1))
                                        non_zero_indices_3 = np.argwhere(sub_array_3 != 0)
                                        bound=np.array([[0,0,0],list(sub_array_3.shape)])
                                        coordinates_3 = [(idx[0], idx[1], idx[2]) for idx in non_zero_indices_3]
                                        coordinates_3 = np.array(coordinates_3)
                                        coordinates_3 = (coordinates_3 - bound.min(axis=0)) / (bound.max(axis=0)-1 - bound.min(axis=0))
                                        coordinates_3 = np.nan_to_num(coordinates_3, nan=0.5)
                                        weights_3 = sub_array_3[sub_array_3!=0]
                                        weights_3 = weights_3 / np.sum(weights_3)
                                        d_met = ot.dist(self.Shape_3D.coordinates, coordinates_3, metric='euclidean')
                                        d_sub = ot.emd2(self.Shape_3D.weights, weights_3, d_met)
                                        if d_min > d_sub:
                                            d_min = d_sub
                                            best_rota = i + 1

                                    # Store results: coordinates, EMD, rotation, size ratio
                                    dist_arr.append([
                                        x, x + x_r + self.Shape_3D.dim[0],
                                        y, y + y_r + self.Shape_3D.dim[1],
                                        z, z + z_r + self.Shape_3D.dim[2],
                                        d_min, best_rota,
                                        abs(tanh(np.log(len(weights_2) / len(self.Shape_3D.weights))))
                                    ])
        dist_arr = pd.DataFrame(dist_arr)

        # Combine EMD and ratio if mode is 'both'
        dist_arr['Sum'] = dist_arr[6] + dist_arr[8] if mode == 'both' else dist_arr[6]
        dist_arr = dist_arr.sort_values('Sum').iloc[:1000]

        # Filter overlapping shapes
        if select:
            dist_arr = filter_overlaps(dist_arr)

        # Final selection based on thresholds
        if mode == 'both':
            dist_arr_sub = dist_arr[(dist_arr[6] < min_emd) & (dist_arr[8] < min_ratio)]
        else:
            dist_arr_sub = dist_arr[dist_arr[6] < min_emd]

        # Ensure at least `min_mat` matches
        if len(dist_arr_sub) < min_mat:
            dist_arr_sub = dist_arr.iloc[:min_mat, :]

        self.sequences = dist_arr_sub

    def predict(self, h, thres_clu):
        """
        Predict future values by projecting matched patterns forward.

        Parameters:
        -----------
        h : int
            Number of steps ahead to predict.
        thres_clu : float
            Threshold to determine cluster maximum distance.
        Other params are passed to find_patterns if no sequences are present.
        
        Returns:
        --------
        df_pred : pd.DataFrame
            A DataFrame with future predictions.
        """
        if len(self.sequences) == 0:
            raise Exception('No shape found, please fit before predict.')

        # Create base 3D grid for prediction
        source_coor = np.meshgrid(np.arange(self.Shape_3D.dim[0]),
                                  np.arange(self.Shape_3D.dim[1]),
                                  np.arange(h), indexing='ij')
        source_np = np.column_stack([a.ravel() for a in source_coor])
        l_mat = []

        # Process each matched subvolume
        for i in range(len(self.sequences)):
        
            # Get the future subvolume (length h) that starts right after the matched pattern
            sub_a = self.data[
                self.sequences.iloc[i, 0]:self.sequences.iloc[i, 1],
                self.sequences.iloc[i, 2]:self.sequences.iloc[i, 3],
                self.sequences.iloc[i, 5]:self.sequences.iloc[i, 5] + h
            ]
        
            # Rotate subvolume to align it the same way as the matched pattern
            sub_a = np.rot90(sub_a, k=self.sequences.iloc[i, 7], axes=(0, 1))
        
            # Grab the matching pattern that came before the prediction horizon
            matc = self.data[
                self.sequences.iloc[i, 0]:self.sequences.iloc[i, 1],
                self.sequences.iloc[i, 2]:self.sequences.iloc[i, 3],
                self.sequences.iloc[i, 4]:self.sequences.iloc[i, 5]
            ]
        
            # Normalize the future subvolume using the min/max of the matched pattern
            sub_a = (sub_a - matc.min()) / (matc.max() - matc.min())
        
            # Create meshgrid for normalized x, y, z coordinates
            x_coords, y_coords, z_coords = np.meshgrid(
                np.arange(sub_a.shape[0]),
                np.arange(sub_a.shape[1]),
                np.arange(sub_a.shape[2]),
                indexing='ij'
            )
        
            # Normalize coordinates to [0, 1]
            x_norm = x_coords.ravel() / x_coords.max()
            y_norm = y_coords.ravel() / y_coords.max()
            z_norm = z_coords.ravel() / z_coords.max()
        
            # Flatten subvolume and stack with coordinates
            sub_a = sub_a.reshape(-1, 1)
            sub_a = np.column_stack((x_norm, y_norm, z_norm, sub_a.ravel()))
        
            # Rescale coordinates back to match expected Shape_3D resolution
            sub_a[:, :3] *= tuple(np.array(list(self.Shape_3D.dim[:2]) + [h]) - 1)
        
            # If the matrix is smaller than expected, pad it with zeros at missing positions
            if len(sub_a) < self.Shape_3D.dim[0] * self.Shape_3D.dim[1] * h:
                sub_a[:, :3] = np.round(sub_a[:, :3]).astype(int)
                for row in source_np:
                    if not np.any(np.all(sub_a[:, :3] == row, axis=1)):
                        new_row = np.append(row, 0)
                        sub_a = np.vstack([sub_a, new_row])
        
                # Reorder so it's in the same grid order as source_np
                reordered_sub_a = np.zeros_like(sub_a)
                for ki, row in enumerate(source_np):
                    index = np.where(np.all(sub_a[:, :3] == row, axis=1))[0][0]
                    reordered_sub_a[ki] = sub_a[index]
                sub_a = reordered_sub_a.copy()
        
                # Handle possible duplicates just in case
                if len(sub_a) > self.Shape_3D.dim[0] * self.Shape_3D.dim[1] * h:
                    sub_a[:, :3] = np.round(sub_a[:, :3]).astype(int)
                    unique_rows, indices, inverse_indices = np.unique(sub_a[:, :3], axis=0, return_index=True, return_inverse=True)
                    means_sub = np.zeros((unique_rows.shape[0], sub_a.shape[1]))
                    means_sub[:, :3] = unique_rows
                    means_sub[:, 3] = np.bincount(inverse_indices, weights=sub_a[:, 3])
                    sub_a = means_sub.copy()
        
            # If the matrix is larger than expected, merge duplicates
            elif len(sub_a) > self.Shape_3D.dim[0] * self.Shape_3D.dim[1] * h:
                sub_a[:, :3] = np.round(sub_a[:, :3]).astype(int)
                unique_rows, indices, inverse_indices = np.unique(sub_a[:, :3], axis=0, return_index=True, return_inverse=True)
                means_sub = np.zeros((unique_rows.shape[0], sub_a.shape[1]))
                means_sub[:, :3] = unique_rows
                means_sub[:, 3] = np.bincount(inverse_indices, weights=sub_a[:, 3])
                sub_a = means_sub.copy()
        
                # Check again for missing entries and pad with zeros
                if len(sub_a) < self.Shape_3D.dim[0] * self.Shape_3D.dim[1] * h:
                    for row in source_np:
                        if not np.any(np.all(sub_a[:, :3] == row, axis=1)):
                            new_row = np.append(row, 0)
                            sub_a = np.vstack([sub_a, new_row])
                    reordered_sub_a = np.zeros_like(sub_a)
                    for ki, row in enumerate(source_np):
                        index = np.where(np.all(sub_a[:, :3] == row, axis=1))[0][0]
                        reordered_sub_a[ki] = sub_a[index]
                    sub_a = reordered_sub_a.copy()
        
            # Add to the list of matrices used for ensemble prediction
            l_mat.append(sub_a)

        # Cluster matched volumes to reduce noise
        cluster_labels = cluster_based_on_threshold(l_mat, (self.Shape_3D.dim[0]*self.Shape_3D.dim[1]*h/thres_clu))
        l_mat_sub = [l_mat[i] for i in range(len(cluster_labels)) if pd.Series(cluster_labels).value_counts().loc[cluster_labels[i]] == pd.Series(cluster_labels).value_counts().max()]
        last_sub_val = np.array([arr[:, 3] for arr in l_mat_sub]).mean(axis=0)

        # Store prediction
        df_pred = pd.DataFrame(np.hstack((source_np, last_sub_val.reshape(-1, 1))),
                               columns=['x', 'y', 'time', 'pred'])
        df_pred['time'] += self.Shape_3D.dim[2]
        self.df_pred = df_pred
        return df_pred

    def plot_predict(self, axis_show=True, mini_b=0.01):
        # Check if predictions have been generated
        if self.df_pred is None:
            raise Exception('Please create the prediction with "predict" to then plot it.')
    
        # Resize coordinates to match the shape dimensions
        coor_resize = self.Shape_3D.coordinates[:, :3] * (tuple(d - 1 for d in self.Shape_3D.dim))
        x, y, z = coor_resize[:, 0], coor_resize[:, 1], coor_resize[:, 2]
        
        # Set color mapping for coordinates using a greyscale colormap
        cmap = cm.get_cmap('Greys')
        norm = mcolors.LogNorm(vmin=0.01, vmax=self.Shape_3D.coordinates.max())
        marker_colors = cmap(norm(self.Shape_3D.weights))  # Normalize based on weights
    
        # Extract prediction coordinates and colorize them based on the prediction's value
        x_pred, y_pred, z_pred = np.array(self.df_pred.iloc[:, 0]), np.array(self.df_pred.iloc[:, 1]), np.array(self.df_pred.iloc[:, 2])
        cmap_pred = cm.get_cmap('Reds')  # Colormap for predictions
        marker_colors_pred = cmap_pred(norm(np.array(self.df_pred.iloc[:, -1])))  # Normalize predicted weights
    
        # Combine the resized coordinates and the weights into a single array for plotting
        coordinates_tot = np.hstack((coor_resize, self.Shape_3D.weights.reshape(-1, 1)))
        coordinates_tot = np.vstack((coordinates_tot, np.array(self.df_pred)))
        coordinates_tot = coordinates_tot[coordinates_tot[:, 3] > 0]  # Filter out rows with zero weight
        weight_tot = coordinates_tot[:, 3]  # Extract weights for further processing
        coordinates_tot = coordinates_tot[:, :3]  # Only keep the 3D coordinates
    
        # Compute pairwise distances between all points in the combined coordinates
        dist_matrix = distance.cdist(coordinates_tot, coordinates_tot)
    
        # Compute the Minimum Spanning Tree (MST) from the distance matrix
        mst = minimum_spanning_tree(dist_matrix)
    
        # Extract the edges of the MST
        edges = np.transpose(mst.nonzero())
    
        # Create a 3D plot using Plotly
        fig = go.Figure()
    
        # Add prediction points as a scatter plot (in red)
        fig.add_trace(go.Scatter3d(
            x=x_pred, y=y_pred, z=z_pred,
            mode='markers',
            marker=dict(size=10, color=marker_colors_pred),
            customdata=np.array(self.df_pred.iloc[:, -1]).reshape(-1, 1),
            hovertemplate="Value: %{customdata[0]:.2f}<extra></extra>"
        ))
    
        # Add original points as a scatter plot (in grey)
        fig.add_trace(go.Scatter3d(
            x=x, y=y, z=z,
            mode='markers',
            marker=dict(size=10, color=marker_colors),
            customdata=self.Shape_3D.weights.reshape(-1, 1),
            hovertemplate="Value: %{customdata[0]:.2f}<extra></extra>"
        ))
    
        # Add edges of the MST to the plot (connecting the points)
        for edge in edges:
            fig.add_trace(go.Scatter3d(
                x=[coordinates_tot[edge[0], 0], coordinates_tot[edge[1], 0]],
                y=[coordinates_tot[edge[0], 1], coordinates_tot[edge[1], 1]],
                z=[coordinates_tot[edge[0], 2], coordinates_tot[edge[1], 2]],
                mode='lines',
                line=dict(color='grey', width=2),
                hoverinfo='skip'
            ))
    
        # Update layout with axis labels and a title
        fig.update_layout(scene=dict(
                            xaxis_title='x',
                            yaxis_title='y',
                            zaxis_title='time'),
                          title='Shape(Grey) + Prediction(Red)',
                          showlegend=False)
    
        # Optionally hide axis labels and gridlines
        if axis_show == False:
            fig.update_layout(scene=dict(
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                zaxis=dict(visible=False)
            ))
    
        # Display the plot
        plot(fig, auto_open=True)



# =============================================================================
# ShapeFinder with covaraites as shapes
# =============================================================================

class finder_multi():
    
    """
    Find sequences in the data similar to a target pattern (Shape) and optional covariate patterns.
    
    Parameters:
    - data: pandas DataFrame, main dataset to search.
    - cov: list of pandas DataFrames, covariates corresponding to data.
    - Shape: object containing the target shape to match (default: empty Shape()).
    - Shape_cov: list of shape objects representing covariates (default: None).
    - sequences: list to store matched sequences from 'data'.
    - sequences_cov: list to store matched sequences from covariates.
    """
    
    def __init__(self,data,cov,Shape=Shape(),Shape_cov=None,sequences=[],sequences_cov=[]):
        # Initialize the finder with primary and covariate data
        self.data=data
        self.cov=cov
        self.Shape=Shape
        self.Shape_cov=Shape_cov
        self.sequences=sequences
        self.sequences_cov=sequences_cov
        
    def plot_inputs(self):
        # Plot the input shape and covariates used for pattern matching
        if len(self.Shape_cov) == 0:
            raise Exception("Sorry, no input to plot.")
    
        num_plots = len(self.Shape_cov)+1
        grid_size = math.isqrt(num_plots)  # integer square root
        if grid_size * grid_size < num_plots:  # If not a perfect square
            grid_size += 1

        subplot_width = 7
        subplot_height = 5
        fig, axs = plt.subplots(grid_size, grid_size, figsize=(subplot_width * grid_size, subplot_height * grid_size))

        if num_plots > 1:
            axs = axs.ravel()
        if not isinstance(axs, np.ndarray):
            axs = np.array([axs])

        for i in range(num_plots):
            if i==0:
                axs[i].plot(pd.Series(self.Shape.values), marker='o')
                axs[i].set_xlabel('Time')
                axs[i].set_title("Main Variable", style='italic', color='grey')
            else:
                axs[i].plot(pd.Series(self.Shape_cov[i-1].values), marker='o')
                axs[i].set_xlabel('Date')
                axs[i].set_title(f"Variable {i}", style='italic', color='grey')

        if grid_size * grid_size > num_plots:
            # If there are extra subplot spaces in the grid, remove them
            for j in range(i + 1, grid_size * grid_size):
                fig.delaxes(axs[j])

        plt.tight_layout()
        plt.suptitle('Input',y=1.02)
        plt.show()
        
    def find_patterns(self, metric='euclidean', min_d=0.5, dtw_sel=0, select=True,weight=None, min_mat=0):
        """
        Find patterns in the data similar to the input shape and covariates.
        
        Parameters:
        - metric: 'euclidean' or 'dtw' for distance metric
        - min_d: distance threshold
        - dtw_sel: DTW tolerance window
        - select: whether to filter overlapping results
        - weight: weights for main and covariate distances
        - min_mat: minimum number of matches
        """
        # Clear any previously stored sequences
        self.sequences = []
        self.sequences_cov = []
        
        # Check if dtw_sel is zero when metric is 'euclidean'
        if metric=='euclidean':
            dtw_sel=0
        if weight==None:
            weight=[1]+[1]*(len(self.Shape_cov))
        # Convert custom shape values to a pandas Series and normalize it
        seq1 = pd.Series(data=self.Shape.values)
        if seq1.var() != 0.0:
            seq1 = (seq1 - seq1.min()) / (seq1.max() - seq1.min())
        seq1 = np.array(seq1)
        
        seq1_cov=[]
        for i in self.Shape_cov:
            val = pd.Series(i.values)
            if val.var() != 0.0:
                i_n = (val - val.min()) / (val.max() - val.min())
            seq1_cov.append(np.array(i_n))
        # Initialize the list to store the found sequences that match the custom shape
        tot = []
        for col in self.data.columns:
            # try:
            for time in self.data.loc[:,col].index:
                flag=False
                if dtw_sel == 0:
                    # Loop through the testing sequence
                    if len(self.data.loc[time:,col].iloc[:len(seq1)])==len(seq1):
                        seq2 = self.data.loc[time:,col].iloc[:len(seq1)]
                        last_d=seq2.index[-1]
                        seq2 = (seq2 - seq2.min()) / (seq2.max() - seq2.min())
                        # try:
                        if metric == 'euclidean':
                            # Calculate the Euclidean distance between the custom shape and the current window
                            dist = ed.distance(seq1, seq2)*weight[0]
                        elif metric == 'dtw':
                            # Calculate the Dynamic Time Warping distance between the custom shape and the current window
                            dist = dtw.distance(seq1, seq2)*weight[0]
                        c_cov=0    
                        for cov_shape in seq1_cov:
                            seq_cov = self.cov[c_cov].loc[:last_d,col].iloc[-len(cov_shape):]
                            if len(seq_cov)!=len(seq1_cov[c_cov]):
                                flag=True
                            seq_cov = (seq_cov - seq_cov.min()) / (seq_cov.max() - seq_cov.min())
                            if metric == 'euclidean':
                                # Calculate the Euclidean distance between the custom shape and the current window
                                dist = dist + ed.distance(cov_shape, seq_cov)*weight[1+c_cov]
                            elif metric == 'dtw':
                                # Calculate the Dynamic Time Warping distance between the custom shape and the current window
                                dist = dist + dtw.distance(cov_shape, seq_cov)*weight[1+c_cov]
                            c_cov += 1
                        if flag==False:    
                            tot.append([last_d,col,dist, self.Shape.window,0])

                else:
                    # Loop through the range of window size variations (dtw_sel)
                    for lop in range(int(-dtw_sel), int(dtw_sel) + 1):
                        if len(self.data.loc[time:,col].iloc[:len(seq1)+ lop])==len(seq1)+ lop:
                            seq2 = self.data.loc[time:,col].iloc[:len(seq1)+ lop]
                            last_d=seq2.index[-1]
                            seq2 = (seq2 - seq2.min()) / (seq2.max() - seq2.min())
                            dist = dtw.distance(seq1, seq2)*weight[0]
                            c_cov=0    
                            for cov_shape in seq1_cov:
                                seq_cov = self.cov[c_cov].loc[:last_d,col].iloc[-(len(cov_shape)+lop):]
                                seq_cov = (seq_cov - seq_cov.min()) / (seq_cov.max() - seq_cov.min())
                                if len(seq_cov)!=len(seq1_cov[c_cov])+lop:
                                    flag=True
                                dist = dist + dtw.distance(cov_shape, seq_cov)*weight[1+c_cov]
                                c_cov += 1
                            if flag==False:       
                                tot.append([last_d,col, dist, self.Shape.window,lop])
                                
        # Prepare results DataFrame
        tot=pd.DataFrame(tot) 
        tot = tot.sort_values([2])
        totu = tot[tot[2]<min_d]
        if len(totu) < min_mat:
            tot = tot.iloc[:min_mat, :]
        else:
            tot = totu.copy()
              
        s1=[]
        s_c=[[] for _ in range(len(self.Shape_cov))]
        if len(tot) > 0:
            for ca in range(len(tot)):
                s1.append((self.data.loc[:tot.iloc[ca,0],tot.iloc[ca,1]].iloc[-tot.iloc[ca,3]+tot.iloc[ca,4]:],tot.iloc[ca,2]))
                for num in range(len(self.Shape_cov)):
                    s_c[num].append(self.cov[num].loc[:tot.iloc[ca,0],tot.iloc[ca,1]].iloc[-self.Shape_cov[num].window+tot.iloc[ca,4]:])
            
            if select:
                # Create a dictionary to store lists of Series by name
                series_dict = {}
                kept = []
            
                # Iterate through the data list
                for idx, (series, value) in enumerate(s1):
                    series_name = series.name
            
                    # Check if there are any Series with the same name in the dictionary
                    if series_name in series_dict:
                        # Get the list of series and values associated with this name
                        series_values = series_dict[series_name]
                        index_set = set(series.index)
                        existing_flag = False
            
                        # Iterate over the list of (series, value) pairs
                        for i, (existing_series, existing_value, existing_idx) in enumerate(series_values):
                            # Calculate the intersection of indices
                            intersection = index_set.intersection(existing_series.index)
            
                            # Check if the intersection is more than 50% of the existing series index
                            if len(intersection) > 0.5 * len(existing_series.index):
                                # Check the value, and if the new series is 'better', update the info
                                if value < existing_value:
                                    series_values[i] = (series, value, idx)
                                    if existing_idx in kept:
                                        kept.remove(existing_idx)
                                    kept.append(idx)
                                    existing_flag = True
                                    break
                                else:
                                    existing_flag = True
            
                        # If the new series does not intersect more than 50% with any existing series, add it
                        if not existing_flag:
                            series_values.append((series, value, idx))
                            kept.append(idx)
            
                        series_dict[series_name] = series_values  # Update the dictionary entry
            
                    else:
                        # If the Series name is not in the dictionary, add it
                        series_dict[series_name] = [(series, value, idx)]
                        kept.append(idx)
            
                # Flatten the values from the dictionary and return them as a list
                resu_l = [item for sublist in series_dict.values() for item in sublist]
                s1 = [(resu[0], resu[1]) for resu in resu_l]  # Drop the index from the result
                nb = 0
                for sequ in s_c:
                    f_seq = []
                    c_cov = 0
                    for sub in sequ:
                        if c_cov in kept:
                            f_seq.append(sub)
                        c_cov += 1
                    s_c[nb] = f_seq
                    nb += 1

            self.sequences = s1
            self.sequences_cov = s_c
            
        else:
            print('No patterns found')
            
            
    def plot_sequences(self,how='units',cov=False):
        """
        Plots the found sequences matching the custom shape.

        Args:
            how (str, optional): 'units' to plot each sequence separately or 'total' to plot all sequences together. Defaults to 'units'.

        Raises:
            Exception: If no patterns were found, raises an exception indicating no patterns to plot.
        """
        # Check if any sequences were found, otherwise raise an exception
        if len(self.sequences) == 0:
            raise Exception("Sorry, no patterns to plot.")
    
        if how == 'units':
            # Plot each sequence separately
            for i in range(len(self.sequences)):
                plt.plot(self.sequences[i][0], marker='o')
                plt.xlabel('Date')
                plt.ylabel('Values')  # Corrected typo in xlabel -> ylabel
                plt.suptitle(str(self.sequences[i][0].name), y=1.02, fontsize=15)
                plt.title("d = " + str(self.sequences[i][1]), style='italic', color='grey')
                plt.show()
    
        elif how == 'total':
            # Plot all sequences together in a grid layout
            num_plots = len(self.sequences)
            grid_size = math.isqrt(num_plots)  # integer square root
            if grid_size * grid_size < num_plots:  # If not a perfect square
                grid_size += 1
    
            subplot_width = 7
            subplot_height = 5
            fig, axs = plt.subplots(grid_size, grid_size, figsize=(subplot_width * grid_size, subplot_height * grid_size))
    
            if num_plots > 1:
                axs = axs.ravel()
            if not isinstance(axs, np.ndarray):
                axs = np.array([axs])
    
            for i in range(num_plots):
                axs[i].plot(self.sequences[i][0], marker='o')
                axs[i].set_xlabel('Date')
                axs[i].set_title(f"{self.sequences[i][0].name}\nd = {self.sequences[i][1]}", style='italic', color='grey')
    
            if grid_size * grid_size > num_plots:
                # If there are extra subplot spaces in the grid, remove them
                for j in range(i + 1, grid_size * grid_size):
                    fig.delaxes(axs[j])
    
            plt.tight_layout()
            plt.suptitle('Main Variable',y=1.02)
            plt.show()
            
            if cov==True:
                for covi in range(len(self.sequences_cov)):
                    num_plots = len(self.sequences_cov[covi])
                    grid_size = math.isqrt(num_plots)  # integer square root
                    if grid_size * grid_size < num_plots:  # If not a perfect square
                        grid_size += 1
            
                    subplot_width = 7
                    subplot_height = 5
                    fig, axs = plt.subplots(grid_size, grid_size, figsize=(subplot_width * grid_size, subplot_height * grid_size))
            
                    if num_plots > 1:
                        axs = axs.ravel()
                    if not isinstance(axs, np.ndarray):
                        axs = np.array([axs])
            
                    for i in range(num_plots):
                        axs[i].plot(self.sequences_cov[covi][i], marker='o')
                        axs[i].set_xlabel('Date')
                        axs[i].set_title(f"{self.sequences[i][0].name}\nd = {self.sequences[i][1]}", style='italic', color='grey')
            
                    if grid_size * grid_size > num_plots:
                        # If there are extra subplot spaces in the grid, remove them
                        for j in range(i + 1, grid_size * grid_size):
                            fig.delaxes(axs[j])
            
                    plt.tight_layout()
                    plt.suptitle('Variable '+str(covi+1),y=1.02)
                    plt.show()
                    
            
    def create_sce(self,horizon=6,clu_thres=3):
        """
        Creates scenarios based on matched series in historical data.
        
        Args:
            horizon (int): The number of future time steps to consider for scenario creation.
            clu_thres (int): The threshold for clustering, influencing the number of clusters.
        
        """
        # Ensure sequences exist before proceeding
        if len(self.sequences) == 0:
            raise Exception('No shape found, please fit before predict.')
    
        # Extract key stats from stored sequences
        tot_seq = [
            [series.name, series.index[-1], series.min(), series.max(), series.sum()] 
            for series, weight in self.sequences]
    
        pred_seq = []
        # Generate future sequences for each stored sequence
        for col, last_date, mi, ma, somme in tot_seq:
            date = self.data.index.get_loc(last_date)  # Get index position of the last known date
            # Ensure there are enough future values for the specified horizon
            if date + horizon < len(self.data):
                # Extract future values for the given column
                seq = self.data.iloc[date + 1 : date + 1 + horizon, self.data.columns.get_loc(col)].reset_index(drop=True)
                # Normalize sequence using min-max scaling
                seq = (seq - mi) / (ma - mi)
                pred_seq.append(seq.tolist())
    
        # Convert sequences to a DataFrame
        tot_seq = pd.DataFrame(pred_seq)
        # Perform hierarchical clustering
        linkage_matrix = linkage(tot_seq, method='ward')
        clusters = fcluster(linkage_matrix, horizon / clu_thres, criterion='distance')
        # Assign clusters to the sequences
        tot_seq['Cluster'] = clusters
        # Compute mean values per cluster
        val_sce = tot_seq.groupby('Cluster').mean()
        # Set the index to the relative frequency of each cluster
        val_sce.index = round(pd.Series(clusters).value_counts(normalize=True).sort_index(), 2)
        # Store the computed scenarios
        self.val_sce = val_sce

   
    def predict(self, horizon=6, clu_thres=3):
        """
        Predicts future values based on historical sequences using hierarchical clustering.
    
        Args:
            horizon (int): The number of future time steps to predict.
            clu_thres (int): The threshold for clustering, affecting the number of clusters.
    
        Returns:
            pd.Series: The final predicted sequence.
        """
        # Ensure sequences exist before proceeding
        if len(self.sequences) == 0:
            raise Exception('No shape found, please fit before predict.')
        # Extract key statistics from stored sequences
        tot_seq = [
            [series.name, series.index[-1], series.min(), series.max(), series.sum()] 
            for series, weight in self.sequences]
    
        pred_seq = []
        # Generate future sequences for each stored sequence
        for col, last_date, mi, ma, somme in tot_seq:
            date = self.data.index.get_loc(last_date)  # Get index position of the last known date
            if date + horizon < len(self.data):
                # Extract future values for the given column
                seq = self.data.iloc[date + 1 : date + 1 + horizon, self.data.columns.get_loc(col)].reset_index(drop=True)
                # Normalize sequence using min-max scaling
                seq = (seq - mi) / (ma - mi)
                pred_seq.append(seq.tolist())

        tot_seq = pd.DataFrame(pred_seq)
        # Perform hierarchical clustering
        linkage_matrix = linkage(tot_seq, method='ward')
        clusters = fcluster(linkage_matrix, horizon / clu_thres, criterion='distance')
        # Assign clusters to the sequences
        tot_seq['Cluster'] = clusters
        # Compute mean values per cluster
        val_sce = tot_seq.groupby('Cluster').mean()
        # Determine the most frequent cluster
        pr = round(pd.Series(clusters).value_counts(normalize=True).sort_index(), 2)
        # Extract the cluster with the highest frequency
        pred_ori = val_sce.loc[pr == pr.max(), :]
        # Compute the mean prediction across sequences in the most frequent cluster
        pred_ori = pred_ori.mean(axis=0)
        # Retrieve original shape values for denormalization
        seq1 = pd.Series(data=self.Shape.values)
        # Denormalize predictions back to original scale
        preds = pred_ori * (seq1.max() - seq1.min()) + seq1.min()
    
        return preds


# =============================================================================
# ShapeFinder with covaraites as static values
# =============================================================================

def weighted_mean(group):
    weights = group['weight']
    return np.average(group.drop(columns=['Cluster', 'weight']), axis=0, weights=weights)

class finder_multi_static():
    
    def __init__(self,data,cov,Shape=Shape(),Shape_cov=None,input_cov=[],sequences=[]):
        self.data=data
        self.cov=cov
        self.Shape=Shape
        self.input_cov=input_cov
        self.sequences=sequences
        
    def find_patterns(self, mode='include', metric='euclidean', min_d=0.5, dtw_sel=0, select=True,weight=None, min_mat=0):
        
        # Clear any previously stored sequences
        self.sequences = []
        
        # Check if dtw_sel is zero when metric is 'euclidean'
        if metric=='euclidean':
            dtw_sel=0
        if weight==None:
            weight=[1]+[1]*(len(self.input_cov))
        # Convert custom shape values to a pandas Series and normalize it
        seq1 = pd.Series(data=self.Shape.values)
        if seq1.var() != 0.0:
            seq1 = (seq1 - seq1.min()) / (seq1.max() - seq1.min())
        seq1 = np.array(seq1)
        
        # Initialize the list to store the found sequences that match the custom shape
        tot = []
        for col in self.data.columns:
            # try:
            for time in self.data.loc[:,col].index:
                if dtw_sel == 0:
                    # Loop through the testing sequence
                    if len(self.data.loc[time:,col].iloc[:len(seq1)])==len(seq1):
                        seq2 = self.data.loc[time:,col].iloc[:len(seq1)]
                        last_d=seq2.index[-1]
                        seq2 = (seq2 - seq2.min()) / (seq2.max() - seq2.min())
                        # try:
                        if metric == 'euclidean':
                            # Calculate the Euclidean distance between the custom shape and the current window
                            dist = ed.distance(seq1, seq2)*weight[0]
                        elif metric == 'dtw':
                            # Calculate the Dynamic Time Warping distance between the custom shape and the current window
                            dist = dtw.distance(seq1, seq2)*weight[0]
                        c_cov=0    
                        dist_cov=0
                        for cov_num in self.input_cov:
                            seq_cov = self.cov[c_cov].loc[last_d,col]
                            dist_cov = dist_cov + abs(seq_cov-cov_num)*weight[1+c_cov]
                            c_cov += 1
                        tot.append([last_d,col,dist, self.Shape.window,0,dist_cov])

                else:
                    # Loop through the range of window size variations (dtw_sel)
                    for lop in range(int(-dtw_sel), int(dtw_sel) + 1):
                        if len(self.data.loc[time:,col].iloc[:len(seq1)+ lop])==len(seq1)+ lop:
                            seq2 = self.data.loc[time:,col].iloc[:len(seq1)+ lop]
                            last_d=seq2.index[-1]
                            seq2 = (seq2 - seq2.min()) / (seq2.max() - seq2.min())
                            dist = dtw.distance(seq1, seq2)*weight[0]
                            c_cov=0    
                            dist_cov=0
                            for cov_num in self.input_cov:
                                seq_cov = self.cov[c_cov].loc[last_d,col]
                                dist_cov = dist_cov + abs(seq_cov-cov_num)*weight[1+c_cov]
                                c_cov += 1       
                            tot.append([last_d,col, dist,self.Shape.window,lop,dist_cov])
        if mode=='include':
            tot=pd.DataFrame(tot) 
            tot['both']=tot[2]+tot[5]
            tot = tot.sort_values(['both'])
            totu = tot[tot['both']<min_d]
            if len(totu) < min_mat:
                tot = tot.iloc[:min_mat, :]
            else:
                tot = totu.copy()
        else:    
            tot=pd.DataFrame(tot) 
            tot = tot.sort_values([2])
            totu = tot[tot[2]<min_d]
            if len(totu) < min_mat:
                tot = tot.iloc[:min_mat, :]
            else:
                tot = totu.copy()
              
        s1=[]
        for ca in range(len(tot)):
            s1.append((self.data.loc[:tot.iloc[ca,0],tot.iloc[ca,1]].iloc[-tot.iloc[ca,3]+tot.iloc[ca,4]:],tot.iloc[ca,2],tot.iloc[ca,5]))
        if select:
            # Create a dictionary to store lists of Series by name
            series_dict = {}

            # Iterate through the data list
            for idx, (series, value, weight_cov) in enumerate(s1):
                series_name = series.name
                # Check if there are any Series with the same name in the dictionary
                if series_name in series_dict:
                    # Get the list of series and values associated with this name
                    series_values = series_dict[series_name]
                    index_set = set(series.index)
                    existing_flag = False
        
                    # Iterate over the list of (series, value) pairs
                    for i, (existing_series, existing_value, existing_idx, existing_weight_cov) in enumerate(series_values):
                        # Calculate the intersection of indices
                        intersection = index_set.intersection(existing_series.index)

                        # Check if the intersection is more than 50% of the existing series index
                        if len(intersection) > 0.5 * len(existing_series.index):
                            # Check the value, and if the new series is 'better', update the info
                            if value < existing_value:
                                series_values[i] = (series, value, idx, weight_cov)
                                existing_flag = True
                                break
                            else:
                                existing_flag = True
                    # If the new series does not intersect more than 50% with any existing series, add it
                    if not existing_flag:
                        series_values.append((series, value, idx, weight_cov))

                    series_dict[series_name] = series_values  # Update the dictionary entry
        
                else:
                    # If the Series name is not in the dictionary, add it
                    series_dict[series_name] = [(series, value, idx, weight_cov)]

            # Flatten the values from the dictionary and return them as a list
            resu_l = [item for sublist in series_dict.values() for item in sublist]
            s1 = [(resu[0], resu[1],resu[3]) for resu in resu_l]  # Drop the index from the result
        self.sequences = s1
        
            
    def plot_sequences(self,how='units'):
        """
        Plots the found sequences matching the custom shape.

        Args:
            how (str, optional): 'units' to plot each sequence separately or 'total' to plot all sequences together. Defaults to 'units'.

        Raises:
            Exception: If no patterns were found, raises an exception indicating no patterns to plot.
        """
        # Check if any sequences were found, otherwise raise an exception
        if len(self.sequences) == 0:
            raise Exception("Sorry, no patterns to plot.")
    
        if how == 'units':
            # Plot each sequence separately
            for i in range(len(self.sequences)):
                plt.plot(self.sequences[i][0], marker='o')
                plt.xlabel('Date')
                plt.ylabel('Values')  # Corrected typo in xlabel -> ylabel
                plt.suptitle(str(self.sequences[i][0].name), y=1.02, fontsize=15)
                plt.title("d = " + str(self.sequences[i][1]), style='italic', color='grey')
                plt.show()
    
        elif how == 'total':
            # Plot all sequences together in a grid layout
            num_plots = len(self.sequences)
            grid_size = math.isqrt(num_plots)  # integer square root
            if grid_size * grid_size < num_plots:  # If not a perfect square
                grid_size += 1
    
            subplot_width = 7
            subplot_height = 5
            fig, axs = plt.subplots(grid_size, grid_size, figsize=(subplot_width * grid_size, subplot_height * grid_size))
    
            if num_plots > 1:
                axs = axs.ravel()
            if not isinstance(axs, np.ndarray):
                axs = np.array([axs])
    
            for i in range(num_plots):
                axs[i].plot(self.sequences[i][0], marker='o')
                axs[i].set_xlabel('Date')
                axs[i].set_title(f"{self.sequences[i][0].name}\nd = {self.sequences[i][1]}\nd_cov = {self.sequences[i][2]}", style='italic', color='grey')
    
            if grid_size * grid_size > num_plots:
                # If there are extra subplot spaces in the grid, remove them
                for j in range(i + 1, grid_size * grid_size):
                    fig.delaxes(axs[j])
    
            plt.tight_layout()
            plt.suptitle('Similar Patterns',y=1.02)
            plt.show()
            
            
    def create_sce(self,horizon=6,mode='b-cluster',clu_thres=3):
        """
        Creates scenarios based on matched series in historical data.
        
        Args:
            horizon (int): The number of future time steps to consider for scenario creation.
            clu_thres (int): The threshold for clustering, influencing the number of clusters.
        
        """
        # Ensure sequences exist before proceeding
        if len(self.sequences) == 0:
            raise Exception('No shape found, please fit before predict.')
    
        # Extract key stats from stored sequences
        tot_seq = [
            [series.name, series.index[-1], series.min(), series.max(), series.sum(),weight_cov] 
            for series, weight, weight_cov in self.sequences]
    
        pred_seq = []
        weight_cov = []
        # Generate future sequences for each stored sequence
        for col, last_date, mi, ma, somme,cov in tot_seq:
            date = self.data.index.get_loc(last_date)  # Get index position of the last known date
            # Ensure there are enough future values for the specified horizon
            if date + horizon < len(self.data):
                # Extract future values for the given column
                seq = self.data.iloc[date + 1 : date + 1 + horizon, self.data.columns.get_loc(col)].reset_index(drop=True)
                # Normalize sequence using min-max scaling
                seq = (seq - mi) / (ma - mi)
                pred_seq.append(seq.tolist())
                weight_cov.append(cov)
                
        # Convert sequences to a DataFrame
        tot_seq = pd.DataFrame(pred_seq)
        
        # Perform hierarchical clustering
        if mode == 'b-cluster':    
            tot_seq_cov = pd.concat([tot_seq,pd.Series(weight_cov)],axis=1)
            linkage_matrix = linkage(tot_seq_cov, method='ward')
            clusters = fcluster(linkage_matrix, (horizon+len(self.cov))/clu_thres, criterion='distance')
        else:
            linkage_matrix = linkage(tot_seq, method='ward')
            clusters = fcluster(linkage_matrix, horizon / clu_thres, criterion='distance')
        
        # Assign clusters to the sequences
        tot_seq['Cluster'] = clusters
        
        if mode == 'a-cluster':
            tot_seq['weight'] = [1/x for x in weight_cov]
            val_sce = tot_seq.groupby('Cluster').apply(weighted_mean).apply(pd.Series)
            
        else:
            # Compute mean values per cluster
            val_sce = tot_seq.groupby('Cluster').mean()
        # Set the index to the relative frequency of each cluster
        val_sce.index = round(pd.Series(clusters).value_counts(normalize=True).sort_index(), 2)
        # Store the computed scenarios
        self.val_sce = val_sce

   
    def predict(self, horizon=6,mode='b-cluster', clu_thres=3):
        """
        Predicts future values based on historical sequences using hierarchical clustering.
    
        Args:
            horizon (int): The number of future time steps to predict.
            clu_thres (int): The threshold for clustering, affecting the number of clusters.
    
        Returns:
            pd.Series: The final predicted sequence.
        """
        # Ensure sequences exist before proceeding
        if len(self.sequences) == 0:
            raise Exception('No shape found, please fit before predict.')
    
        # Extract key stats from stored sequences
        tot_seq = [
            [series.name, series.index[-1], series.min(), series.max(), series.sum(),weight_cov] 
            for series, weight, weight_cov in self.sequences]
    
        pred_seq = []
        weight_cov = []
        # Generate future sequences for each stored sequence
        for col, last_date, mi, ma, somme,cov in tot_seq:
            date = self.data.index.get_loc(last_date)  # Get index position of the last known date
            # Ensure there are enough future values for the specified horizon
            if date + horizon < len(self.data):
                # Extract future values for the given column
                seq = self.data.iloc[date + 1 : date + 1 + horizon, self.data.columns.get_loc(col)].reset_index(drop=True)
                # Normalize sequence using min-max scaling
                seq = (seq - mi) / (ma - mi)
                pred_seq.append(seq.tolist())
                weight_cov.append(cov)
                
        # Convert sequences to a DataFrame
        tot_seq = pd.DataFrame(pred_seq)
        
        # Perform hierarchical clustering
        if mode == 'b-cluster':    
            tot_seq_cov = pd.concat([tot_seq,pd.Series(weight_cov)],axis=1)
            linkage_matrix = linkage(tot_seq_cov, method='ward')
            clusters = fcluster(linkage_matrix, (horizon+len(self.input_cov))/clu_thres, criterion='distance')

        else:
            linkage_matrix = linkage(tot_seq, method='ward')
            clusters = fcluster(linkage_matrix, horizon / clu_thres, criterion='distance')
        
        # Assign clusters to the sequences
        tot_seq['Cluster'] = clusters

        if mode == 'a-cluster':
            tot_seq['weight'] = [1/x for x in weight_cov]
            val_sce = tot_seq.groupby('Cluster').apply(weighted_mean).apply(pd.Series)
        else:
            # Compute mean values per cluster
            val_sce = tot_seq.groupby('Cluster').mean()
        # Set the index to the relative frequency of each cluster
        val_sce.index = round(pd.Series(clusters).value_counts(normalize=True).sort_index(), 2)
        # Determine the most frequent cluster       
        pred_ori = val_sce.loc[val_sce.index == val_sce.index.max()].mean()
        # Retrieve original shape values for denormalization
        seq1 = pd.Series(data=self.Shape.values)
        # Denormalize predictions back to original scale
        preds = pred_ori * (seq1.max() - seq1.min()) + seq1.min()
    
        return preds

