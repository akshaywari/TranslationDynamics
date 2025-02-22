import pandas as pd
import numpy as np
import sys
import math
import pickle as pkl
import glob


def readSimData(path):
    """Reads reaction_log output csv file from a Smoldyn simulation and converts to a dataframe
    
    Args:
        path (string): Path to reaction_log output csv/xls file
    
    Returns:
        df (dataframe): dataframe containing reaction_log data. 
        Rows: One for each reaction/collision that took place
        Columns: 
            time: describes the time of reaction
            rxn: gives the reaction name
            x: x coordinate of reaction
            y: y coordinate of reaction
            z: z coordinate of reaction
            reactantA: Gives the id of the first reactant defined
            reactantB: Gives the id of the second reactant defined
            productA: Gives the id of the first product defined (usually same as reactant A)
            productB: Gives the id of the second product defined (usually same as reactant B)
    """
    df = pd.read_csv("/Users/Akshay/Dropbox/Life/EndyLab/Research/TranslationDynamics/data/expt-0-Reactions-20181018.csv",sep=" ",
        header=None,names=list(["time","rxn","x","y","z","reactantA","reactantB","productA","productB"]))

    return df


def totalCollisions(path):
    """
    Calculates the total number of collisions between all molecules of any type based on a defined "min_delta_time",
    or the minimum time that must lapse before an overlap between two particles is considered a collision again.
    
    Arguments:
        path {string} -- Path to the smoldyn output file that records all overlap events that occured between particles
    
    Returns:
        [List] -- [List containing 1. original length of collision file; 2. length after discarding collisions that occured
        before some set time (to avoid artifacts from extra collisions at startup due to overlap). 3. Total number of collisions 
        between all particles in the provided simulation]
    """
    min_delta_time = 1e-9
    print(path)
    df_chunker = pd.read_csv(path,delimiter=" ",header=None,chunksize=500000)
    overall_return_array = list([0,0,0])
    for df in df_chunker:
        returnArray=list()
        df.columns=["time","rxn","x","y","z","reactantA","reactantB","productA","productB"]
        returnArray.append(df.shape[0])
        df = df[df['time'] > 1e-7]  #Drop first 100 nanoseconds due to overlap of spheres at startup causing increased rxns
        #df = df.sort_values(by=['time','reactantA'])
        df = df[['time','reactantA','reactantB']]

        df = df.iloc[0:] #test different time lengths if desired
        returnArray.append(df.shape[0])

        lookup = {}
        collision=0
     
        for index, row in df.iterrows():
            reacA_i = row["reactantA"] 
            reacB_i = row["reactantB"]
            time_i = row['time']
            
            #Check if the pair collision occured in the last min_delta_time, and if not, add the collision to the count
            if ((reacA_i,reacB_i) not in lookup) or ((time_i-lookup[(reacA_i,reacB_i)][0] > min_delta_time)): 
            #Note, second part of or statement only evaluated if first is false, i.e. reacA and reacB in lookup.
                collision+=1
                lookup[(reacA_i,reacB_i)] = [time_i]
                lookup[(reacB_i,reacA_i)] = [time_i]

        returnArray.append(collision)
        overall_return_array = np.add(overall_return_array, returnArray)
        print(1)
    return overall_return_array

