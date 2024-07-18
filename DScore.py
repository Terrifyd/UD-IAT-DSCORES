import re
import io
import numpy as np
import pandas as pd

def collectIATs(df, iatName: str):
    """
    collects both the mobile and desktop versions from their columns and combines them 
    (necessary because each IAT version needed its own question on Qualtrics)

    :df: data frame
    :iatName: name of IAT to be fetched (ours were named "iat" for the weight based 
        iat and "decoy" for the flower/insect iat)
    :return: array of combined mobile and desktop IATs
    """
    mobileIATs = fetchColumn(df, "Mobile " + iatName)
    desktopIATs = fetchColumn(df, "Desktop " + iatName)

    combinedIATs = np.zeros_like(mobileIATs)

    for i in range(len(combinedIATs)):
        if (isinstance(mobileIATs[i], str)):
            combinedIATs[i] = mobileIATs[i]
        else:
            combinedIATs[i] = desktopIATs[i]
    
    # print(combinedIATs[0])
    # print(combinedIATs[1])
    # print(combinedIATs[2])
    # print(combinedIATs[3])
    # print(combinedIATs[4])
    # print(combinedIATs[5])

    # print(combinedIATs[2])
    # print(iatToCSV(combinedIATs[2]))
    return combinedIATs


def fetchColumn(df, columnName: str):
    """
    fetches column from data frame with the given name

    :df: data frame
    :columnName: name of column to be fetched
    :return: array of column
    """
    return df[columnName].to_numpy()

def iatToCSV(iat: str):
    """
    transforms the IAT data into a format that can be read as CSV

    :iat: string of IAT output from Qualtrics
    :return: the IAT string in a format that can be parsed as CSV
    """
    iat = iat.replace('"block,trial', 'block,trial')
    iat = iat.replace('"""', '""')
    iat = iat.replace('""', '"')
    return iat

def meetsExclusion(iatf, threshold: int):
    """
    checks if the iat meets the exclsuon criteria: subjects where more than 10% of 
    their responses are below the threshold are excluded 

    :iatf: data frame of subject's iat 
    :threshold: the reaction time threshold to exclude by
    :return: true if the subject should be excluded, false otherwise
    """

    total = 0
    countBelowThresh = 0

    # iatf['rt'][0]

    for index, row in iatf.iterrows():
        total += 1
        if (row['rt'] < threshold): countBelowThresh += 1

    # print(countBelowThresh)
    # print(total)
    percentBelowThresh = countBelowThresh / total

    return True if percentBelowThresh > 0.1 else False

def blockStdDev(iatf, blockNum):
    """
    calculated the standard deviation of a given block(s)

    :iatf: data frame of subject's iat 
    :blockNum: int of block or array of blocks to find std dev of 
    :return: blocks' std dev
    """
    block = []
    if (isinstance(blockNum, int)):
        block = iatf[iatf['block'] == blockNum]

        return np.std(block['rt'])
        # print(stdDeviation)

    elif (isinstance(blockNum , list)):
        for i in blockNum:
            block = block.append()
    

def processIAT(iat: str):
    """
    calculated the D score from the iat

    :iat:dtring in csv format of the subjects iat responses
    :return: the iat's associated D score
    """

    # no IAT data
    if (not isinstance(iat, str)): return -100

    # iatf = pd.read_table(io.StringIO(iat), sep=",")
    iatf = pd.read_csv(io.StringIO(iat))

    # filter out all trials with time > 10000
    iatf = iatf[iatf['rt'] <= 10000]
    iatf = iatf.reset_index(drop=True) # reset indexes so 0th index will be filled even if filtered out

    exclusion = meetsExclusion(iatf, 300)
    # print(exclusion)
    if exclusion == True:
        return -101

    # from the first block we know the order of the other blocks
    firstBlock = iatf['cond'][0]
    #print(firstBlock)

    deviations = {}
    # deviations[3] = blockStdDev(iatf, 3)
    # deviations[4] = blockStdDev(iatf, 4)
    # deviations[6] = blockStdDev(iatf, 6)
    # deviations[7] = blockStdDev(iatf, 7)

    # find inclusive standard deviations of 3 + 6 and 4 + 7
    deviations['3,6'] = np.std(np.concatenate((iatf[iatf['block'] == 3]['rt'], iatf[iatf['block'] == 6]['rt'])))
    deviations['4,7'] = np.std(np.concatenate((iatf[iatf['block'] == 4]['rt'], iatf[iatf['block'] == 7]['rt'])))
    # print(deviations['4,7'])

    meanLatencies = {}
    meanLatencies['3'] = np.mean(iatf[iatf['block'] == 3]['rt'])
    meanLatencies['4'] = np.mean(iatf[iatf['block'] == 4]['rt'])
    meanLatencies['6'] = np.mean(iatf[iatf['block'] == 6]['rt'])
    meanLatencies['7'] = np.mean(iatf[iatf['block'] == 7]['rt'])
    # print(latencies['7'])

    meanDifferences = {}
    meanDifferences['3,6'] = meanLatencies['6'] - meanLatencies['3']
    meanDifferences['4,7'] = meanLatencies['7'] - meanLatencies['4']

    # D score is the equal weight average of the mean differences divided by their associated standard deviations
    Dscore = ((meanDifferences['3,6'] / deviations['3,6']) + (meanDifferences['4,7'] / deviations['4,7'])) / 2
    Dscore = -Dscore if (firstBlock == 'Fat people/Bad words,Thin people/Good words') else Dscore
    # print(Dscore)
    return Dscore



def main():
    # csv file with Qualtrics exported data as well as users BMIs
    df = pd.read_csv("C:\\Users\\dlttu\\OneDrive\\Documents\\BMIs.csv")

    weightIATs = collectIATs(df, "IAT")[2:]
    # flowerInsectIATs = collectIATs(df, "Decoy")[2:]

    weightDScores = [None] * len(weightIATs)
    for i in range(len(weightIATs)):
        # print(i)
        weightDScores[i] = processIAT(weightIATs[i])

    weightDScores = np.insert(weightDScores, 0, np.nan)
    weightDScores = np.insert(weightDScores, 1, np.nan)

    df['Weight D-Scores'] = weightDScores

    flowerInsectIATs = collectIATs(df, "Decoy")[2:]
    # flowerInsectIATs = collectIATs(df, "Decoy")[2:]

    flowerInsectDScores = [None] * len(flowerInsectIATs)
    for i in range(len(flowerInsectIATs)):
        # print(i)
        flowerInsectDScores[i] = processIAT(flowerInsectIATs[i])

    flowerInsectDScores = np.insert(flowerInsectDScores, 0, np.nan)
    flowerInsectDScores = np.insert(flowerInsectDScores, 1, np.nan)

    df['Flower/Insect D-Scores'] = flowerInsectDScores

    df.to_csv('D-Scores.csv', index=False)


main()