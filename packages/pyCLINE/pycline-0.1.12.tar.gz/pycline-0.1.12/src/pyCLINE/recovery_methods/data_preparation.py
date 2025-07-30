import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.signal import find_peaks

def normalize_variables(df, vars, time, norm_method='minmax', value_max=1.0, value_min=0.0):
    """
    The function conducts min-max normalization in the range '[0:1]
    of the varibles from the list 'vars' in the dataframe 'df'

    return dataframe containing normalized variables 'df_norm'
    and the dataframe containing normalization coefficients per variable 'df_coef'

    Args:
        df (pandas DataFrame): dataframe containing variables
        vars (list): list of the variables to normalize
        time (str): name of the time column
        value_max (float, optional): Maximal value for min-max normalizaiton. Defaults to 1.0.
        value_min (int, optional): Minimal value for min-max noramlization. Defaults to 0.0.

    Returns:
        df_norm (pandas DataFrame): dataframe containing normalized variables
        df_coef (pandas DataFrame): dataframe containing minimal and maximal values per variable
    """
    # creating a new dataframe for normalized data and copying the time column
    df_norm = pd.DataFrame()
    df_norm[time] = df[time]
    # creating a dataframe to store the normalization coefficients (min and max of the raw variables)
    df_coef = pd.DataFrame(index=['min', 'max'])
    if norm_method != 'None':
        # normalizing variables
        for var in vars:
            if norm_method == 'minmax':
                df_coef[var] = [df[var].min(), df[var].max()]
                
                df_norm['norm {:}'.format(var)] = (df[var] - df_coef[var]['min'])*(value_max-value_min)/(df_coef[var]['max'] - df_coef[var]['min']) + value_min
            if norm_method == 'zscore':
                df_coef[var] = [df[var].mean(), df[var].std()]
                df_norm['norm {:}'.format(var)] = (df[var] - df_coef[var]['mean'])/(df_coef[var]['sd'])

    return df_norm, df_coef

def plot_optimal_thresholding(thresholds, nsamples, varsamples, optimal_threshold, idx, histogram):
    """
    When a system exhibits a non-uniform distribution of data points in the phase space,
    the optimal thresholding can be used to sample the data uniformly.
    This function plots the normalized sample size, normalized sampling standard deviation,
    and the ratio of the sample size to the sampling standard deviation as a function of the threshold.

    Args:
        thresholds (numpy array): array of threshold values
        nsamples (numpy array): array of normalized sample sizes
        varsamples (numpy array): array of normalized sampling standard deviations
        optimal_threshold (int): optimal threshold value
        idx (int): index of the optimal threshold value
        histogram (numpy histogram object): 2D histogram of the phase space
    """  
    fig, axes = plt.subplots(1,2, figsize=(11,5))
    axes[0].plot(thresholds, nsamples, label='norm. sample size')
    axes[0].plot(thresholds, varsamples, label='norm. sampling SD', c='C1')
    axtwinx = axes[0].twinx()
    axtwinx.plot(thresholds, nsamples/varsamples, label='sample size/SD', c='C2')
    axtwinx.scatter(optimal_threshold, (nsamples/varsamples)[idx], c='r', s=50, label='optimal threshold, {:d}'.format(int(optimal_threshold)))

    axes[0].legend()
    axtwinx.legend()
    axes[0].set_xlabel('sampling threshold')
    axes[0].set_ylabel('norm sample size, sampling SD')
    axtwinx.set_ylabel('sample size/SD')

    hthresh = np.copy(histogram)
    hthresh[hthresh>optimal_threshold] = optimal_threshold

    axes[1].imshow(hthresh)

    plt.show()

def compute_optimal_threshold(df, vars, binx, biny, plot_thresholding=True):
    """
    When a system exhibits a non-uniform distribution of data points in the phase space,
    the optimal thresholding can be used to sample the data uniformly.
    This function computes the optimal thresholding value based on the normalized sample size,
    normalized sampling standard deviation, and the ratio of the sample size to the sampling standard deviation.

    Args:
        df (pandas dataframe): dataframe containing variables
        vars (list): list of the variables to generate the optimal threshold
        binx (list): list of bins for the first variable
        biny (list): list of bins for the second variable
        plot_thresholding (bool, optional): If the thresholded phase space between the first and second
                                            variable should be plotted. Defaults to True.

    Returns:
        optimal_threshold (int): optimal threshold value
    """    
    h, _, _ = np.histogram2d(df[vars[0]], df[vars[1]], bins=(binx, biny))

    nthresh = np.arange(np.min(h[h>0]),np.max(h[h>0]),50)
    nsamples = np.zeros(nthresh.shape[0])
    varsamples = np.zeros(nthresh.shape[0])

    for i in range(nthresh.shape[0]):

        hthresh = np.copy(h)
        hthresh[hthresh>nthresh[i]] = nthresh[i]
        nsamples[i] = np.sum(hthresh)
        varsamples[i] = np.std(hthresh[hthresh>0])

    if np.max(nsamples) != np.min(nsamples):
        nsamples = (nsamples - np.min(nsamples))/(np.max(nsamples) - np.min(nsamples)) + 1
        varsamples = (varsamples - np.min(varsamples))/(np.max(varsamples) - np.min(varsamples)) + 1

        idx = np.argmax(nsamples/varsamples)
        optimal_threshold = nthresh[idx]
    else:
        optimal_threshold = np.max(nthresh)

    if plot_thresholding:
        plot_optimal_thresholding(nthresh, nsamples, varsamples, optimal_threshold, idx, h)

    return int(optimal_threshold)