def mixTime(path):
    # df = pd.read_csv(path,delimiter=" ",header=None,names=(["time","rxn","x","y","z","reactantA","reactantB","productA","productB"]))
    
    # mixtimes=list()

    # df = df[['time','reactantA']]
    # df = df[df['time'] > 1e-7]  #Drop first 100 nanoseconds due to overlap of spheres at startup causing increased rxns

    # df = df.sort_values(by=['reactantA','time'])
    # df_group = df.groupby('reactantA')
    # while(len(df_group)==42):
    #     first_times = df_group.first()["time"]
    #     max_first = max(first_times)
    #     min_first = min(first_times)
    #     mixtimes.append(max_first - min_first)
    #     df_sub = df[df['time'] > max_first]
    #     df_group = df_sub.groupby('reactantA')

    # #return mixtimes
    # print(mixtimes)

    df_chunker = pd.read_csv(path,delim_whitespace=True,header=None,names=(["time","rxn","x","y","z","reactantA","reactantB","productA","productB"]),chunksize=100000)
    lookup = {}
    sampleTimes_i = list()

    mixTime=list()
    sampleTimes = list()
    i=0
    time_prev = 0
    for df in df_chunker:
        print(df.info(memory_usage='deep'))
        df = df[['time','reactantA']]
        if i==0:
            df = df[df['time'] > 1e-7]  #Drop first 100 nanoseconds due to overlap of spheres at startup causing increased rxns

        df = df.sort_values(by=['time','reactantA'])
        for index, row in df.iterrows():
            reacA_i = row["reactantA"]
            time_i = row['time']
            if (reacA_i not in lookup):
                lookup[reacA_i] = [time_i]
                sampleTimes_i.append(time_i-time_prev)
                time_prev = time_i

            if len(lookup)==42:
                sampleTimes.append(np.array(sampleTimes_i))
                mixTime.append((max(lookup.values()))[0]-min(lookup.values())[0])
                lookup = {}
                sampleTimes_i=list()
        i+=1
    return mixTime,sampleTimes

#def processOutput(path):
 #   df_chunker = pd.read_csv(path,delimiter=" ",header=None,names=(["time","rxn","x","y","z","reactantA","reactantB","productA","productB"]),chunksize=500000)
  #  for df in df_chunker:


def collisionPickleAggregator(datapath, expts):
    """Aggregates multiple pickle files that each contain an array returned by totalCollision assessed on respective Smoldyn simulation output files
    
    Arguments:
        datapath {[type]} -- [description]
        expts {[]} -- A list of tuples. Each list contains the range of experiments that should be averaged across. For example,
        [(0,3),(3,6),(6,9),(9,12),(12,15)] means to calculate the average collisions between expts0,1,and2; then calculate the average collisions
        btwn expts3,4,5,...and so on. Then, a list of average collisions is returned for each tuple range provided (so, in the example, a list of 
        5 average collision values would be returned)
        
    
    Returns:
        [List] -- a list of average collisions is returned for each tuple range provided (so, in the example, a list of 
        5 average collision values would be returned)
    """
    collision_count=list()
    avg_coll_count = list()
    for expt_i in expts:
        data_arr_j=list()
        count_arr_j=list()
        for j in range(expt_i[0],expt_i[1]):
            try:
                collision_expt_path =glob.glob(datapath+'/analysis/expt-'+str(j)+'-*')[0]
                with open(collision_expt_path, 'rb') as f:
                    data_i = pkl.load(f)
                    count_arr_i = data_i[2]
                data_arr_j.append(data_i)
                count_arr_j.append(count_arr_i)
            except:
                print("Missing experiment")
        avg_coll_count.append(np.average(count_arr_j))
        collision_count.append(data_arr_j)
    #print(avg_coll_count)
    return avg_coll_count,collision_count

def mixTimePickleAggregator(datapath, expts,check_hittimes=False):
    mixTimes = list()
    hitTimes = list()
    for expt_i in expts:
        data_arr_j = list()
        hittimes_arr_j = list()
        for j in range(expt_i[0],expt_i[1]):
            try:
                expt_path = glob.glob(datapath+'/analysis/expt-'+str(j)+'-*')[0]
                with open(expt_path,'rb') as f:
                    data = pkl.load(f)
                    if check_hittimes:
                        data = data[0]
                    data_arr_j.append(np.average(data))
                    #print(data)
                #print(str(j))
            except:
                print("Missing experiment")
        mixTimes.append(np.average(data_arr_j))
    return mixTimes

def hitTimePickleAggregator(datapath,expts):
    hitTimes = list()
    for j in range(expts[0],expts[1]):
        try:
            expt_path = glob.glob(datapath+'/analysis/expt-'+str(j)+'-*')[0]
            with open(expt_path,'rb') as f:
                data = pkl.load(f)
                hitTimes_j = data[1]
                hitTimes.append([sum(hitTimes_onemix) for hitTimes_onemix in hitTimes_j])
        except:
            print("Missing experiment")
    return [i for hitTimes_i in hitTimes for i in hitTimes_i]

