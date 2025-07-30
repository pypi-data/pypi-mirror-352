#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@Description: The main program of Raser induced current simulation      
@Date       : 2024/09/26 15:11:20
@Author     : zhulin
@version    : 2.0
'''
import sys
import os
import array
import time
import subprocess
import json
import random

import ROOT
ROOT.gROOT.SetBatch(True)

from device import build_device as bdv
from field import devsim_field as devfield
from current import cal_current as ccrt
from afe import readout as rdo
from util.output import output

from .laser import LaserInjection


def job_main(kwargs):
    det_name = kwargs['det_name']
    my_d = bdv.Detector(det_name)
    
    if kwargs['voltage'] != None:
        voltage = kwargs['voltage']
    else:
        voltage = my_d.voltage

    if kwargs['laser'] != None:
        laser = kwargs['laser']
        laser_json = os.getenv("RASER_SETTING_PATH")+"/laser/" + laser + ".json"
        with open(laser_json) as f:
            laser_dic = json.load(f)
    else:
        # TCT must be with laser
        raise NameError

    if kwargs['amplifier'] != None:
        amplifier = kwargs['amplifier']
    else:
        amplifier = my_d.amplifier

    my_f = devfield.DevsimField(my_d.device, my_d.dimension, voltage, my_d.read_out_contact, my_d.irradiation_flux)
    my_l = LaserInjection(my_d, laser_dic)

    my_current = ccrt.CalCurrentLaser(my_d, my_f, my_l)
    path = output(__file__, my_d.det_name, my_l.model)

    ele_current = rdo.Amplifier(my_current.sum_cu, amplifier, seed=int(kwargs['job'])) # job number
    if kwargs['scan'] != None: #assume parameter alter
        # key = my_l.fz_rel
        tag = kwargs['job']
        ele_current.save_signal_TTree(path, tag)
    else:
        my_current.draw_currents(path) # Draw current
        ele_current.draw_waveform(my_current.sum_cu, path) # Draw waveform

        my_l.draw_nocarrier3D(path)
        my_l.draw_nocarrier2D(path)
        
    print('successfully')

def main(kwargs):
    scan_number = kwargs['scan']
    for i in range(scan_number):
        command = ' '.join(['python3', 'src/raser', '-b', 'tct signal',sys.argv[3],sys.argv[4], '--job', str(i)] + sys.argv[5:]) # 'raser', '-sh', 'signal'
        # command = ' '.join(['python3', 'raser', 'tct signal',sys.argv[3],sys.argv[4], '--job', str(i)] + sys.argv[5:]) # 'raser', '-sh', 'signal'
        print(command)
        subprocess.run([command], shell=True)
    