# Technical Data — Blueprint Invariant Overlay (v1.0.0)

## 1. Geometry Layer

### 1.1 Concentric Architecture
- Outer ring: dashed, pale gold (#ffd484)
- Inner geometry: Tusi-couple overlay (#d4b8ff)
- Radial partitions: 12, monospaced labels
- Dial: 260 (WHEEL + WHEEL_OFFSET)

### 1.2 Harmonic Ratio
ωB / ωA = 1.37  
Chosen to avoid phase locking and maintain an open coherence trace.

---

## 2. Invariant Layer

### 2.1 Hierarchy Ratio
H = T_focus / T_boundary  
Boundary = longest member period.

### 2.2 Closure
closure = exp( - ln²(H/260) )  
Bounded in (0, 1].

### 2.3 Hill Ratio
Keplerian, warns on unbound outer members.

---

## 3. Coherence Layer

### 3.1 Gate Phases
φA = 2π ωA sA(s)  
φB = 2π ωB sB(s)

### 3.2 Coherence
C(s) = cos(φA − φB)

### 3.3 Ring Event
Triggered on local peak above threshold τ.

---

## 4. Differential Layer

### 4.1 Drift Extraction
ΔC(s) = C_gate(s) − C_tusi(s)

### 4.2 Residual Spectrum
FFT after removing facility periodic terms.

---

## 5. Cryptographic Layer

### 5.1 Invariant Hash Block (IHB)
Contains:
- Tusi trace hash
- Gate trace hash
- Differential trace hash
- Residual spectrum hash
- H, closure
- Ring count
- Timestamp
- Device hash

### 5.2 Sentinel_dot SHA-256
Final sealing hash over entire IHB.

### 5.3 SVC Wrapper
Metadata container for blueprint image:
- geometry spec
- invariant parameters
- cryptographic binding
- provenance
- audit metadata

---

## 6. Packaging Layer

Release bundle:
- blueprint.jpeg
- blueprint.svc
- invariant_hash_block.json
- sentinel_sha256.txt
- orrery.py
- daemon_gate.py
- validation_suite/
- manifest.json
- package_sha256.txt
- README.md
- TECHNICAL_DATA.md
- REPLICATION_PROTOCOL.md
- ANNOUNCEMENT_TEXT.md
- DOI_ABSTRACT.md
- RELEASE_NOTES_v1.0.0.md

---

## 7. Publication Layer

1. GitHub release (v1.0.0)
2. Zenodo deposition → DOI
3. Compliance report
4. Announcement text
5. Abstract for citation

---

## 8. Validation Layer

### 8.1 Classification
- periodic → environmental → null  
- secular → candidate  
- source flip → invalid  

### 8.2 Reproducibility Tests
Validation suite ensures:
- deterministic hashing
- invariant stability
- pipeline correctness
