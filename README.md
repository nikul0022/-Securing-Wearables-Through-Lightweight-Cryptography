# Securing Wearables Through Lightweight Cryptography

**Master's capstone project** — a comparative study of lightweight cryptographic algorithms for resource-constrained IoT/wearable devices, backed by a working Python simulation of a healthcare IoT pipeline (smartwatch + GPS tracker → gateway → cloud), including live MITM and data-tampering attacks against both an unprotected and a cryptographically-protected version of the system.

*Master of Information Systems Security Management, Concordia University of Edmonton — submitted April 2025.*

## Problem

IoT wearables (smartwatches, GPS trackers, heart-rate monitors) are increasingly used in healthcare and sports to transmit sensitive physiological and location data — but they're resource-constrained: limited CPU, memory, and battery. Standard cryptography (RSA, AES-256) is often too heavy for these devices, creating a real tension between security and performance. This project investigates which lightweight cryptographic primitives actually hold up under this constraint, and proves it with a live simulation rather than just theory.

## Algorithm Comparison

Benchmarked five cryptographic primitives across power consumption, latency, throughput, and security level:

| Algorithm | Type | Key Size | Power (mJ) | Latency (ms) | Throughput (kbps) | Security |
|---|---|---|---|---|---|---|
| AES-128 | Symmetric | 128 bits | 0.39 | 4.1 | 1315 | High |
| ECC-256 | Asymmetric | 256 bits | 0.78 | 10.3 | 600 | High |
| RSA-3072 | Asymmetric | 3072 bits | 4.7 | 82.6 | 210 | High |
| Speck-128 | Symmetric | 128 bits | 0.28 | 3.8 | 1450 | Medium-High |
| HMAC-SHA256 | Authentication | N/A | 0.09 | 2.5 | 1700 | High |

**Selected approach:** AES-128 (encryption) + HMAC-SHA256 (integrity) for device-to-device communication, with ECDH (key exchange) and ECDSA (digital signatures) for authentication — chosen for the best balance of strong security with minimal power/latency overhead on battery-powered wearables.

## System Architecture

Three-layer design: IoT devices (smartwatch, GPS tracker) → IoT gateway (aggregation + TLS/SSL to cloud) → cloud database, with AES-128/HMAC-SHA256 securing device-to-device traffic and ECDH/ECDSA handling key exchange and authentication end-to-end:

<img width="927" height="756" alt="image" src="https://github.com/user-attachments/assets/dce03f62-ce74-4899-8d40-b05165af5bec" />

## Simulation — Built and Attacked in Python

Built a full working simulation (smartwatch.py, gps_tracker.py, cloud_server.py, plus MITM and data-tampering attack scripts) and ran it through four scenarios:

### Scenario 1 — Baseline (No Encryption)
Transmitted simulated smartwatch and GPS data over plain HTTP and captured it in Wireshark — confirming the data (heart rate, coordinates) was fully readable in transit:

<img width="1197" height="996" alt="image" src="https://github.com/user-attachments/assets/0d00de1f-2613-4b58-acf3-d4f6ade09acf" />

### Scenario 2 — With AES-128 + HMAC-SHA256
Implemented encryption and re-ran the transmission — confirmed via console output that data was now sent as unreadable ciphertext, at effectively the same latency as the unencrypted baseline:

<img width="583" height="270" alt="image" src="https://github.com/user-attachments/assets/5a0c749d-374d-47b0-99f6-c0cb9eb70131" />

### Scenario 3 — Attacking the Encrypted System
Attempted to intercept and modify the now-encrypted traffic. The moment tampered ciphertext reached the cloud server, HMAC verification caught the mismatch in real time and rejected it:

<img width="840" height="296" alt="image" src="https://github.com/user-attachments/assets/146b5b53-e4a5-4700-9856-3da1386a4af7" />

> `[CLOUD] ⚠️HMAC verification failed! Data might be tampered.`

This is the core result of the project: the encrypted pipeline successfully detected and rejected tampered data, while unmodified traffic verified and passed through normally.

### Scenario 4 — Attacking the Unprotected System
For comparison, ran the same MITM and tampering attacks against the **unencrypted** version. The attacker script intercepted plaintext GPS coordinates in real time with no effort:

<img width="531" height="481" alt="image" src="https://github.com/user-attachments/assets/f1c60e8c-a6b3-443f-9ccb-7f18052c84af" />

...and successfully altered heart-rate and GPS values in-flight, with the modified data accepted silently by the cloud server (no integrity check to catch it):

<img width="1253" height="657" alt="image" src="https://github.com/user-attachments/assets/d99a300c-008a-4cda-b71c-9a7167b937bf" />

**The contrast between Scenario 3 and Scenario 4 is the entire thesis of the project**, made concrete: identical attack code, wildly different outcomes, purely due to the presence or absence of AES-128 + HMAC-SHA256.

## Key Results

- Combined AES-128 + HMAC-SHA256 overhead: ~5-6ms latency, ~0.5-0.6 mJ energy per transmission — a **negligible ~0.08% of a typical 200mAh wearable battery per hour**
- The protected pipeline successfully detected 100% of tampering attempts via HMAC mismatch, with no false rejections of legitimate traffic
- The unprotected pipeline had zero resistance to either eavesdropping (MITM) or data tampering — both attacks succeeded silently
- Demonstrated that strong security and wearable-appropriate performance are not mutually exclusive when the right lightweight primitives are chosen

## Key Takeaways

- Went beyond a literature review — built and personally attacked a working system to generate original, verifiable evidence rather than citing others' benchmarks alone
- Practiced full-stack security thinking: algorithm selection and justification, system architecture design, offensive testing (MITM, tampering, replay considerations), and defensive validation (HMAC integrity checks) in one project
- Learned to communicate security trade-offs (power vs. latency vs. security level) in a way that supports real engineering decisions, not just academic comparison

## Tools & Technologies
Python, Flask (cloud server simulation), Wireshark, AES-128, HMAC-SHA256, ECDH/ECDSA (proposed), VS Code

## Future Work
Quantum-resistant algorithm evaluation, edge-computing integration for local threat detection, scalability testing across larger device fleets, and real-world field trials beyond simulation.

*Full capstone paper (28 pages, IEEE-style citations) and complete Python source (smartwatch.py, gps_tracker.py, cloud_server.py, MITM/tampering scripts) available on request.*