def computeTransportRxnTimes(path,simtime, num_rib,expt_start,expt_end,avg=False):
    """Calculates transport (how long partic tRNA unbound) and 
    reaction times (how long particular tRNA bound) from simulations
    
    Arguments:
        path {[type]} -- String to output folder
        simtime {[type]} -- Length of time over which to 
        num_rib {[type]} -- [description]
        expt_start {[type]} -- [description]
        expt_end {[type]} -- [description]
    
    Keyword Arguments:
        avg {bool} -- [description] (default: {False})
    
    Returns:
        [type] -- [description]
    """
    df_outputs = pd.read_csv(path+"outputReactionsList.txt",sep=" ",header=None) #Add batch processing here potentially
    transport_time = list()
    reaction_time = list()
    success_incorp = list()
    rxn17_tot = list()
    rxn21_tot = list()

    for expt_num, row in df_outputs.iterrows():
        succincorp_count = 0
        rxn17_count = 0
        rxn21_count = 0
        if(expt_num>=expt_start and expt_num<expt_end):
            try:
                df = pd.read_csv(path+row[0],delimiter=" ",header=None)
                df.columns=["time","rxn","x","y","z","reactantA","productA","productB"]
                df=df.loc[df['rxn'].isin(["rxn17","rxn18","rxn19","rxn20","rxn21","rxn22"])]
                df=df.loc[df['time']<simtime]
                df=df[['time','rxn']]
                transport_time_i = list()
                reaction_time_i = list()
                i=-1
                single_RxnTime = list() #Created to aggregate transport time between unsuccesful rxns into those btwn only succesful rxns
                single_TransportTime = list() #Created to aggregate transport time between unsuccesful rxns into those btwn only succesful rxns

                for _, row in df.iterrows():
                    i+=1

                    ### If the rxn is a first binding to a ribosome [that unique tRNA is non-cog or cog to]
                    if((row["rxn"]=='rxn17' or row["rxn"]=='rxn21') and succincorp_count<num_rib):
                        if(i>0):
                            single_TransportTime.append(row['time']-float(df.iloc[[i-1]]['time']))
                        else:
                            single_TransportTime.append(row['time'])
                        if(row["rxn"]=='rxn17'):
                            rxn17_count+=1
                        elif (row["rxn"]=='rxn21'):
                            rxn21_count+=1

                    ### If the rxn is after binding between tRNA-ribosome, include as a reaction_time
                    if((row['rxn']=='rxn18'or row["rxn"]=='rxn19' or row['rxn']=='rxn20' or row['rxn']=='rxn22') and succincorp_count<num_rib):
                        single_RxnTime.append(row['time']-float(df.iloc[[i-1]]['time']))
                        if(row['rxn']=='rxn20'):
                            succincorp_count+=1
                            transport_time_i.append(sum(single_TransportTime))
                            reaction_time_i.append(sum(single_RxnTime))
                            rxn17_tot.append(rxn17_count)
                            rxn21_tot.append(rxn21_count)
                            single_TransportTime = list()
                            single_RxnTime = list()
                #print(reaction_time_i)
            except:
                print("missing expt")
                print(expt_num)
            if(succincorp_count<num_rib and avg==True):
                transport_time_i = transport_time_i[:-1] #drops the last transport time if there wasn't a reaction recorded afterwards (else last transport time would be too short)
            transport_time.append(transport_time_i)
            reaction_time.append(reaction_time_i)
            success_incorp.append(succincorp_count)
         #   print(len(transport_time))
          #  print((reaction_time))

    return transport_time, reaction_time, success_incorp,rxn17_tot,rxn21_tot


