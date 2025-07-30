
import pandas as pd
import numpy as np



def split_cccv(data:pd.DataFrame, current_threshold:float = 5e-4, voltage_slope_threshold:float = 2e-4, window:int = 5, max_outliers:int=3) -> pd.DataFrame:
    """
    Splits CCCV DCHG steps into CC and CV portions based on voltage stabilization.\n
    Given a dataframe containing at least 'VOLTAGE_V' and 'CURRENT_A' columns during a CCCV step, \
        a dataframe will be returned with a 'STEP_MODE' column indicating the CC and CV portions.
    If `data` already contains a 'STEP_MODE' column, only steps with 'CCCV' will be split and the 'STEP_MODE' \
        column will be replaced with new values. \n
    *WARNING*: If \'STEP_CAPACITY_AH\' and \'STEP_NUMBER\' are in `data`, \'STEP_CAPACITY_AH\' will be updated to \
        restart at 0 during the CV step. However, \'STEP_NUMBER\' will not be changed. Therefore, the original \
        \'STEP_NUMBER\' still corresponds to both the CC and CV steps after splitting.

    Args:
        data (pd.DataFrame): A dataframe containing 'VOLTAGE_V' and 'CURRENT_A' columns. If 'STEP_MODE' is not \
        supplied, all data will be assumed to be from a CCCV step. Optional columns include any column names \
        from the 'TimeSeriesSchema' definition. 
        current_threshold (float, optional): The tolerance on the current setpoint during CC hold. Defaults to 5e-4.
        voltage_slope_threshold (float, optional): The dV/dt threshold for CV detection. Defaults to 2e-4.
        window (int, optional): Moving average window size to smooth voltage slope. Defaults to 5.
        max_outlier (int, optional): The number of discontinuities allowed during continuous CC detection. Defaults to 3.

    Returns:
        pd.DataFrame: Updated dataframe with the same columns as `data` with a new (or replaced) 'STEP_MODE' column
    """

    df = data.copy()

    # Ensure there is an indexing column with unique values
    original_idx = df.index.values
    df['_row_id'] = np.arange(len(df))
    df.set_index('_row_id', drop=True, inplace=True)
    

    # Identify CCCV step rows (if STEP_MODE exists)
    if 'STEP_MODE' in df.columns:
        mask_cccv = df['STEP_MODE'].str.contains('CCCV', na=False)
    else:
        mask_cccv = pd.Series(True, index=df.index)  # Assume all rows are CCCV if STEP_MODE isn't provided

    # Determine grouping columns based on available df
    group_cols = [col for col in ['FILE_ID', 'STEP_NUMBER'] if col in df.columns]


    # Group by available identifiers (ensures multiple CCCV steps are treated separately)
    grouped = df[mask_cccv].groupby(group_cols) if group_cols else [('all', df[mask_cccv])]
    
    # Use the existing STEP_MODE and STEP_CAPACITY columns if available
    step_modes = df.get('STEP_MODE', pd.Series(index=df.index, dtype='object')).copy()
    step_capacities = df.get('STEP_CAPACITY_AH', None).copy()

    for _, group in grouped:    # for each CCCV step in each FILE_ID
        if group.empty:
            continue

        # Compute voltage slope (dV/dt)
        voltage_slope = group['VOLTAGE_V'].diff().rolling(window=window, min_periods=1).mean()
        # Compute change in current
        current_diff = group['CURRENT_A'].diff().fillna(0)

        # Identify CC phase:
        cc_mask = (
            (current_diff.abs() <= group['CURRENT_A'].abs()*current_threshold) &      # Change in current is less threshold
            (voltage_slope.abs() > voltage_slope_threshold)                         # Voltage is still changing
        )

        # Handle continuity: ensure CC phase does not restart after switching to CV
        continuous_cc = cc_mask.copy()
        outlier_count = 0
        # Check if there's a CC portion based on the first `window` points
        cc_active = cc_mask.iloc[:window].sum() > window // 2  # More than half of the first window should be CC for it to be considered as CC

        for i in range(1, len(continuous_cc)):
            # If CV but currently cc_active check outlier count 
            if not continuous_cc.iloc[i] and cc_active:  
                # Ignore up to max_outliers (assume still CC)
                if outlier_count < max_outliers:
                    outlier_count += 1  
                    continuous_cc.iloc[i] = True
                else:
                    cc_active = False  # CC has definitively ended
            
            # If cc has ended (found more than max_outliers of CV indications)
            if not cc_active:
                continuous_cc.iloc[i] = False  # Ensure it stays CV
        if len(continuous_cc) > 1:
            continuous_cc.iloc[0] = continuous_cc.iloc[1]

        # Identify CHG vs DCHG
        chg_type = 'CHG' if (voltage_slope[continuous_cc].mean() > 0) else 'DCHG'

        # Map back using _row_id
        step_modes.loc[group.index[continuous_cc]] = f'CC {chg_type}'
        step_modes.loc[group.index[~continuous_cc]] = f'CV {chg_type}'

        # Subtract the initial STEP_CAPACITY_AH for each (FILE_ID, NEW_STEP_MODE)
        if step_capacities is not None:
            # Select only the CV portion of the step
            cv_steps_capacities = step_capacities.loc[group.index[~continuous_cc]]
            # Subtract the initial capacity value from the CV steps
            initial_capacity = cv_steps_capacities.iloc[0] if not cv_steps_capacities.empty else 0
            cv_steps_capacities -= initial_capacity
            # Update the original `step_capacities` in the dataframe
            step_capacities.loc[group.index[~continuous_cc]] = cv_steps_capacities

    df['STEP_CAPACITY_AH'] = step_capacities
    df['STEP_MODE'] = step_modes

    # Update STEP_CAPACITY_AH (if in df) --> all STEP_MODEs should start at zero capacity
    if not step_capacities is None: 
        df['STEP_CAPACITY_AH'] = step_capacities

    # Restore the original index
    df.index = original_idx

    return df