def uniform_sampling(df, threshold, input_vars, binx, biny):
    """
    The function samples the data uniformly in the phase space defined by the input variables
    based on the provided threshold value.

    Args:
        df (pandas dataframe): dataframe containing variables
        threshold (int): threshold value for the uniform sampling
        input_vars (list): list of the input variables
        binx (list): list of bins for the first variable
        biny (list): list of bins for the second variable

    Returns:
        df_uniform (pandas dataframe): dataframe containing uniformly sampled data
    """    
    df_uniform = pd.DataFrame()

    for i in range(0,binx.shape[0]):
        for j in range(0,biny.shape[0]):

            df_subsample = df[(df[input_vars[0]]>binx[i-1]) & (df[input_vars[0]]<binx[i]) &
                              (df[input_vars[1]]>biny[j-1]) & (df[input_vars[1]]<biny[j])].copy()
            if df_subsample.shape[0]>0:
                if df_subsample.shape[0]<=threshold:
                    df_uniform = pd.concat((df_uniform,df_subsample), ignore_index=True)
                else:
                    df_uniform = pd.concat((df_uniform,df_subsample[:threshold]), ignore_index=True)

    return df_uniform

# data preparation
def prepare_data(df, vars, time, tmin=None, tmax=None, scheme='newton_difference', norm_method='minmax',value_min=0.0,  value_max=1.0, normalize=True):    
    """
    The function prepares the raw time series of the system variables for feeding into ML model. Preparation includes the following steps: (i) data slicing in the indicated range [tmin:tmax], [:tmax], or [tmin:] (optional). If tmin and tmax are not provided, full data are processed (ii) min-max normalization of the variables from the list 'vars'(iii) computing a delayed [t-1] variable for each variable from the list.
    The function returns a prepared dataframe 'df_prepared' and the dataframe containing normalization coefficients per variable 'df_coef'.

    Args:
        df (pandas dataframe): dataframe containing variables
        vars (list): list of the variables to normalize
        time (str): name of the time column
        tmin (float, optional): Minimal time of the time slice of data. Defaults to None.
        tmax (float, optional): Maximal time of the time slice of data. Defaults to None.
        scheme (str, optional): Scheme for computing second input variable. Defaults to 'newton_difference'.
        norm_method (str, optional): Normalization method. Defaults to 'minmax'.
        value_min (int, optional): Minimal value for minmax normalization. Defaults to 0.0.
        value_max (int, optional): Maximal value for minmax normalization. Defaults to 1.0.
        normalize (bool, optional): If data should be normalized. Defaults to True.

    Returns:
        df_prepared (pandas dataframe): dataframe containing prepared data for feeding into ML model
        df_coef (pandas dataframe): dataframe containing normalization coefficients (min and max values) per variable
    """   
    
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input data is not a pandas DataFrame")
    if not isinstance(vars, list):
        raise ValueError("Variables should be provided as a list")
    if not isinstance(time, str):
        raise ValueError("Time column name of pandas DataFrame should be provided as a string")
    if not isinstance(tmin, (int, float)) and tmin is not None:
        raise ValueError("tmin should be a float or an integer, or None")
    if not isinstance(tmax, (int, float)) and tmax is not None:
        raise ValueError("tmax should be a float or an integer, or None")
    if not isinstance(scheme, str):
        raise ValueError("Scheme should be provided as a string")
    if not isinstance(norm_method, str):
        raise ValueError("Normalization method should be provided as a string")
    if not isinstance(value_min, (int, float)):
        raise ValueError("Minimal value for minmax normalization should be a float or an integer")
    if not isinstance(value_max, (int, float)):
        raise ValueError("Maximal value for minmax normalization should be a float or an integer")
    if not isinstance(normalize, bool):
        raise ValueError("Normalize variable should be a boolean value")
    if not all([var in df.columns for var in vars]):
        raise ValueError("Variables should be present in the provided dataframe")
    if not time in df.columns:
        raise ValueError("Time column should be present in the provided dataframe")
    if scheme not in ['newton_difference', 'two_point', 'five_point', 'derivative']:
        raise ValueError("Unknown scheme: {:}".format(scheme))

    # slice the data in the range [tmin; tmax] if needed
    # if ((tmin is None) or (tmax is None)):
    if tmin is None:
        tmin = df[time].min()
    if tmax is None:
        tmax = df[time].max()
    df_slice = df[(df[time]>=tmin) & (df[time]<=tmax)].copy()

    # min-max normalization of each variable in the range [value_min; value_max]
    if normalize:
        df_norm, df_coef = normalize_variables(df_slice, vars=vars, time=time, norm_method=norm_method,value_max=value_max,value_min=value_min)
    else:
        df_norm = df_slice.copy()
        df_coef = pd.DataFrame(index=['min', 'max'])
        for var in vars:
            df_norm['norm {:}'.format(var)] = df_norm[var]
            df_coef[var] = [df[var].min(), df[var].max()]
    # computing delayed variables
    df_prepared = pd.DataFrame()
    
    if scheme == 'newton_difference':
        first_point = 1
    if scheme == 'two_point':
        first_point = 2   
    if scheme == 'five_point':
        first_point = 4
    if scheme == 'derivative':
        first_point=0
    df_prepared[time] = df_norm[time].iloc[first_point:]
    for var in vars:
        # df_prepared['norm {:}'.format(var)] = df_norm['norm {:}'.format(var)].to_numpy()[first_point:]
        if scheme=='newton_difference':
            df_prepared['norm {:}'.format(var)] = df_norm['norm {:}'.format(var)].to_numpy()[first_point:]
            df_prepared['norm {:}'.format(var)+'[t-1]'] = df_norm['norm {:}'.format(var)].to_numpy()[:-first_point]
        if scheme=='two_point':
            df_prepared['norm {:}'.format(var)] = df_norm['norm {:}'.format(var)].to_numpy()[first_point-1:-first_point+1]
            df_prepared['norm {:}'.format(var)+'[t+1]'] = df_norm['norm {:}'.format(var)].to_numpy()[first_point:]
            df_prepared['norm {:}'.format(var)+'[t-1]'] = df_norm['norm {:}'.format(var)].to_numpy()[first_point-2:-first_point]
        if scheme=='five_point':
            df_prepared['norm {:}'.format(var)] = df_norm['norm {:}'.format(var)].to_numpy()[first_point-2:-first_point+2]
            df_prepared['norm {:}'.format(var)+'[t+2]'] = df_norm['norm {:}'.format(var)].to_numpy()[first_point:]
            df_prepared['norm {:}'.format(var)+'[t+1]'] = df_norm['norm {:}'.format(var)].to_numpy()[first_point-1:-first_point+3]
            df_prepared['norm {:}'.format(var)+'[t-1]'] = df_norm['norm {:}'.format(var)].to_numpy()[first_point-3:-first_point+1]
            df_prepared['norm {:}'.format(var)+'[t-2]'] = df_norm['norm {:}'.format(var)].to_numpy()[:-first_point]
        if scheme=='derivative':
            dt=df[time][1]-df[time][0]
            df_prepared['norm {:}'.format(var)] = df_norm['norm {:}'.format(var)].to_numpy()[first_point:]

            x = df_norm['norm {:}'.format(var)].to_numpy()[first_point:]
            x_dot = np.ones(x.shape[0])*np.NaN
            x_dot_forward =[(x[i+1]-x[i])/dt for i in range(x[:-1].shape[0])]
            
            x_dot_backward =[(x[i]-x[i-1])/dt for i in range(x[1:].shape[0])]

            x_dot_forward = np.array(x_dot_forward)
            x_dot_backward = np.array(x_dot_backward)
            x_dot= (x_dot_forward + x_dot_backward)/2
            # insert np.nan at the first position
            x_dot = np.insert(x_dot, -1, np.nan)
            x_dot[0]=np.nan
            
            df_prepared['d norm{:}'.format(var)+'/dt'] = x_dot

    return df_prepared.dropna(), df_coef