def countRibosomeCollisions(df,tRNAIDList,ribosomeIDList):
    """Counts the number of collisions that a single tRNA has with each ribosome from 
    a group of ribosomes provided (in a given Smoldyn reaction_log dataframe)
    
    Args:
        df (dataframe): dataframe containing Smoldyn reaction_log data
        tRNAid (int): id of tRNA which to 
        ribosomeIDList (list): list of ribosome IDs from which to count
    
    Returns:
        tRNACollisionCount_r (np array): Array containing number of collisions between a given tRNA
            and all ribosomes in ribosomeIDList
    """
    #Sort the data based on ascending ribosome ID ('reactantB') and reaction timestamp ('time')
    df=df.sort_values(['reactantB','time'], ascending=[True,True])

    # Create two arrays the length or # ribosome IDs to check collisions with
    tRNACollisionCount_rt=np.zeros([len(ribosomeIDList),len(tRNAIDList)])
    print("Computing tRNA collision count [rib,tRNA]: "+str(tRNACollisionCount_rt.shape))
    #Iterate through the sorted dataframe reaction by reaction (row by row)
    df_r = df.loc[df['reactantB'].isin(ribosomeIDList)]
    df_r=df_r.sort_values(['reactantB','time'], ascending=[True,True])

    prevtRNAID = -1;
    prevRibID = -1
    for i, rxn_i in df_r.iterrows():
        #Iterate through ribosomes being tracked, and for the ribosome that the tRNA collided with for the given rxn_i: 
        #1) increment collision count
        
        ribosome_i = rxn_i["reactantB"]
        tRNA_i = rxn_i["reactantA"]
        if(tRNA_i in tRNAIDList and tRNA_i != prevtRNAID and ribosome_i == prevRibID):
            tRNACollisionCount_rt[int(np.where(ribosomeIDList==ribosome_i)[0]),int(np.where(tRNAIDList==tRNA_i)[0])]+=1
        prevtRNAID = tRNA_i
        prevRibID = ribosome_i


    #print(tRNACollisionCount_rt)
    return tRNACollisionCount_rt

def countIncorrectRibosomeCollisions(df, tRNA_IDList, ribosome_IDList, tRNAInclusionList=np.array([])):
    """Creates a list for each tRNA and ribosome pair possible (tRNA_t and ribosome_r)
    of the # of time other tRNAs collided with the ribosome_r in between collisions of 
    the specified tRNA_t and ribosome_r (in a given Smoldyn reaction_log dataframe).
    
    
    Args:
        df (dataframe): dataframe containing Smoldyn reaction_log data
        tRNA_IDList (TYPE): List of tRNA IDs for which to check collisions 
        ribosome_IDList (TYPE): List of ribosome IDs for which to check collisions
    
    Returns:
        IncorrectCollisions_tr (List of Lists of Lists; rank 3 tensor): A list containing a list
        of ribosomes for each tRNAs. Each ribosome has a list that records in time order 
        incorrect collision number between each correct collision (between the ribosome and 
        corresponding tRNA parents). 
        The nested lists/tensor is ordered [trNAid, ribosomeid, collisionGapNumber] = # of incorrect collisions.
    """

    #Sort the data based on ascending ribosome ID ('reactantB') and reaction timestamp ('time')
    df=df.sort_values(['reactantB','time'], ascending=[True,True])
    IncorrectNumColMatrix_rt=np.zeros([len(ribosome_IDList),len(tRNA_IDList)])

    #Create a list of lists of lists (rank 3) [tRNAid, ribosomeid, collisionGapNumber]
    IncorrectCollisions_rt = list()
    for r in range(len(ribosome_IDList)):
        IncorrectCollisions_rt.append(list())
        for t in range(len(tRNA_IDList)):
            IncorrectCollisions_rt[r].append(list())
    print("Initial ribosome x tRNA x collisionGapNumber has shape:", np.array(IncorrectCollisions_rt).shape)

    if tRNAInclusionList.shape[0] == 0:
        tRNAInclusionList = np.arange(df["reactantA"].min(),df["reactantA"].max()+1)

    #Create a sub-dataframe df_r for each ribosome and iterate through each one
    for r_index, ribosomeID in enumerate(ribosome_IDList):
        #print("Currently processing ribosome #",r_index)
        df_r = df.loc[df['reactantB']==ribosomeID]
        prevtRNAID=-1;
        #Iterate through each ribosome sub dataframe
        for i, rxn_i in df_r.iterrows():   

            #Check to ensure the reactant is being considered as a tRNA & Check to see if the reactant is a repeat reactant, in which case ignore. 
            # If reactant is previous reactant then keeping prev rxn var same is ok. If reactantA not on tRNA list, then keeping prev rxn var same also ok.
            if rxn_i["reactantA"] in tRNAInclusionList: #and rxn_i["reactantA"]!=prevtRNAID:              
                for t_index, tRNAID in enumerate(tRNA_IDList):    #For each reaction, iterate through each tRNA. 
                    #Increment the incorrect collision count for each tRNA that wasn't involved 
                    #in the reaction (IncorrectNumColMatrix_tr). 

                    if rxn_i["reactantA"]!=tRNAID: #and (tRNAInclusionList.size==1 or rxn_i["reactantA"] in tRNAInclusionList):
                        IncorrectNumColMatrix_rt[r_index, t_index]+=1

                    #For the tRNA_t that was involved in the reaction, save the total other tRNA-ribosome_r 
                    #collisions that occured in between this reaction and the previous reaction with tRNA_t
                    #and ribosome_r in IncorrectCollisions_tr, and then reset the incorrect collision count
                    #(for tRNA_t-ribosome_r) back to 0.

                    elif rxn_i["reactantA"]==tRNAID:
                        IncorrectCollisions_rt[r_index][t_index].append(IncorrectNumColMatrix_rt[r_index, t_index])
                        IncorrectNumColMatrix_rt[r_index, t_index] = 0
                
                prevtRNAID = rxn_i["reactantA"]

    return IncorrectCollisions_rt


