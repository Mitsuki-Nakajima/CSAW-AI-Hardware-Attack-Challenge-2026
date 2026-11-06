# CSAW 2026 AI Hardware Attack (AHA!) Challenge — Technical Brief

**Team:** Mitsuki Nakajima · Yan Pang
**Course:** Computer Engineering Design, NYU Tandon
**Target device:** Lattice iCE40-UP5K FPGA (Hackster security-education board)
**Status:** Experiment A verified in simulation · Experiment B reverse-engineering partially complete
**Challenge repo:** https://github.com/JBlocklove/CSAW-AI-Hardware-Attack-Challenge-2026

---

## 1. Overview

The challenge is to use a large language model (LLM) to (a) reverse-engineer a compiled FPGA
bitstream for a cryptographic accelerator, (b) insert a hardware Trojan into the recovered
design, and (c) demonstrate an exploit for that Trojan in simulation. Per the rules, the Trojan
and exploit must be produced by the AI, and every AI interaction must be logged.

We have organized the work into two experiments:

| | Experiment A | Experiment B |
|---|---|---|
| **Goal** | Prove the AI generate-and-verify loop works | Reverse-engineer and understand the real target |
| **Design** | Public AES-128 Verilog (reference) | The actual CSAW `ice40_bitstream.bin` |
| **Status** | ✅ Complete and verified in simulation | 🟡 Bitstream decoded & cipher modeled; target Trojan not yet inserted |

**Main takeaway:** We verified an LLM-generated hardware Trojan on a reference AES design,
decoded the actual CSAW FPGA bitstream, reconstructed its structural Verilog, identified its
physical I/O pins, and validated a software model of the supplied four-round cipher through
encryption and decryption. The next milestone is verifying the recovered FPGA implementation
and generating a target-specific Trojan.

---

## 2. Proposed repository layout

```
.
├── TECHNICAL_BRIEF.md            # this document
├── presentation/
│   └── AHA_Progress_Report.pptx  # progress presentation
├── experiment_a/                 # AI Trojan on the AES-128 reference core
│   ├── ghost_portkey_ai.ipynb    # the pipeline we ran
│   ├── ghost_portkey_ai.html     # exported run — serves as the AI interaction log
│   ├── generated/                # AI output: modified Verilog + taxonomy reports
│   ├── tb/                        # comparison testbench
│   └── experiment_a.vcd          # waveform output
├── reverse_engineering/          # Experiment B
│   ├── unpacked.asc              # IceStorm ASCII config
│   ├── recovered.v               # structural netlist
│   ├── recovered_pins.v          # netlist with physical pin numbers
│   └── verify_cipher.py          # Python reference model of the cipher
└── ai_logs/                      # collected prompt/response logs (in progress)
```

---

## 3. Experiment A — AI-generated hardware Trojan (verified)

### 3.1 Generation

