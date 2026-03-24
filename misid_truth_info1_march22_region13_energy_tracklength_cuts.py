#!/usr/bin/env python3

import argparse
import os
import ROOT

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)
ROOT.TH1.AddDirectory(False)

# =========================
# CONSTANTS
# =========================
FUDICIAL_CUT = 50

LAR_START = (-3478.48,-2166.71,4179.24)
LAR_END =(3478.48,829.282,9135.88)

# =========================
# GEOMETRY
# =========================
def in_between(x_lar_start,x_lar_end,y_lar_start,y_lar_end,z_lar_start,z_lar_end):
    return (
        LAR_START[0] < x_lar_start and
        LAR_START[1] < y_lar_start and
        LAR_START[2] < z_lar_start and
        LAR_END[0] > x_lar_end and
        LAR_END[1] > y_lar_end and
        LAR_END[2] > z_lar_end
    )

def inside_tms(x, y, z):
    if not -3500 < x < 3500: return False
    if not -3700 < y < 1000: return False
    if not 11000 < z < 18200: return False
    return True

def inside_lar(x, y, z):
    if not -4500 < x < 3700: return False
    if not -3200 < y < 1000: return False
    if not 4100 < z < 9200: return False
    return True

# =========================
# REGIONS
# =========================
def region1(x): return -4000 < x < -2500
def region3(x): return 2500 < x < 4000

