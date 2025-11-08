# OpenKNX Nuki

Das OpenKNX-Nuki-Modul erlaubt die Steuerung von bis zu 10 Nuki Smart Locks oder Nuki Openern in Bluetooth-Reichweite.

## Features

- Nuki über Bluetooth steuern

## Anwenderdokumentation

Die Anwenderdokumentation ist [hier](./doc/Applikationsbeschreibung.md) zu finden.

## Firmware

Eine vorkompilierte Firmware ist [hier](https://github.com/OpenKNX/OAM-Nuki/releases) zu finden. ZIP-Datei herunterladen, entpacken und der Anleitung im README folgen.

## Hardware

Als Hardware kann jede OpenKNX- oder OpenKNX-Ready-Hardware mit Bluetooth verwendet werden.
Die vorkompilierte Firmware unterstützt:

- [Adafruit ESP32 Feather V2](https://github.com/OpenKNX/OpenKNX/wiki/Adafruit-ESP32-Feather-V2)

### Optional bei Adafruit ESP32 Feather V2: Zusätzlicher Prog-Taster und LED

An Pin GPIO 7 (RX) und/oder GPIO 20 (am Stecker) kann jeweils ein zusätzlicher Taster angeschlossen werden. Dieser muss gegen GND schalten.

An Pin GPIO 8 (TX) und/oder GPIO 22 (am Stecker) kann mit einem 100-Ohm-Widerstand eine LED (Anode) angeschlossen werden. Die Kathode mit GND verbinden.

## Lizenz

Diese Software steht unter der [GNU GPL v3](LICENSE).