We executed the Portkey-adapted GHOST notebook (`ghost_portkey_ai.ipynb`), an implementation of
the GHOST framework (Faruque et al., *"Unleashing GHOST: An LLM-Powered Framework for Automated
Hardware Trojan Design"*). The pipeline runs through **NYU's Portkey AI gateway** using
**Gemini 2.5 Pro** (`@vertexai/gemini-2.5-pro`); the model is selectable via `PORTKEY_MODEL`.

The notebook submitted three public AES-128 Verilog modules (`aes_128.v`, `round.v`, `table.v`)
to the model with an instruction to insert a **T1 (Change Functionality)** Trojan. For each
module the model returned modified Verilog plus a structured taxonomy report.

### 3.2 The Trojan (`aes_128.v`)

- **Trigger (sequential):** the **upper 32 bits** of the 128-bit plaintext equal
  `0xDEADBEEF` for **16 consecutive clock cycles**. A sustained sequential trigger makes
  accidental activation highly unlikely.
- **Payload (combinational):** once active, the final ciphertext is corrupted by XORing its
  least-significant byte with `key[7:0]`:

  ```verilog
  assign out = trojan_active ? (original_out ^ {120'b0, key[7:0]}) : original_out;
  ```

### 3.3 Taxonomy (model-generated)

| Field | Value |
|---|---|
| Vulnerability category | T1 — Change Functionality |
| Insertion phase | Design |
| Abstraction level | Register-transfer level (RTL) |
| Activation mechanism | Triggered internally |
| Effect | Change functionality |
| Location | Processor (as labeled by GHOST) |
| Characteristics | Distribution: Localized · Size: Small · Type: Functional |

### 3.4 Verification

We wrote a comparison testbench (original vs. Trojan-modified) and ran it in **Icarus Verilog**.

| Test case | Expected | Result |
|---|---|---|
| Normal operation | Original & modified ciphertext match | **PASS** |
| Trigger held 15 cycles | Trojan inactive | **PASS** |
| Trigger held 16 cycles | Trojan active, ciphertext corrupted | **PASS** |
| Trigger removed | Original behavior restored | **PASS** |

Observed ciphertext for the tested input:

```
normal : 0545aad56da2a97c3663d1432a3d1c84
trojan : 0545aad56da2a97c3663d1432a3d1c85   (final byte 84 → 85)
```

A waveform file (`experiment_a.vcd`) was produced for inspection in GTKWave.

### 3.5 Engineering review of the AI output

Successfully generated Verilog still requires human review. Two items we flagged:

1. **Interface change** — the model silently added a new `rst_n` reset input, which must be
   reconciled against the original module interface for clean integration.
2. **Key/ciphertext alignment** — the payload uses the *current* `key[7:0]`; because the AES
   core is pipelined, alignment between the key and the corresponding ciphertext needs
   verification.

**Scope note:** Experiment A is a controlled demonstration on public AES Verilog. It is **not**
an attack on the actual CSAW hardware, and the testbench checks selected behaviors rather than
exhaustive AES correctness.

---

## 4. Experiment B — Reverse engineering the real bitstream (partial)

### 4.1 Bitstream recovery

Using **Project IceStorm** (in VS Code, macOS) on the provided `qualifier/ice40_bitstream.bin`:

```bash
iceunpack qualifier/ice40_bitstream.bin > reverse_engineering/unpacked.asc
```

- Produced an ASCII configuration of **≈718 KB**.
- Header identifies the device as `.device 5k` (the iCE40-UP5K).

```bash
icebox_vlog reverse_engineering/unpacked.asc > reverse_engineering/recovered.v
```

- Produced `recovered.v`: a **45,711-line** structural Verilog netlist.
- Top-level module is named **`chip`**.
- Contains **four `SB_RAM40_4K`** block-RAM primitive instances.

> **Limitation:** This is a low-level structural netlist (generic wires + routing), **not**
> recovered high-level RTL. Yosys-based optimization and behavioral reconstruction have **not**
> yet been performed.

### 4.2 Physical pin recovery

```bash
icebox_vlog -l reverse_engineering/unpacked.asc > reverse_engineering/recovered_pins.v
```

| Direction | Package pins |
|---|---|
| Inputs | 36 · 25 · 28 · 32 · 34 · 27 |
| Outputs | 38 · 23 · 31 |

> **Limitation:** These are **physical package pins only**. We have **not** yet mapped them to
> logical signals (SCK, MOSI, MISO, START, RESET, BUSY, ENC_DEC).

---

## 5. Target cryptographic architecture

Source documentation: `les_block_diagrams.pdf` and `spi_ice40_crypto_ip_test.py` (both provided).

The target is a custom, lightweight **32-bit cryptographic accelerator**:

- 32-bit SPI shift register front end (RP2040 is the SPI controller).
- Separate encryption and decryption cores.
- **Four rounds** per operation; round-controller FSM `IDLE → R1 → R2 → R3 → IDLE`.
- AES S-box / inverse S-box transformations and 8-bit word rotations.
- A single **fixed 32-bit XOR key**, reused each round (no key schedule).
- Control signals: START, BUSY, RESET, and encrypt/decrypt select.

**Fixed key:** `K = 0x8E043CB1`

> **Important:** This key is **documented in the supplied block diagrams**. We did **not**
> independently extract it from the bitstream or recover it through cryptanalysis.

**Known plaintext/ciphertext pair** (from the MicroPython test program):

```
plaintext  : 0x59C359C3
ciphertext : 0x9CD84392
```

> **Open issue:** We observed an apparent inconsistency between the encrypt/decrypt control
> labeling in the block diagram and the MicroPython test program. The logical polarity of the
> recovered FPGA's mode control has not yet been verified.

---

## 6. Python reference model (verified)

`reverse_engineering/verify_cipher.py` implements the documented four-round transformations
(AES S-box lookups, 8-bit rotation, fixed key) and was tested against the supplied vector.

**Encryption** — `x_next = ROTL8( SBOX( x ⊕ K ) )`, repeated four times:

| Round | Output |
|---|---|
| 1 | `0xC64D400E` |
| 2 | `0x3B100852` |
| 3 | `0xFA1811D5` |
| 4 | `0x9CD84392` |

Expected `0x9CD84392`, actual `0x9CD84392` → **ENCRYPTION PASS**

**Decryption** — `x_next = INV_SBOX( ROTR8( x ) ) ⊕ K`:

| Round | Output |
|---|---|
| 1 | `0xFA1811D5` |
| 2 | `0x3B100852` |
| 3 | `0xC64D400E` |
| 4 | `0x59C359C3` |

Recovered plaintext `0x59C359C3` = original → **DECRYPTION PASS**

> **Scope:** This validates our understanding of the *documented mathematical algorithm* for the
> tested vector. It does **not** independently verify the behavior of the reconstructed FPGA
> netlist, and it is not an exhaustive cryptographic validation.

---

## 7. AI pipeline, tools, and guardrails

### 7.1 How the design reaches the LLM

GHOST-style structured prompting. Each request packages: the Verilog design (AES-128 so far —
the recovered netlist is the planned next input), a vulnerability class to insert (T1–T4), a
prompting strategy, and a strict output format (code + explanation + trigger + payload +
taxonomy). All requests go through the NYU Portkey gateway; the API key is read from the
environment and kept out of the committed notebook.

### 7.2 Open-source tools

**Used so far:** Project IceStorm (`iceunpack`, `icebox_vlog`) · Icarus Verilog · GHOST
notebook · NYU Portkey → Gemini 2.5 Pro · Python / PyCryptodome · Git / GitHub · VS Code.

**Planned / not yet used:** Yosys (structural netlist cleanup) · GTKWave (visual waveform
inspection) · full target-specific hardware simulation.

### 7.3 LLM security guardrails — honest position

Working through the authorized NYU gateway, the GHOST framing casts the model as a hardware
design and verification expert generating Trojan-detection benchmarks; under that framing the
model produced the modified Verilog directly. **Successful generation does not, by itself, prove
that any model security guardrail was bypassed.** We did not jailbreak the model and make no such
claim. A systematic evaluation of guardrail behavior (which categories or framings are refused)
has not yet been completed. Every interaction is logged, per the challenge rules.

---

## 8. Division of labor

**Completed to date — all by Mitsuki Nakajima:** GHOST notebook execution and initial
generation; Experiment A Trojan analysis and simulation; CSAW repository setup; IceStorm
installation; bitstream decoding; structural Verilog reconstruction; physical pin recovery;
cipher architecture analysis; Python encryption/decryption reference-model verification.

**Planned role division (proposed, going forward):**

- **Mitsuki** — reverse-engineering and Trojan design.
- **Yan** — AI-pipeline automation, exploit/demo, AI logging.
- **Joint** — target-specific Trojan generation, simulation, AI logging, and final submission.

---

## 9. Remaining work

1. Map the recovered FPGA physical pins to their logical functions.
2. Validate the recovered structural Verilog against the documented SPI protocol and the known
   encryption/decryption test vectors.
3. Improve the readability of the recovered logic where practical (Yosys and/or AI-assisted).
4. Provide the recovered design information to the LLM.
5. Generate a hardware Trojan targeting the actual CSAW circuit. *(Type not yet selected —
   T2 key exfiltration is a candidate, not an achieved result.)*
6. Develop an AI-generated exploit and verification testbench meeting the competition rules.
7. Verify ordinary operation and triggered malicious behavior.
8. Collect and organize AI prompt/response logs.
9. Document results, taxonomy, and reproducibility steps.
10. Package the required files and upload the presentation to the team repository.

---

## 10. Reproducibility — Experiment B quickstart

```bash
# 1. Decode the bitstream to ASCII configuration
iceunpack qualifier/ice40_bitstream.bin > reverse_engineering/unpacked.asc

# 2. Reconstruct a structural Verilog netlist
icebox_vlog reverse_engineering/unpacked.asc > reverse_engineering/recovered.v

# 3. Reconstruct with physical package pin numbers
icebox_vlog -l reverse_engineering/unpacked.asc > reverse_engineering/recovered_pins.v

# 4. Verify the cipher reference model against the known test vector
python3 reverse_engineering/verify_cipher.py
# expected: ENCRYPTION PASS / DECRYPTION PASS
```

---

## 11. Summary of what is verified vs. supplied vs. pending

| Item | Status |
|---|---|
| AI-generated Trojan (AES-128) behaves as specified | ✅ Verified in simulation |
| Bitstream → structural netlist | ✅ Done (structural only) |
| Physical I/O pin numbers | ✅ Recovered |
| Cipher algorithm & key `0x8E043CB1` | ℹ️ Supplied in diagrams (not extracted) |
| Cipher math (enc + dec on known vector) | ✅ Verified via Python model |
| Pins → logical signal mapping | ⏳ Pending |
| Behavioral RTL recovery (Yosys / AI lift) | ⏳ Pending |
| Target-specific Trojan + exploit | ⏳ Pending |
| Independent key recovery (bonus) | ⏳ Pending |