def shuffle_and_split(df, input_vars, target_var, train_frac=0.7, test_frac=0.15, optimal_thresholding=True, plot_thresholding=True):
    """
    The function prepares training, testing, and validation sets from the prepared dataframe
    by random uniform shuffling and splitting the data according to the provided proportions

    the function returns respective training, testing, and validation datasets

    Args:
        df (pandas dataframe): dataframe containing prepared data for feeding into ML model
        input_vars (list): list of the input variables
        target_var (list): list of the target variable(s)
        train_frac (float, optional): fraction of training data. Defaults to 0.7.
        test_frac (float, optional): fraction of testing data. Defaults to 0.15.
        optimal_thresholding (bool, optional): If the optimal thresholding should be used. Defaults to True.
        plot_thresholding (bool, optional): _description_. Defaults to True.

    Returns:
        input_train (pandas dataframe): dataframe containing input variables for training
        target_train (pandas dataframe): dataframe containing target variables for training
        input_test (pandas dataframe): dataframe containing input variables for testing
        target_test (pandas dataframe): dataframe containing target variables for testing
        input_val (pandas dataframe): dataframe containing input variables for validation
        target_val (pandas dataframe): dataframe containing target variables for validation
    """    

    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input data is not a pandas DataFrame")
    if not isinstance(input_vars, list):
        raise ValueError("Input variables should be provided as a list")
    if not isinstance(target_var, list):
        raise ValueError("Target variables should be provided as a list")
    if not isinstance(train_frac, float):
        raise ValueError("Training fraction should be a float")
    if not isinstance(test_frac, float):
        raise ValueError("Testing fraction should be a float")
    if train_frac + test_frac > 1:
        raise ValueError("Training and testing fractions should be less or equal to 1")
    if train_frac< test_frac:
        raise ValueError("Training fraction should be greater than testing fraction")
    if not isinstance(optimal_thresholding, bool):
        raise ValueError("Optimal thresholding should be a boolean value")
    if not isinstance(plot_thresholding, bool):
        raise ValueError("Plot thresholding should be a boolean value")
    if not all([var in df.columns for var in input_vars]):
        raise ValueError("Input variables should be present in the provided dataframe")
    if not all([var in df.columns for var in target_var]):
        raise ValueError("Target variables should be present in the provided dataframe")
    
    # data shuffling
    df_shuffled = df.sample(frac = 1)

    # uniform data sampling in the phase space
    if optimal_thresholding:
        binx = np.linspace(df_shuffled[input_vars[0]].min(), df_shuffled[input_vars[0]].max(), 11)
        biny = np.linspace(df_shuffled[target_var[0]].min(), df_shuffled[target_var[0]].max(), 11)

        if optimal_thresholding:
            optimal_threshold = compute_optimal_threshold(df_shuffled, [input_vars[0], target_var[0]], binx, biny, plot_thresholding)

        df_shuffled = uniform_sampling(df_shuffled, optimal_threshold, [input_vars[0], target_var[0]], binx, biny)
        df_shuffled = df_shuffled.sample(frac = 1)

    # computing the sizes of the training and testing datasets based of the provided fractions
    Ntrain = int(df_shuffled.shape[0]*train_frac)
    Ntest = int(df_shuffled.shape[0]*test_frac)

    # splitting the data
    input_train = df_shuffled[input_vars].iloc[:Ntrain]
    target_train = df_shuffled[target_var].iloc[:Ntrain]

    input_test = df_shuffled[input_vars].iloc[Ntrain:Ntrain+Ntest]
    target_test = df_shuffled[target_var].iloc[Ntrain:Ntrain+Ntest]

    input_val = df_shuffled[input_vars].iloc[Ntrain+Ntest:]
    target_val = df_shuffled[target_var].iloc[Ntrain+Ntest:]

    return input_train, target_train, input_test, target_test, input_val, target_val