def timeSplitter(df, start_time=0, time_interval=0.01, scale="linear",logscalestart=-4):
    """Splits a given Smoldyn reaction_log dataframe into a list of dataframes each with reactions
    that occured between given timestamps. 
    
    Args:
        df (dataframe): dataframe containing Smoldyn reaction_log data. 
        start_time (int, optional): Start time at which to begin splitting reaction data. Default=0
        time_interval (float, optional): Time intervals in which to split reaction data. Default=0.01
        scale (str, optional): "linear" or "log". Log divides by powers of 10 (e.g., 10^-3,10^-2,...,10^2). Default="linear"
        logscalestart (TYPE, optional): if "log" scale selected, the ten power to start the log scale. Default=-3.
    
    Returns:
        timesplitdf_list: A list of dataframes each with reactions from specified time range. 
        In asending order of time frames.
    """

    #Sort overall reaction_log dataframe by ascending time 
    df=df.sort_values(['time'], ascending=[True])
    end_time = df.iloc[df.shape[0]-1]['time']

    #Create array of sampling times based on linear vs. log:
    if scale=="linear":
        #Time interval is added to end_time since np.arange doesn't take into account last interval
        time_arr = np.arange(start_time,end_time+time_interval,time_interval)
    elif scale=="log":
        #Logspace from the start until log10 rounded up end_time. Final param is # of intervals.
        time_arr = np.logspace(logscalestart,math.ceil(np.log10(end_time)),1+abs(logscalestart)+math.ceil(np.log10(end_time)))
    
    #Split up (cut) and group (groupby) the dataframe by the times in time_arr ("time" has timestamp)
    timesplitdf = df.groupby(pd.cut(df["time"],time_arr))

    #Create an ordered list of intervals (the interval is a key to the respective dataframe of reactions)
    intervalkeys = [interval for interval, timesplitdf_i in timesplitdf]

    #Add the time interval organized dataframes of reactions into a list to return 
    timesplitdf_list = list()
    for key in intervalkeys:
        timesplitdf_list.append(timesplitdf.get_group(key))

    return timesplitdf_list


def analyze(path, countRibosomeCollisionsMethod=True, countIncorrectRibosomeCollisionsMethod=True,tRNA_range=-1,rib_range=-1):
    df= readSimData(path)
    if(tRNA_range==-1):
        tRNA_range_arr=np.arange(df["reactantA"].min(),df["reactantA"].max()+1)
    if(rib_range==-1):
        rib_range_arr=np.arange(df["reactantB"].min(),df["reactantB"].max()+1)
    tRNACollisionCount_rt=countRibosomeCollisions(df, tRNA_range_arr,rib_range_arr)
    incorrectCollisions_rt=countIncorrectRibosomeCollisions(df, tRNA_range_arr,rib_range_arr)
    pkl.dump([tRNACollisionCount_rt,incorrectCollisions_rt],open(path[:-4]+".p","wb"))

#how do the 2 most "different" tRNAs (across histogram for all 3 ribosomes) -- create a calculation
#algorithm for this, quantitatively differ/differ when visualized for the 2 diff ribosomes?





