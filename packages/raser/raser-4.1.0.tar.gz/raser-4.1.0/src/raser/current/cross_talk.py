import os
import subprocess
from time import time_ns

import ROOT
ROOT.gROOT.SetBatch(True)

from afe.ngspice import set_ngspice_input
from afe.ngspice import set_tmp_cir
from util.output import output, delete_file

def cross_talk(name, cu):
    read_ele_num = len(cu)
    cross_talk_cu = []
    for i in range(read_ele_num):
        cross_talk_cu.append(ROOT.TH1F("cross_talk"+str(i+1),"Cross Talked Current"+" No."+str(i+1)+"electrode",
                                cu[i].GetNbinsX(), cu[i].GetXaxis().GetXmin(), cu[i].GetXaxis().GetXmax()))
        cross_talk_cu[i].Reset()

    cross_talk_cir = os.getenv("RASER_SETTING_PATH")+"/detector/" + name + "_cross_talk.cir"

    input_current_strs = set_ngspice_input(cu)
    time_stamp = time_ns()
    pid = os.getpid()
    # stamp and thread name for avoiding file name conflict
    path = output(__file__, name)
    tmp_cirs, raws = set_tmp_cir(read_ele_num, path, input_current_strs, cross_talk_cir, str(time_stamp)+"_"+str(pid))
    for i in range(read_ele_num):
        subprocess.run(['ngspice -b '+tmp_cirs[i]], shell=True)
    
    time_limit = 20e-9
    time_unit = 10e-12
    # TODO: make this match the .tran in the .cir file
    for i in range(read_ele_num):
        raw = raws[i]
        temp_cross_talk_cu = []
        with open(raw, 'r') as f:
            lines = f.readlines()
            line = lines[0]
            neighbor_num = int(len(line.split())/2)
            # TODO: here assumes the raw file arranges the data from the original electrode to the farest one
            times, volts = [[] for i in range(neighbor_num)], [[] for i in range(neighbor_num)]

            for line in lines:
                for i_prime in range(neighbor_num):
                    times[i_prime].append(float(line.split()[2*i_prime]))
                    volts[i_prime].append(float(line.split()[2*i_prime+1]))
        for i_prime in range(neighbor_num):
            temp_cross_talk_cu.append(ROOT.TH1F("cross talk %s"%(name)+str(i+1), "cross talk %s"%(name),
                            int(time_limit/time_unit),0,times[i_prime][-1]))
            # the .raw input is not uniform, so we need to slice the time range
            filled = set()
            for j in range(len(times[i_prime])):
                k = temp_cross_talk_cu[i_prime].FindBin(times[i_prime][j])
                temp_cross_talk_cu[i_prime].SetBinContent(k, volts[i_prime][j])
                filled.add(k)
            # fill the empty bins
            for k in range(1, int(times[i_prime][-1]/time_unit)-1):
                if k not in filled:
                    temp_cross_talk_cu[i_prime].SetBinContent(k, temp_cross_talk_cu[i_prime][k-1])

            if i-i_prime >= 0:
                cross_talk_cu[i-i_prime].Add(temp_cross_talk_cu[i_prime])
            if i_prime != 0 and i+i_prime < read_ele_num:
                cross_talk_cu[i+i_prime].Add(temp_cross_talk_cu[i_prime])


    # TODO: delete the files properly
    for tmp_cir in tmp_cirs:
        delete_file(tmp_cir)
    for raw in raws:
        delete_file(raw)

    return cross_talk_cu
