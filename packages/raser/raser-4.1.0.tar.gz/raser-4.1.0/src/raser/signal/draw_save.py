#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@Description: Draw and plot drift path and induced current       
@Date       : 2021/08/31 11:09:40
@Author     : tanyuhang
@version    : 1.0
'''
from array import array
import time

import ROOT
ROOT.gROOT.SetBatch(True)

from util.output import output

def energy_deposition(my_g4v):
    """
    @description:
        Energy_deposition for multi events of Geant4 simulation
    @param:
        None     
    @Returns:
        None
    @Modify:
        2021/08/31
    """
    c1=ROOT.TCanvas("c1","canvas1",1000,1000)
    h1 = ROOT.TH1F("Edep_device", "Energy deposition in SiC", 100, 0., 0.1)
    for i in range (len(my_g4v.edep_devices)):
        h1.Fill(my_g4v.edep_devices[i])
    g1 = ROOT.TF1("m1","landau",0,0.1)
    h1.Fit(g1,"S")
    print("MPV:%s"%g1.GetParameter(1))
    h1.Draw()
    now = time.strftime("%Y_%m%d_%H%M")
    c1.SaveAs("output/particle/dep_SiC"+"_"+now+"_energy.pdf")
    c1.SaveAs("output/particle/dep_SiC"+"_"+now+"_energy.root")

def draw_scat_angle(evnets_angle,angle,model):
    """Draw scatting angle of events"""
    c1=ROOT.TCanvas("c1","canvas1",1000,1000)
    c1.Divide(1,2)
    c1.cd(1)
    n=len(evnets_angle)
    ROOT.gStyle.SetOptStat(0)
    h1 = ROOT.TH1F("event angle", "Source Angle = "+str(angle), n, 0., n)
    for i in range(n):
        if evnets_angle[i] != None:
            h1.SetBinContent(i,evnets_angle[i])
    h1.GetXaxis().SetTitle(" Event number ")
    h1.GetYaxis().SetTitle(" Scattering Angle ")
    h1.GetXaxis().CenterTitle()
    h1.GetYaxis().CenterTitle() 
    h1.SetLineWidth(2)
    h1.SetLineColor(2)
    h1.Draw("HIST")
    c1.cd(2)
    events = [ evnets_angle[i] for i in range(n) if evnets_angle[i] != None ]
    h2 = ROOT.TH1F("angle distribution", "Source Angle = "+str(angle), 
                   100, 0., max(events))
    for i in range(n):
        if evnets_angle[i] != None:
            h2.Fill(evnets_angle[i])
    h2.GetXaxis().SetTitle(" Scattering Angle ")
    h2.GetYaxis().SetTitle(" number ")
    h2.GetXaxis().CenterTitle()
    h2.GetYaxis().CenterTitle() 
    h2.SetLineWidth(2)
    h2.SetLineColor(2)
    h2.Draw("HIST")    
    c1.SaveAs("scat_angle"+model+".pdf")

def draw_drift_path(my_d,my_g4,my_f,my_current,path):
    ROOT.gStyle.SetOptStat(0)
    # # ROOT.gROOT.SetBatch(1)
    c1 = ROOT.TCanvas("c", "canvas1", 200, 10, 1500, 2000)
    c1.Divide(1,2)

    if "3Dpixel" in my_d.det_model:
        n_bin=[int((my_f.sx_r-my_f.sx_l)/5),
                int((my_f.sy_r-my_f.sy_l)/5),int((my_d.l_z)/10)]
        structure = ROOT.TH3D("","",n_bin[0],my_f.sx_l,my_f.sx_r,
                                    n_bin[1],my_f.sy_l,my_f.sy_r,
                                    n_bin[2],0,my_d.l_z)
    else:
        n_bin=[int(my_d.l_x/50),int(my_d.l_y/50),int(my_d.l_z)]
        structure = ROOT.TH3D("","",n_bin[0],0,my_d.l_x,
                                    n_bin[1],0,my_d.l_y,
                                    n_bin[2],0,my_d.l_z)
    c1.cd(1)
    ROOT.gPad.SetMargin(0.15, 0.1, 0.1, 0.1)
    for k in range(n_bin[2]):
        for j in range (n_bin[1]):
            for i in range(n_bin[0]):
                if "3Dpixel" in my_d.det_model:
                    x_v = (i+1)*((my_f.sx_r-my_f.sx_l)/n_bin[0])+my_f.sx_l
                    y_v = (j+1)*((my_f.sx_r-my_f.sx_l)/n_bin[1])+my_f.sx_l
                    z_v = (k+1)*(my_d.l_z/n_bin[2])
                else:
                    x_v = (i+1)*(my_d.l_x/n_bin[0])
                    y_v = (j+1)*(my_d.l_y/n_bin[1])
                    z_v = (k+1)*(my_d.l_z/n_bin[2])
                try:
                    x_value,y_value,z_value = my_f.get_e_field(x_v,y_v,z_v)
                    if x_value==0 and y_value==0 and z_value ==0:
                        structure.SetBinContent(i+1,j+1,k+1,1)
                    else:                       
                        structure.SetBinContent(i+1,j+1,k+1,0)
                except RuntimeError:
                    structure.SetBinContent(i+1,j+1,k+1,1)
    structure.SetFillColor(1)
    structure.GetXaxis().SetTitle("x axis [\mum]")
    structure.GetYaxis().SetTitle("y axis [\mum]")
    structure.GetZaxis().SetTitle("z axis [\mum]")
    structure.GetXaxis().CenterTitle()
    structure.GetYaxis().CenterTitle() 
    structure.GetZaxis().CenterTitle() 
    structure.GetXaxis().SetTitleOffset(1.2)
    structure.GetYaxis().SetTitleOffset(1.4)
    structure.GetZaxis().SetTitleOffset(1.0)
    structure.GetXaxis().SetLabelSize(0.08)
    structure.GetYaxis().SetLabelSize(0.08)
    structure.GetZaxis().SetLabelSize(0.08)
    structure.GetXaxis().SetTitleSize(0.08)
    structure.GetYaxis().SetTitleSize(0.08)
    structure.GetZaxis().SetTitleSize(0.08)
    structure.GetXaxis().SetNdivisions(5)
    structure.GetYaxis().SetNdivisions(5)
    structure.GetZaxis().SetNdivisions(5)
    structure.Draw("ISO")
    c1.Update()

    mg = ROOT.TMultiGraph("mg","") # graph for page 2
    x_array=array('f')
    y_array=array('f')
    z_array=array('f')
    for hole in my_current.holes:
        n=len(hole.path)
        if(n>0):
            x_array.extend([step[0] for step in hole.path])
            y_array.extend([step[1] for step in hole.path]) 
            z_array.extend([step[2] for step in hole.path])              
            gr_p = ROOT.TPolyLine3D(n,x_array,y_array,z_array)
            gr_p.SetLineColor(2)
            gr_p.SetLineStyle(1)
            gr_p.Draw("SAME")
            gr_2D_p=ROOT.TGraph(n,x_array,z_array)
            gr_2D_p.SetMarkerColor(2)
            gr_2D_p.SetLineColor(2)
            gr_2D_p.SetLineStyle(1)
            mg.Add(gr_2D_p)
            del x_array[:]
            del y_array[:]
            del z_array[:]
    for electron in my_current.electrons:
        m=len(electron.path)
        if(m>0):
            x_array.extend([step[0] for step in electron.path])
            y_array.extend([step[1] for step in electron.path])
            z_array.extend([step[2] for step in electron.path])                
            gr_n = ROOT.TPolyLine3D(m,x_array,y_array,z_array)
            gr_n.SetLineColor(4)
            gr_n.SetLineStyle(1)
            gr_n.Draw("SAME")
            gr_2D_n=ROOT.TGraph(m,x_array,z_array)
            gr_2D_n.SetMarkerColor(4)
            gr_2D_n.SetLineColor(4)
            gr_2D_n.SetLineStyle(1)
            mg.Add(gr_2D_n)
            del x_array[:]
            del y_array[:]
            del z_array[:]
    if 'lgad' in my_d.det_model:
        for hole in my_current.gain_current.holes:
            n=len(hole.path)
            if(n>0):
                x_array.extend([step[0] for step in hole.path])
                y_array.extend([step[1] for step in hole.path]) 
                z_array.extend([step[2] for step in hole.path])              
                gr_p = ROOT.TPolyLine3D(n,x_array,y_array,z_array)
                gr_p.SetLineColor(617)#kMagneta+1
                gr_p.SetLineStyle(1)
                gr_p.Draw("SAME")
                gr_2D_p=ROOT.TGraph(n,x_array,z_array)
                gr_2D_p.SetMarkerColor(617)#kMagneta+1
                gr_2D_p.SetLineColor(617)#kMagneta+1
                gr_2D_p.SetLineStyle(1)
                mg.Add(gr_2D_p)
                del x_array[:]
                del y_array[:]
                del z_array[:]
        for electron in my_current.gain_current.electrons:
            m=len(electron.path)
            if(m>0):
                x_array.extend([step[0] for step in electron.path])
                y_array.extend([step[1] for step in electron.path])
                z_array.extend([step[2] for step in electron.path])                
                gr_n = ROOT.TPolyLine3D(m,x_array,y_array,z_array)
                gr_n.SetLineColor(867)#kAzure+7
                gr_n.SetLineStyle(1)
                gr_n.Draw("SAME")
                gr_2D_n=ROOT.TGraph(m,x_array,z_array)
                gr_2D_n.SetMarkerColor(867)#kAzure+7
                gr_2D_n.SetLineColor(867)#kAzure+7
                gr_2D_n.SetLineStyle(1)
                mg.Add(gr_2D_n)
                del x_array[:]
                del y_array[:]
                del z_array[:]
    particle_track = my_g4.p_steps_current[my_g4.selected_batch_number]
    n = len(particle_track)
    if(n>0):
        x_array.extend([step[0] for step in particle_track])
        y_array.extend([step[1] for step in particle_track])
        z_array.extend([step[2] for step in particle_track])
        gr = ROOT.TPolyLine3D(n,x_array,y_array,z_array)
        gr.SetLineColor(1)
        gr.SetLineStyle(1)
        gr.SetLineWidth(4)
        gr.Draw("SAME")
        gr_2D=ROOT.TGraph(n,x_array,z_array)
        gr_2D.SetMarkerColor(1)
        gr_2D.SetLineColor(1)
        gr_2D.SetLineStyle(1)
        gr_2D.SetLineWidth(4)
        mg.Add(gr_2D)
        del x_array[:]
        del y_array[:]
        del z_array[:]
    c1.cd(2)
    ROOT.gPad.SetMargin(0.15, 0.1, 0.2, 0.1)
    mg.GetXaxis().SetTitle("x axis [\mum]")
    mg.GetYaxis().SetTitle("z axis [\mum]")
    mg.GetXaxis().CenterTitle()
    mg.GetYaxis().CenterTitle() 
    mg.GetXaxis().SetTitleOffset(1.2)
    mg.GetYaxis().SetTitleOffset(0.8)
    mg.GetXaxis().SetLabelSize(0.08)
    mg.GetYaxis().SetLabelSize(0.08)
    mg.GetXaxis().SetTitleSize(0.08)
    mg.GetYaxis().SetTitleSize(0.08)
    mg.GetXaxis().SetNdivisions(5)
    mg.GetYaxis().SetNdivisions(5)
    c1.Update()
    mg.Draw("APL")
    c1.SaveAs(path+'/'+my_d.det_model+"_drift_path.pdf")
    c1.SaveAs(path+'/'+my_d.det_model+"_drift_path.root")
    del c1