# =========================
# MAIN ANALYSIS
# =========================
def run(c, truth, outfilename, nmax=-1, preview=False):

    # =========================
    # HISTOGRAMS
    # =========================
    hist_signed_distance = ROOT.TH1D("hist_signed_distance","Muon Signed Distance;mm",100,-2000,2000)
    hist_signed_distance_antimuon = ROOT.TH1D("hist_signed_distance_antimuon","Antimuon Signed Distance;mm",100,-2000,2000)

    hist_total_charge_id = ROOT.TH1D("hist_total_charge_id","Muon total; KE (MeV)",50,0,5000)
    hist_correct_charge_id = ROOT.TH1D("hist_correct_charge_id","Muon correct; KE (MeV)",50,0,5000)

    hist_total_charge_id_antimuon = ROOT.TH1D("hist_total_charge_id_antimuon","Antimuon total; KE (MeV)",50,0,5000)
    hist_correct_charge_id_antimuon = ROOT.TH1D("hist_correct_charge_id_antimuon","Antimuon correct; KE (MeV)",50,0,5000)

    hist_correct_charge_id_percentage = hist_correct_charge_id.Clone("hist_correct_charge_id_percentage")
    hist_correct_charge_id_percentage_antimuon = hist_correct_charge_id_antimuon.Clone("hist_correct_charge_id_percentage_antimuon")

    hist_sd_vs_x = ROOT.TH2D(
        "hist_sd_vs_x",
        "Signed Distance vs X; x_start_tms (mm); signed distance (mm)",
        50, -4000, 4000,
        100, -2000, 2000
    )

    # =========================
    # COUNTERS
    # =========================
    n_correct_mu = 0
    n_correct_amu = 0
    n_mu_total = 0
    n_amu_total = 0

    nevents = c.GetEntries()
    if nmax >= 0 and nevents > nmax:
        nevents = nmax

    print(f"Running over {nevents} events")

    # =========================
    # LOOP
    # =========================
    for i, event in enumerate(c):

        if i >= nevents:
            break

        truth.GetEntry(i)

        if i % 1000 == 0:
            print(f"On {i}/{nevents}")

        for index, pdg in enumerate(truth.PDG):

            if abs(pdg) != 13:
                continue

            # Positions
            x_start = truth.BirthPosition[4*index+0]
            y_start = truth.BirthPosition[4*index+1]
            z_start = truth.BirthPosition[4*index+2]

            x_end = truth.DeathPosition[4*index+0]
            y_end = truth.DeathPosition[4*index+1]
            z_end = truth.DeathPosition[4*index+2]

            x_start_tms = truth.PositionTMSStart[4*index+0]
            z_start_tms = truth.PositionTMSStart[4*index+2]

            # LAr fiducial
            x_lar_start = truth.PositionLArStart[4*index+0] + FUDICIAL_CUT
            y_lar_start = truth.PositionLArStart[4*index+1] + FUDICIAL_CUT
            z_lar_start = truth.PositionLArStart[4*index+2] + FUDICIAL_CUT

            x_lar_end = truth.PositionLArEnd[4*index+0] - FUDICIAL_CUT
            y_lar_end = truth.PositionLArEnd[4*index+1] - FUDICIAL_CUT
            z_lar_end = truth.PositionLArEnd[4*index+2] - FUDICIAL_CUT

            # =========================
            # GEOMETRY CUTS
            # =========================
            if not in_between(x_lar_start,x_lar_end,y_lar_start,y_lar_end,z_lar_start,z_lar_end):
                continue

            if not (inside_lar(x_start,y_start,z_start) and inside_tms(x_end,y_end,z_end)):
                continue

            # =========================
            # REGION SELECTION
            # =========================
            if not (region1(x_start_tms) or region3(x_start_tms)):
                continue

            # =========================
            # PHYSICS CUTS
            # =========================
            if truth.Muon_TrueKE < 1500:
                continue

            #if (z_end - z_start_tms) < 800:
               # continue

            if abs(x_start_tms) < 1000:
                continue

            # =========================
            # MOMENTUM
            # =========================
            p_z = truth.MomentumTMSStart[4*index+2]
            p_x = truth.MomentumTMSStart[4*index+0]

            if p_z == 0:
                continue

            # =========================
            # EXTRAPOLATION
            # =========================
            m = p_x / p_z
            b = x_start_tms - m * z_start_tms
            x_extrapolate = m * z_end + b

            # =========================
            # REGION-DEPENDENT SIGN
            # =========================
            if region1(x_start_tms):
                signed_dist = x_extrapolate - x_end
            elif region3(x_start_tms):
                signed_dist = -(x_extrapolate - x_end)
            else:
                continue

            # =========================
            # FILL DIAGNOSTIC
            # =========================
            hist_sd_vs_x.Fill(x_start_tms, signed_dist)

            # =========================
            # MUON
            # =========================
            if pdg == 13:

                n_mu_total += 1
                hist_signed_distance.Fill(signed_dist)
                hist_total_charge_id.Fill(truth.Muon_TrueKE)

                if signed_dist > 0:
                    hist_correct_charge_id.Fill(truth.Muon_TrueKE)
                    n_correct_mu += 1

            # =========================
            # ANTIMUON
            # =========================
            elif pdg == -13:

                n_amu_total += 1
                hist_signed_distance_antimuon.Fill(signed_dist)
                hist_total_charge_id_antimuon.Fill(truth.Muon_TrueKE)

                if signed_dist < 0:
                    hist_correct_charge_id_antimuon.Fill(truth.Muon_TrueKE)
                    n_correct_amu += 1

    # =========================
    # EFFICIENCY
    # =========================
    hist_correct_charge_id_percentage.Divide(hist_correct_charge_id, hist_total_charge_id)
    hist_correct_charge_id_percentage_antimuon.Divide(hist_correct_charge_id_antimuon, hist_total_charge_id_antimuon)

    eff_mu = n_correct_mu / n_mu_total if n_mu_total > 0 else 0
    eff_amu = n_correct_amu / n_amu_total if n_amu_total > 0 else 0

    print("\n==== FINAL RESULTS ====")
    print("Muon efficiency:", eff_mu)
    print("Antimuon efficiency:", eff_amu)

    # =========================
    # SAVE
    # =========================
    tf = ROOT.TFile(outfilename, "RECREATE")
    hist_signed_distance.Write()
    hist_signed_distance_antimuon.Write()
    hist_correct_charge_id_percentage.Write()
    hist_correct_charge_id_percentage_antimuon.Write()
    hist_sd_vs_x.Write()
    tf.Close()

    # =========================
    # PREVIEW
    # =========================
    if preview:
        c1 = ROOT.TCanvas()

        hist_signed_distance.Draw()
        c1.SaveAs("muon_signed_distance.png")

        hist_signed_distance_antimuon.Draw()
        c1.SaveAs("antimuon_signed_distance.png")

        hist_sd_vs_x.Draw("COLZ")
        c1.SaveAs("signed_distance_vs_x.png")


# =========================
# DRIVER
# =========================
def validate_then_run(args):

    f = ROOT.TFile.Open(args.filename)

    c = f.Get("Reco_Tree")
    truth = f.Get("Truth_Info")

    if not c or not truth:
        print("ERROR: Tree not found")
        f.ls()
        return

    os.makedirs(args.outdir, exist_ok=True)
    outpath = os.path.join(args.outdir, args.name)

    run(c, truth, outpath, args.nevents, args.preview)


# =========================
# ENTRY
# =========================
if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument('--outdir', type=str, default="")
    parser.add_argument('--name', type=str, default="output.root")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--filename', '-f', type=str)

    parser.add_argument('--nevents', '-n', type=int, default=-1)
    parser.add_argument('--preview', action='store_true')

    args = parser.parse_args()

    validate_then_run(args)
