"""
Created by Akshay Maheshwari
09/05/2017

Produces smoldyn parameter specification files that sweep parameters in a specified way.
"""

import os
import datetime
import numpy as np


#_side_len_ = 0.0677*1/0.0059# diameter 100 nm
_tRNA_cog_NUM_ = 42
_tRNA_nr_NUM_ = 0
_tRNA_non_NUM_ = 0
_crowder_NUM_ = 0
_ribosome_NUM_ = 0
_ribosome_cog_NUM_ =0
_ribosome_nr_NUM_ = 0
_ribosome_non_NUM_ = 0
_ribosome_suc_NUM_ = 0
_ribosome_inac_NUM_ = 0
_ribosome_noreac_NUM_ = 0
_tRNA_uni_NUM_ = 0

_simtime_ = 1.6e-3*1e5+1000
_ts_ = 1e-04
_molPosTS_ = 1e-04

_seed_ =  (np.random.randint(1e12))

exptList = open("/Users/Akshay/Dropbox/Life/EndyLab/Research/TranslationDynamics/expts/expt_list.txt","w")
outputSimtimeList=open("/Users/Akshay/Dropbox/Life/EndyLab/Research/TranslationDynamics/expts/outputSimtimeList.txt","w")

outputReactionsList=open("/Users/Akshay/Dropbox/Life/EndyLab/Research/TranslationDynamics/expts/outputReactionsList.txt","w")
outputMolPosList = open("/Users/Akshay/Dropbox/Life/EndyLab/Research/TranslationDynamics/expts/outputMolPosList.txt","w")

_D_tRNAEfTu_ = 1.0
_D_ribosome_ = 0.454545
_D_crowder_ = 2.95

expt_description = open("/Users/Akshay/Dropbox/Life/EndyLab/Research/TranslationDynamics/expts/expt_description.txt","w")

ts_list = np.array([1.6e-3,0.8e-3,0.4e-3,0.2e-3,0.1e-3])
molposts_list = np.array([1.6e-2,1.6e-2,1.6e-2,1.6e-2,1.6e-2])*100

#simtime_list = (ts_list*1e5+100)*1.6e-3/ts_list
ribosome_NUM_list = [1,1]
crowder_NUM_list = [2273,2273]
_seed_list = range(0,10000,5)

res_steps_list = [1,2,3,5,10,100,300]
crowders = np.array([820,820,820,820,820,820,820])#crowders = np.array([1970,2096,1791,1418,1090,820])
ribosomes = list([7,7,7,7,7,7,7]) #ribosomes = [4,8,9,9,8,7]
side_len = list([0.0677*1/0.0059,0.0677*1/0.0059,0.0677*1/0.0059,0.0677*1/0.0059,0.0677*1/0.0059,0.0677*1/0.0059,0.0677*1/0.0059]) #sidelen = [0.101,0.0929,0.0842,0.0774,0.072,0.0677]
cog_tRNA = np.array([0,0,0,0,0,0,0])

_molPosTSStartCrowder_ =1000

phi_sweep = list()
for i in range(len(crowders)):
    phi_sweep.append((crowders[i],ribosomes[i],side_len[i],cog_tRNA[i]))

