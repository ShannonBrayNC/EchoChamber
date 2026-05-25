# EchoChamber Integrations

## Overview

EchoChamber acts as the multilingual interoperability layer for Lantern.

Every integrated tool should communicate using shared contracts defined in `contracts/schemas/`.

## ETS

ETS uses EchoChamber to:

- translate governance artifacts
- localize evidence summaries
- produce multilingual immutable records
- support cross-language civic/research workflows

### Constraints

- provenance required
- voice generation disabled by default
- immutable artifacts preserved

## OpsHelm

OpsHelm uses EchoChamber to:

- translate customer queue briefs
- localize executive updates
- generate multilingual meeting prep
- create customer-safe audio summaries

### Constraints

- workspace isolation mandatory
- evidence references preserved
- customer formatting preserved

## Christina

Christina uses EchoChamber to:

- provide multilingual business assistance
- communicate with customers
- generate pronunciation coaching
- speak with localized tone and intent

### Constraints

- customer-safe outputs
- tone-aware translation
- consent-aware voice generation

## SignalForge

SignalForge acts as the canonical contract registry and schema synchronization layer.

SignalForge should eventually:

- mirror contract versions
- validate schema compatibility
- coordinate cross-platform releases
- preserve provenance between systems

## Content Engine

Content Engine uses EchoChamber for:

- multilingual scripts
- AI video dialogue
- audiobook narration
- subtitle and transcript generation

### Constraints

- preserve emotional tone
- support multi-speaker flows
- preserve screenplay formatting

## EchoLiving

EchoLiving uses EchoChamber for:

- multilingual guest messaging
- check-in instructions
- hospitality phrasebooks
- emergency and safety communication

## Standard Request Lifecycle

1. Caller creates request.
2. Request validated against schema.
3. EchoChamber generates translation.
4. Optional pronunciation guidance created.
5. Optional ElevenLabs audio generated.
6. Artifact metadata stored.
7. Structured response returned.
