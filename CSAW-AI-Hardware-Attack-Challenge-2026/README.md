# CSAW 2026 - AI Hardware Attack Challenge
 [![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC_BY--NC_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)

[![](https://dcbadge.limes.pink/api/server/https://discord.gg/KEVbWs6BPU)](https://discord.gg/KEVbWs6BPU)

Welcome to the NYU CSAW 2026 AI Hardware Attack (AHA!) Challenge!

In this year's competition, teams are challenged to use generative AI to both insert hardware Trojans into FPGA-targeted hardware designs as well as demonstrate exploits for these new Trojans. The target of this competition is the Hackster board from Calico Computer, an education-focused device which includes an application microprocessor, an FPGA, and additional peripherals aimed at hardware security education.

Teams will need to reverse-engineer the FPGA bitstream provided for the Hackster board and use that, along with basic integration documentation and tests, to determine how the hardware design works and add a Trojan to it.

A preliminary qualifying round of the competition will take place across two weeks, from 18 September to 2 October. Finalists will be selected by 4 October. These teams will be brought to New York to attend CSAW in-person. The final challenge will be given at CSAW and will take place over 24 hours, where teams will be given access to the physical Hackster boards to both demonstrate their preliminary Trojans and complete the final challenge on the hardware.

**Register Here:** https://forms.gle/U9jf9WYuRjpdJjvZ7

## Table of Contents
- [Table of Contents](#table-of-contents)
- [General Guidelines](#general-guidelines)
  - [Timeline](#timeline)
  - [Teams](#teams)
  - [Communication](#communication)
  - [AI Usage](#ai-usage)
- [Qualifying Phase](#qualifying-phase)
- [Finals @ CSAW](#finals)
- [Getting Started](#getting-started)
- [Hackster Board](#hackster-board)

## General Guidelines
### Timeline
- 18 September: Qualifying Phase Launch
- 02 October: Qualifying Phase Submission Deadline
- 04 October: Finalists Notified
- 12 November: Final Challenge Released @ CSAW
- 13 November: Final Challenge Deadline & Presentations @ CSAW
- 14 November: Winners Announced @ CSAW

*Note: There is no registration deadline. Teams can register and submit up until the preliminary phase submission deadline.*

### Teams
Teams must consist of the following:
- Up to four currently-enrolled students (graduate or undergradute)
- One advisor (can be a graduate student advising and undergraduate team, or a professor advising a graduate team)

### Communication
The majority of communications about this and future competitions will be done through our Discord server. [Please feel free to join.](https://discord.gg/KEVbWs6BPU)

### AI Usage
This competition relies on significant use of generative AI. As such, detailed logs need to be kept and included in all submissions, detailing every interaction with AI. **If a submission is made without logs or the logs are missing key information, the submission may be disqualified.**

## Qualifying Phase
Details on the qualifying phase of the competition can be found in [the qualifying phase directory.](./qualifier/)

## Finals
Finals will take place at NYU during CSAW from November 12 - 14. Initial details on this phase of the competition can be found in [the finals directory.](./finals/)

## Getting Started
We recommend the [Yosys OSS CAD Suite](https://github.com/YosysHQ/oss-cad-suite-build) for use with the Hackster board. It contains all of the tools that teams should need to get started such as:
- Icarus Verilog
- GTKWave
- Yosys
- IceStorm

While you are not required to use these specific tools, the Hackster was designed to work with open-source tooling such as this.

For the first phase of the competition, teams will not have access to a physical Hackster board, however, [this documentation](https://cgi.cse.unsw.edu.au/~cs6420/labs/lab00introduction/) on getting the Hackster set up (with the OSS CAD Suite) could prove helpful in understanding the connections on the board and how the whole system is built. You can also see the [hackster-programmer GitHub](https://github.com/kiwih/hackster-programmer) repo for additional information like the PCB schematics.

## Hackster Board
The *Hackster* board from Calico Computer is a hardware security learning platform designed by Dr. Hammond Pearce. It contains an application processor ([RP2040](https://www.raspberrypi.com/products/rp2040/)), a programming processor (RP2040), FPGA ([iCE40-UP5K](https://www.latticesemi.com/en/products/fpgaandcpld/ice40ultraplus)), and additional circuitry and components for side-channel power analysis.

The Hackster hardware is under the CC BY-SA 4.0 license. Any use of the hardware documentation (such as the schematic) or the gerber files for the Hackster should be attributed as follows:

"Hammond Pearce, UNSW Sydney - CC BY-SA 4.0"

## Previous Competitions
We've run versions of this competition for the past several years at [NYU's CSAW Event](https://www.csaw.io/ai-hardware-attack-challenge). We also [published results from the first two competitions](https://ieeexplore.ieee.org/document/11169309), which might help serve as inspiration if you find your team is stuck.

