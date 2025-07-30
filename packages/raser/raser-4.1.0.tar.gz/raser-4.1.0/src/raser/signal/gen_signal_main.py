#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@Description: The main program of Raser induced current simulation      
@Date       : 2024/02/20 18:12:26
@Author     : tanyuhang, Chenxi Fu
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
import geant4_pybind as g4b

from device import build_device as bdv
from interaction.interaction import GeneralG4Interaction
from interaction.detector_construction import GeneralDetectorConstruction
from interaction.action_initialization import GeneralActionInitialization
from field import devsim_field as devfield
from current import cal_current as ccrt
from current.cross_talk import cross_talk
from afe import readout as rdo
from .draw_save import energy_deposition, draw_drift_path
from util.output import output


def main(kwargs):
    """
    Description:
        The main program of Raser induced current simulation      
    Parameters:
    ---------
    dset : class
        Parameters of simulation
    Function or class:
        Detector -- Define the basic parameters and mesh structure of the detector
        DevsimField -- Get the electric field and weighting potential 
        G4Interaction -- Electron and hole paris distibution
        CalCurrent -- Drift of e-h pais and induced current
        Amplifier -- Readout electronics simulation  
    Modify:
    ---------
        2021/09/02
    """
    start = time.time()

    det_name = kwargs['det_name']
    my_d = bdv.Detector(det_name)
    if kwargs['voltage'] != None:
        my_d.voltage = kwargs['voltage']

    if kwargs['irradiation'] != None:
        my_d.irradiation_flux = float(kwargs['irradiation'])

    if kwargs['g4experiment'] != None:
        my_d.g4experiment = kwargs['g4experiment']

    if kwargs['amplifier'] != None:
        my_d.amplifier = kwargs['amplifier']

    g4_vis = kwargs['g4_vis']

    my_f = devfield.DevsimField(my_d.device, my_d.dimension, my_d.voltage, my_d.read_out_contact, my_d.irradiation_flux)
    
    g4_seed = random.randint(0,1e7)
    my_g4 = GeneralG4Interaction(my_d, my_d.g4experiment, g4_seed, g4_vis)
    my_current = ccrt.CalCurrentG4P(my_d, my_f, my_g4, -1)
    if "strip" in my_d.det_model:
        my_current.cross_talk_cu = cross_talk(det_name, my_current.sum_cu)
        ele_current = rdo.Amplifier(my_current.cross_talk_cu, my_d.amplifier)
    else:
        ele_current = rdo.Amplifier(my_current.sum_cu, my_d.amplifier)

    now = time.strftime("%Y_%m%d_%H%M%S")
    path = output(__file__, my_d.det_name, now)
    #energy_deposition(my_g4)   # Draw Geant4 depostion distribution
    draw_drift_path(my_d,my_g4,my_f,my_current,path)
    my_current.draw_currents(path) # Draw current
    if "strip" in my_d.det_model:
        ele_current.draw_waveform(my_current.cross_talk_cu, path) # Draw waveform
    else:
        ele_current.draw_waveform(my_current.sum_cu, path)

    if 'strip' in my_d.det_model:
        my_current.charge_collection(path)
    
    del my_f
    end = time.time()
    print("total_time:%s"%(end-start))


if __name__ == '__main__':
    args = sys.argv[1:]
    kwargs = {}
    for arg in args:
        key, value = arg.split('=')
        kwargs[key] = value
    main(kwargs)
    