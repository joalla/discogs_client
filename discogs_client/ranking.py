from discogs_client.exceptions import UserInputError

from tqdm import tqdm

def artistAnalyzer(statDic,artist,releases):
    for release in releases:
        if release.data['type'] == 'master':
            if artist not in release.main_release.artists:
                break
            statDic[release.main_release.id] = release.ratings()
        else:
            if artist not in release.artists:
                break
            ratings = release.ratings()
            if ratings[0]:
                statDic[release.id] = ratings
    return statDic
def labelAnalyzer(releases) :
    statDic = {}
    for release in tqdm(releases):
        ratings = release.ratings()
        if not ratings[0]:
            continue
        master = release.master
        if master:
            title = master.main_release.id
        else:
            statDic[release.id] = ratings
            continue
        if title not in statDic:
            statDic[title] = ratings
        else:
            newCount = statDic[title][0] + ratings[0]
            newRating = ((statDic[title][0] * statDic[title][1]) + (ratings[0] * ratings[1])) / newCount
            statDic[title] = [newCount,newRating]
    return statDic

def findArtist(artists):
    numArtists = len(artists)
    index = 0
    while index < numArtists:
        searchRes = input("Is {} the correct artist? (Y/N): ".format(artists[index])).lower()
        if searchRes == 'y':
            return artists[index]
        index += 1
    raise UserInputError('No artist found with name ' + artist)

def findLabel(labels):
    numLabels = len(labels)
    index = 0
    while index < numLabels:
        searchRes = input("Is {} the correct label? (Y/N): ".format(labels[index])).lower()
        if searchRes == 'y':
            return labels[index]
        index += 1
    raise UserInputError('No label found with name ' + artist)

def artistYearAdjust(artist,yearRange):
    lowRange, highRange = yearRange
    if lowRange != -1:
        yearAdjusted = []
        for release in artist.releases:
            year = release.year
            if year >= lowRange and year <= highRange:
                yearAdjusted.append(release)
        return yearAdjusted
    else:
        return artist.releases
    
def labelYearAdjust(label,yearRange):
    lowRange, highRange = yearRange
    yearAdjusted = []
    if lowRange != -1:
        for release in label.releases:
            if release in yearAdjusted:
                continue
            year = release.year
            if year>= lowRange and year <= highRange:
                yearAdjusted.append(release)
    else:
        for release in label.releases:
            if release not in yearAdjusted:
                yearAdjusted.append(release)

    return yearAdjusted

        
def bayesianAvg(rating,avg,confidence):
        return ((rating[0] * rating[1]) + (avg * confidence)) / (rating[0] + confidence)

def bayesianSort(dic,numResults,rankingType):
    if rankingType == 'popular':
        return sorted(dic.items(),key = lambda item: item[1][0],reverse = True)[:numResults]
    numElems = len(dic)
    numRatings = sum(i[0] for i in dic.values())
    avgRating = sum(i[0] * i[1] for i in dic.values())/numRatings
    if rankingType == 'normal':
        if numElems > 100:
            confidenceNum = sorted(dic.items(),key = lambda item: item[1][0])[int(numElems * (1-(10/numElems)))][1][0]
        else:
            confidenceNum = sorted(dic.items(),key = lambda item: item[1][0])[int(numElems * .9)][1][0]
    else:
        confidenceNum = sorted(dic.items(),key = lambda item: item[1][0])[int(numElems * .35)][1][0]

    bayesianVals = [None] * numElems
    for idx, rating in enumerate(dic.items()):
        bayesianVals[idx] = [rating[0],bayesianAvg(rating[1],avgRating,confidenceNum)]
    return sorted(bayesianVals,key = lambda item: item[1], reverse = True)[:numResults]


def checkExceptions(kwargs):
    year_range = kwargs.get('year_range',[-1,-1])
    if not isinstance(year_range,list) or len(year_range) != 2 or year_range[0] > year_range[1]:
        raise UserInputError('Incorrect year_range format')
    numResults = kwargs.get('num_results',5)
    if not isinstance(numResults,int) or numResults < 1:
        raise UserInputError('Incorrect num_results input')
    rankingType = kwargs.get('ranking_type','normal')
    if rankingType not in ['normal','esoteric','popular']:
        raise UserInputError('Incorrect ranking_type input')
    alias = kwargs.get('alias',False)
    if not isinstance(alias,bool):
        raise UserInputError('Incorrect alias input')
    return [year_range,numResults,rankingType,alias]