def normalize_adjusted(x, df_coef, var, min=-1, max=1):
    return (x - df_coef[var].min())*(max-min) / (df_coef[var].max() - df_coef[var].min())+min


#### General functions
def calculate_period(x_train, t_train):
    """
    Calculate the period of an oscillation.

    Parameters
    ----------
    x_train : np.array
        Time series of data.
    t_train : np.array
        Time of the time series.

    Returns
    -------
    peaks_u : np.array
        Size of peaks detected in the time series.
    peaks_t : np.array
        Time points where peaks occur in the data set.
    period : float
        Period of Time Series.
    peaks[0]: list
        Array of all indicies of local maxima
    
    """
    if len(x_train.shape)<2:
        peaks=find_peaks(x_train)
        peaks_t=t_train[peaks[0]]
        peaks_u=x_train[peaks[0]]
    elif x_train.shape[1]==2 or x_train.shape[1]==3:
        peaks=find_peaks(x_train[:,0])
        peaks_t=t_train[peaks[0]]
        peaks_u=x_train[peaks[0],0]
    elif x_train.shape[1]==5:
        peaks=find_peaks(x_train[:,1])
        peaks_t=t_train[peaks[0]]
        peaks_u=x_train[peaks[0],1]

    period_temp=0
    for i in range(len(peaks_t)-1):
        period_temp=period_temp+(peaks_t[i+1]-peaks_t[i])
    if len(peaks_t)>1:
        subtract=1
    else: subtract=0
    period=period_temp/(len(peaks_t)-subtract)
    return peaks_u, peaks_t, period, peaks[0]
