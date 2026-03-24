# 🧲 Magnetic Field Mapping & Validation — DUNE ND TMS

## 📌 Overview

This repository focuses on the implementation and validation of magnetic fields in the **DUNE Near Detector (ND) Muon Spectrometer (TMS)** using **Geant4 / edep-sim**.

The goal is to ensure that **charged particles (muons)** exhibit physically correct bending, enabling:

- Charge identification (μ⁺ vs μ⁻)
- Momentum reconstruction
- Detector validation

---

## 🚀 Background

Magnetic fields were previously validated using:

- A **constant (uniform) magnetic field**
- A Python analysis script that measured **signed displacement**

This setup successfully showed **non-zero peaks**, confirming muon bending.

---

## 🧭 Project History

### 🔹 1. Initial Implementation — Memory Failure

Magnetic field was assigned to a **repeated geometry unit**  
(≈ 1/4 segment of each steel plate)

This caused:

- Field to be instantiated **hundreds of times**
- Severe **memory exhaustion**
- Simulation failure

---

### 🔹 2. Fix — Field Placement Optimization

Field reference moved to the **mother volume**

✅ **Result:**

- Memory issues resolved  
- Simulation successfully executed  
- Large ROOT files generated  

---

### 🔹 3. Validation Attempt

Used an existing Python script (from ~2 years ago)

**Method:**
- Compute **signed values** to detect bending  
- Expect **non-zero peak** if curvature exists  

---

### 🔻 Current Observation

- Signed distributions **peak at zero**
- No visible bending signal

---

## ⚠️ Key Insight

The validation script was designed for:

- Older detector geometry  
- Different region definitions  
- Simpler track paths  

Since then:

- Detector geometry has evolved  
- New regions and bounds have been introduced  

➡️ Therefore:

> A zero-centered result may indicate **invalid analysis**, not necessarily **absence of bending**

---

## 🎯 Current Focus

### 🔄 Re-evaluate Validation Method

We are shifting from:

> **“Simulation is wrong”**

to:

> **“Validation method may be outdated”**

---

## 🧩 Current Goals

### 1. Rebuild Analysis Pipeline

Develop a new Python script that:

- Uses updated detector geometry  
- Tracks muons across correct regions  
- Applies proper entry/exit conditions  

---

### 2. Redefine Bending Metrics

Move beyond signed displacement:

- Track curvature estimation  
- Δx vs Δz slope analysis  
- Direction change along trajectory  

---

### 3. Geometry-Aware Analysis

Incorporate:

- Updated TMS bounds  
- Region segmentation (Region1, Region2, Region3)  
- Position and energy cuts  

---

### 4. Cross-Validation

Compare:

- Constant magnetic field (baseline)  
- Arbitrary field mapper  

Ensure consistent physical behavior  

---

### 5. Sanity Checks

- Verify field values are non-zero  
- Sample field at known coordinates  
- Enable Geant4 tracking diagnostics  
- Confirm step-wise particle motion  

---

## 🛠️ Workflow
GDML Geometry
↓
Magnetic Field Definition (BField / ArbBField)
↓
edep-sim Execution
↓
ROOT Output
↓
Python Analysis (OLD ❌ / NEW 🔄)
↓
Bending Validation


---

## ⚠️ Core Problem

> Are we observing **no bending**,  
> or using an **outdated method to detect it**?

---

## 🔮 Next Steps

- Build a **new geometry-aware validation script**  
- Define **robust bending observables**  
- Integrate with **ND validation framework**  
- Confirm **physical correctness of field behavior**  

---

## 🧠 Key Takeaway

> A correct simulation can appear incorrect  
> if analyzed with an outdated model.

---

## 🤝 Context

This work contributes to:

- DUNE Near Detector (ND)  
- Muon Spectrometer (TMS)  
- Simulation validation and reconstruction studies  
