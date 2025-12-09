# Västtrafik for Home Assistant

This is the repository for the extended and modified Västtrafik integration for Home Assistant. It provides a custom frontend visualization feature for whole journey planning. It is an extension that allows you to retrieve journeys between two pre-configured stops with buttons.

This document covers the setup and configuration for this extension.

## Features

    *   Define in your configuration (e.g. "Go to Work").
    *   Use a customized Lovelace card with buttons to get a whole trip plan.
    *   View departure time and information on all required lines for the journey.

## How the Journey Planner Differs from the Official Integration

It is important to understand that the new journey-planning feature is an **extension** of the functionality found in the official Västtrafik integration and uses a different setup.

The official integration answers: "When is the next bus leaving from my stop?".
This extension answers: "What is the best way for me to get from A to B right now?".

## Prerequisites

*   A running instance of Home Assistant.
*   A Västtrafik API Key and Secret. You can obtain these from the Västtrafik Developer Portal.

## Installation (Manual)

### Part 1: Backend Setup
Make sure you have the files secured from our forked Home Assistant repository.

### Part 2: Frontend Lovelace Card Installation

This step installs the custom card that is needed to display the Journey Planner on your dashboard. You must manually create the JavaScript resource file, which will be given here.

1.  Navigate to your Home Assistant configuration directory, name it config/

2.  Create a folder named www if it does not exist.

3.  Create a new file vasttrafik-card.js in directory www so that it has the path: config/www/vasttrafik-card.js.

4.  Paste the following code into vasttrafik-card.js:

"

console.log("Vasttrafik card loaded");

class VasttrafikCard extends HTMLElement {

    setConfig(config) {
        this._config = config;
        this._selectedJourney = 0;
        this.innerHTML = `
            <style>
                .vt-button-row {
                    display: flex;
                    gap: 8px;
                    margin-bottom: 16px;
                }

                .vt-btn {
                    border-radius: 999px;
                    padding: 6px 16px;
                    border: none;
                    font: inherit;
                    cursor: pointer;
                    background: var(--primary-color);
                    color: var(--text-primary-color, #fff);
                }

                .vt-btn.outlined {
                    background: transparent;
                    color: var(--primary-text-color);
                    border: 1px solid var(--primary-color);
                }

                .vt-btn:hover{
                    background-image: linear-gradient(rgb(0 0 0/40%) 0 0);
                }
            </style>


            <ha-card header="Västtrafik">
                <div id="content" style="padding: 16px;">Loading...</div>
            </ha-card>
        `;
    }

    set hass(hass) {
        this._hass = hass;
        this._render();
    }

    _render() {
        const entity = this._config.entity;
        const stateObj = this._hass.states[entity];
        const content = this.querySelector("#content");

        if (!stateObj) {
            content.innerHTML = "Entity not found";
            return;
        }

        const attrs = stateObj.attributes;

        // Gather all journeys dynamically
        const journeys = Object.entries(attrs)
            .filter(([key, value]) => value.legs)
            .map(([key, value]) => ({name: key, ...value}));

        let html = ``;

        html += `<div class="vt-button-row">`;
        journeys.forEach((journey, index) => {
            html += `<button class="vt-btn ${this._selectedJourney === index ? "outlined" : ""}" data-index="${index}">${journey.name}</button>`;
        });
        html += `</div>`;

        const selectedJourney = journeys[this._selectedJourney];

        if (selectedJourney) {
            html += `<h4>${selectedJourney.name}: ${selectedJourney.from} → ${selectedJourney.to}</h4>`;
            // Ensure legs exist before accessing [0]
            if (selectedJourney.legs && selectedJourney.legs[0]) {
                 html += `<h4>Departure time: ${selectedJourney.legs[0].time}</h4>`;
            }

            const legs = selectedJourney.legs || [];
            if (legs.length > 0) {
                html += "<ol>";
                for (const leg of legs) {
                    html += `<li>
                                <strong>From:</strong> ${leg.from} <br>
                                <strong>To:</strong> ${leg.to} <br>
                                <strong>Line:</strong> ${leg.line} <br>
                                <strong>Direction:</strong> ${leg.direction} <br>
                                <strong>Track:</strong> ${leg.track || "N/A"} <br>
                                <strong>Accessible:</strong> ${leg.accessible ? "Yes" : "No"}
                            </li>
                    `;
                }
                html += "</ol>";
            } else {
                html += "<p> No legs available </p>";
            }
        } else {
             html += "<p> Select a journey </p>";
        }

        content.innerHTML = html;

        content.querySelectorAll(".vt-btn").forEach((btn) => {
            btn.addEventListener("click", (ev) => {
                this._selectedJourney = Number(ev.target.dataset.index);
                this._render();
            });
        });
    }
}

customElements.define("vasttrafik-card", VasttrafikCard);

"

## Update Configuration.yaml

Modify your `configuration.yaml` file to include the sensor setup, register the custom card resource and enable YAML mode for Lovelace.

Important: Replace key and secret with your valid Västtrafik API credentials!


"

# Loads default set of integrations. Do not remove.
default_config:
demo:

# Load frontend themes from the themes folder
frontend:
  themes: !include_dir_merge_named themes

automation: !include automations.yaml
script: !include scripts.yaml
scene: !include scenes.yaml

logger:
  default: info
  logs:
    homeassistant.components.assist_pipeline: debug
    homeassistant.components.conversation: debug
    homeassistant.helpers.intent: debug

# Västtrafik Integration Configuration
sensor:
  - platform: vasttrafik
    key: "YOUR_API_KEY"
    secret: "YOUR_API_SECRET"
    departures:
      - name: Work
        from: Beryllgatan
        heading: Chalmers
        transfers:
          - Brunnsparken

      - name: School
        from: Engdahlsgatan
        heading: Lindholmen

      - name: Gym
        from: Nordstan
        heading: Chalmers

# Lovelace (Dashboard) Configuration
lovelace:
  mode: yaml
  resources:
    - url: /local/vasttrafik-card.js
      type: module

"

## Create UI Dashboard

Create a file in config directory called ui-lovelace.yaml. This file defines the layout of your dashboard since mode: yaml was enabled above.

Note: The entity ID (e.g. sensor.work) is generated based on the name you defined in the sensor configuration. Please update the ID according to your chosen name for the journey.

Paste this in the new file ui-lovelace.yaml:

"

views:
  - name: Example
    cards:
      # Display the custom card for the "Work" journey
      - type: "custom:vasttrafik-card"
        entity: sensor.work

      # Example for the "School" journey
      - type: "custom:vasttrafik-card"
        entity: sensor.school

"

## Finalize

1. Restart Home Assistant Core to load the new configuration and resources.

2. Open the Home Assistant dashboard.

3. You may need to perform a Hard Refresh (Ctrl+Shift+R / Cmd+Shift+R) in your browser to clear the cache and load the new JavaScript card.


Good Luck!