i_max = len(phi_sweep)
k_max=5
j_max=50
for i in range(i_max):
	_crowder_NUM_ = phi_sweep[i][0]
	_ribosome_NUM_ = phi_sweep[i][1]
	_side_len_ = phi_sweep[i][2]
	_tRNA_uni_NUM_ = phi_sweep[i][3]
	res_steps = res_steps_list[i]
	for k in range (0, k_max):
		#res_steps = 300
		_ts_ = ts_list[k]
		#_molPosTS_ = ts_list[0]*res_steps
		_ts_rxnon_ = 0
		_ts_diffon_= _ts_*(res_steps-1)
		_ts_delta_= _ts_*res_steps
		_molPosTS_ = molposts_list[k]
		_molPosTSStart_ = _ts_*res_steps*100
		_molPosTSEndReactionLog_ = _ts_*res_steps*102
		_simtime_ = _ts_*res_steps*100+(250)*res_steps
		_simtime2_ = _ts_*res_steps*100+(500)*res_steps


		for j in range(0, j_max):
			_seed_ = _seed_list[j]
			#_seed_ =  (np.random.randint(1e12))

			exptname = "expt_"+str(j_max*k_max*i+j_max*k+j)+".txt"
			_outputSimtime_ = "expt-"+str(j_max*k_max*i+j_max*k+j)+"-Simtime-"+datetime.date.today().strftime('%Y%m%d')+ ".csv"
			_outputSimtime2_ = "expt-"+str(j_max*k_max*i+j_max*k+j)+"-Simtime2-"+datetime.date.today().strftime('%Y%m%d')+ ".csv"

			_outputReactions_ = "expt-"+str(j_max*k_max*i+j_max*k+j)+"-Reactions-"+datetime.date.today().strftime('%Y%m%d')+ ".csv"
			_outputMoleculePos_ = "expt-"+str(j_max*k_max*i+j_max*k+j)+"-Molpos-"+datetime.date.today().strftime('%Y%m%d')+ ".csv"
			_outputMoleculePostRNA_ = "expt-"+str(j_max*k_max*i+j_max*k+j)+"-MolpostRNA-"+datetime.date.today().strftime('%Y%m%d')+ ".csv"
			_outputMoleculePostRNA2_ = "expt-"+str(j_max*k_max*i+j_max*k+j)+"-MolpostRNA2-"+datetime.date.today().strftime('%Y%m%d')+ ".csv"
			_outputMoleculePosCrowder_ = "expt-"+str(j_max*k_max*i+j_max*k+j)+"-MolposCrowder-"+datetime.date.today().strftime('%Y%m%d')+ ".csv"
			_outputMoleculePosRibosome_ = "expt-"+str(j_max*k_max*i+j_max*k+j)+"-MolposRibosome-"+datetime.date.today().strftime('%Y%m%d')+ ".csv"
			_outputMoleculePos_ = "expt-"+str(j_max*k_max*i+j_max*k+j)+"-MolpostRNA-"+datetime.date.today().strftime('%Y%m%d')+ ".csv"

			expt = open("/Users/Akshay/Dropbox/Life/EndyLab/Research/TranslationDynamics/expts/" + exptname,'w')
			expt.write("variable Z_side_len_ " + str(_side_len_) + "\n")
			expt.write("variable Z_tRNA_cog_NUM_ " + str(_tRNA_cog_NUM_)+ "\n")
			expt.write("variable Z_tRNA_nr_NUM_ " + str(_tRNA_nr_NUM_)+ "\n")
			expt.write("variable Z_tRNA_non_NUM_ " + str(_tRNA_non_NUM_)+ "\n")
			expt.write("variable Z_crowder_NUM_ " + str(_crowder_NUM_)+ "\n")
			expt.write("variable Z_ribosome_NUM_ " + str(_ribosome_NUM_)+ "\n")
			expt.write("variable Z_ribosome_cog_NUM_ " + str(_ribosome_cog_NUM_)+ "\n")
			expt.write("variable Z_ribosome_nr_NUM_ " + str(_ribosome_nr_NUM_)+ "\n")
			expt.write("variable Z_ribosome_non_NUM_ " + str(_ribosome_non_NUM_)+ "\n")
			expt.write("variable Z_ribosome_suc_NUM_ " + str(_ribosome_suc_NUM_)+ "\n")
			expt.write("variable Z_ribosome_inac_NUM_ " + str(_ribosome_inac_NUM_)+ "\n")
			expt.write("variable Z_ribosome_noreac_NUM_ " + str(_ribosome_noreac_NUM_)+ "\n")
			expt.write("variable Z_tRNA_uni_NUM_ " + str(_tRNA_uni_NUM_)+ "\n")

			expt.write("variable Z_D_tRNAEfTu_ " + str(_D_tRNAEfTu_) + "\n")
			expt.write("variable Z_D_ribosome_ " + str(_D_ribosome_) + "\n")
			expt.write("variable Z_D_crowder_ " + str(_D_crowder_) + "\n")

			expt.write("variable Z_ts_ " + str(_ts_)+ "\n")
			expt.write("define_global Z_molPosTS_ " + str(_molPosTS_) + "\n")
			expt.write("define_global Z_simtime_ " + str(_simtime_)+ "\n")
			expt.write("define_global Z_simtime2_ " + str(_simtime2_)+ "\n")


			expt.write("define_global Z_molPosTSStart_ " + str(_molPosTSStart_) + "\n")
			expt.write("define_global Z_molPosTSStartCrowder_ " + str(_molPosTSStartCrowder_ ) + "\n")
			expt.write("define_global Z_molPosTSEndReactionLog_ " + str(_molPosTSEndReactionLog_ ) + "\n")


			expt.write("define_global Z_outputSimtime_ " + "data/"+_outputSimtime_ +"\n")
			expt.write("define_global Z_outputSimtime2_ " + "data/"+_outputSimtime2_ +"\n")

			expt.write("define_global Z_outputReactions_ " + "data/"+_outputReactions_+"\n")
			expt.write("define_global Z_outputMoleculePostRNA_ " + "data/"+_outputMoleculePostRNA_+"\n")
			expt.write("define_global Z_outputMoleculePostRNA2_ " + "data/"+_outputMoleculePostRNA2_+"\n")
			expt.write("define_global Z_outputMoleculePosCrowder_ " + "data/"+_outputMoleculePosCrowder_+"\n")
			expt.write("define_global Z_outputMoleculePosRibosome_ " + "data/"+_outputMoleculePosRibosome_+"\n")
			expt.write("define_global Z_seed_ " + str(_seed_) + "\n")

			expt.write("define_global Z_ts_rxnon_ "+str(_ts_rxnon_)+"\n")
			expt.write("define_global Z_ts_diffon_ "+str(_ts_diffon_)+"\n")
			expt.write("define_global Z_ts_delta_ "+str(_ts_delta_)+"\n")





			####### Variables to sweep########
			#_ribosome_NUM_ += 1
			####### Write list of experiment and output

			exptList.write(exptname + "\n")
			outputSimtimeList.write(_outputSimtime_ + "\n")
			outputReactionsList.write(_outputReactions_ + "\n")
			outputMolPosList.write(_outputMoleculePos_ + "\n")

expt_description.write("Total simulation time: "+ str(_simtime_) + "s. ; Simulation time step: " + str(_ts_)+" s.")