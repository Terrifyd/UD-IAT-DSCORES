import re
import numpy as np
import pandas as pd

def checkHeightFormat(height):
    """
    raises an error if height is in wrong format

    :height: survey string of height selection
    """ 
    # print("Height: " , height)
    if not height[0].isdigit() or not height[5].isdigit():
        print("Height: " , height)
        raise ValueError("Height is not in the correct format")
    
def checkWeightFormat(weight: str):
    """
    raises an error if weight is in wrong format

    :weight: survey string of weight selection
    """ 
    if not re.match(r'^\d{2,3}', weight) and weight[:5] != "Above" and weight[:5] != "Below":
        print("Weight: ", weight)
        raise ValueError("Weight is not in the correct format")
    
def isNaN(value):
    """
    checks if a variable is nan, there exists a numpy function for this, but it
    throws an error when run on strings

    :value: variable to be checked
    :return: true if var is nan
    """ 
    if isinstance(value, str):
        return False
    
    else:
        return True if np.isnan(value) else False
    
    return False

def heightToInches(height: str):
    """
    translates height selection from survey (in form of '5 ft 11 in: 162 cm') 
    and into inches.

    :height: survey string of height selection
    :return: height in inches
    """ 
    feet = int(height[0])
    inches = int(height[5]) if height[6] == ' ' else int(height[5]+height[6])
    return inches + (feet * 12)


def weightToPounds(weight: str):
    """
    translates weight selection from survey (in form of '130lb: 59kg') 
    and into pounds.

    :weight: survey string of weight selection
    :return: weight in pounds
    """ 
    if weight[:5] == "Above":
        return 300
    
    elif weight[:5] == "Below":
        return 50

    return int(weight[0]+weight[1]+weight[2]) if weight[3] == 'l' or weight[3] == ':' else int(weight[0]+weight[1])


def calculateBMI(height: str, weight: str):
    """
    takes the height and weight from survey participants selection and 
    calculates a participanst BMI

    :height: survey string of height selection
    :weight: survey string of weight selection
    :return: BMI of participant
    """ 
    if isNaN(height): return -1
    if isNaN(weight): return -1

    checkHeightFormat(height)
    checkWeightFormat(weight)

    pounds = weightToPounds(weight)
    inches = heightToInches(height)
    return 703 * (pounds/(inches)**2)

def fetchColumn(df, columnName: str):
    """
    fetches column from data file with the given name

    :df: data file
    :columnName: name of column to be fetched
    :return: array of column
    """
    return df[columnName].to_numpy()

def main():
    # height = '6 ft 1 in'
    # weight = '185lb: 84kg'
    # print(BMI(height, weight))

    # read data from csv file
    df = pd.read_csv("C:\\Users\\dlttu\\OneDrive\\Documents\\IAT_Data.csv")
    # print(df.head())

    #fetch heights and weights into arrays
    heights = fetchColumn(df, 'Q25_1')
    weights = fetchColumn(df, 'Q26_1')

    # remove first two rows (survey question and import ID)
    heights = heights[2:]
    weights = weights[2:]

    BMIs = np.zeros_like(heights)
    BMIs = np.vectorize(calculateBMI)(heights, weights)
    
    BMIs = np.insert(BMIs, 0, np.nan)
    BMIs = np.insert(BMIs, 1, np.nan)

    df['BMI'] = BMIs
    df.to_csv('BMIs.csv', index=False)

    return 0

main()