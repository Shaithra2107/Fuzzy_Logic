from flask import Flask, request, jsonify, send_file
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

app = Flask(__name__)

# --- Define fuzzy variables ---
voltage = ctrl.Antecedent(np.arange(0, 21, 1), 'VoltageDeviation')
frequency = ctrl.Antecedent(np.arange(0, 2.1, 0.1), 'FrequencyVariation')
load = ctrl.Antecedent(np.arange(0, 101, 1), 'LoadImbalance')
severity = ctrl.Consequent(np.arange(0, 101, 1), 'Severity')

# Membership functions
# Voltage Membership Functions
voltage['Low'] = fuzz.trimf(voltage.universe, [0, 0, 6])  # Narrower range for Low
voltage['Medium'] = fuzz.trimf(voltage.universe, [5, 10, 15])  # Keep Medium as is
voltage['High'] = fuzz.trimf(voltage.universe, [13, 20, 20])  # Extend range for High

# Frequency Membership Functions
frequency['Stable'] = fuzz.trimf(frequency.universe, [0, 0, 0.4])  # Narrower range for Stable
frequency['SlightlyUnstable'] = fuzz.trimf(frequency.universe, [0.3, 0.7, 1.5])  # Spread out SlightlyUnstable
frequency['Unstable'] = fuzz.trimf(frequency.universe, [1.4, 2, 2])  # Shift range for Unstable

# Load Membership Functions
load['Balanced'] = fuzz.trimf(load.universe, [0, 0, 25])  # Narrow range for Balanced
load['SlightlyUnbalanced'] = fuzz.trimf(load.universe, [20, 50, 80])  # Keep SlightlyUnbalanced as is
load['Unbalanced'] = fuzz.trimf(load.universe, [75, 100, 100])  # Extend range for Unbalanced

severity['Low'] = fuzz.trimf(severity.universe, [0, 0, 30])
severity['Moderate'] = fuzz.trimf(severity.universe, [20, 50, 80])
severity['High'] = fuzz.trimf(severity.universe, [70, 100, 100])

# Fuzzy rules
# New Fuzzy Rules
rule1 = ctrl.Rule(voltage['High'] & frequency['Unstable'] & load['Unbalanced'], severity['High'])  # High severity
rule2 = ctrl.Rule(voltage['Medium'] & frequency['SlightlyUnstable'], severity['Moderate'])  # Moderate severity
rule3 = ctrl.Rule(voltage['Low'] & frequency['Stable'] & load['Balanced'], severity['Low'])  # Low severity
rule4 = ctrl.Rule(voltage['High'] | frequency['SlightlyUnstable'] | load['SlightlyUnbalanced'], severity['Moderate'])
rule5 = ctrl.Rule(voltage['Low'] & frequency['Stable'], severity['Low'])  # Low for stable voltage & frequency

severity_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5])
severity_sim = ctrl.ControlSystemSimulation(severity_ctrl)

# --- Serve HTML without templates folder ---
@app.route('/')
def home():
    return send_file('fuzzy.html')

# --- API for fuzzy detection ---
@app.route('/detect', methods=['POST'])
def detect():
    data = request.json
    voltage_input = data['voltage']
    frequency_input = data['frequency']
    load_input = data['load']

    # Set the inputs to the fuzzy logic controller
    severity_sim.input['VoltageDeviation'] = voltage_input
    severity_sim.input['FrequencyVariation'] = frequency_input
    severity_sim.input['LoadImbalance'] = load_input

    # Log the input values to verify
    print(f"Input - Voltage: {voltage_input}, Frequency: {frequency_input}, Load: {load_input}")

    # Perform the fuzzy logic computation
    severity_sim.compute()

    # Log the output and membership values for debugging
    severity_score = severity_sim.output['Severity']
    print(f"Severity Score: {severity_score}")  # Log severity score for debugging

    print(f"Membership values for Voltage: Low={voltage['Low'].mf}, Medium={voltage['Medium'].mf}, High={voltage['High'].mf}")
    print(f"Membership values for Frequency: Stable={frequency['Stable'].mf}, Unstable={frequency['Unstable'].mf}")
    print(f"Membership values for Load: Balanced={load['Balanced'].mf}, Unbalanced={load['Unbalanced'].mf}")

    # Logic for determining severity level and suggested action
    if severity_score < 30:
        severity_level = "Low Severity"
        action = "No Action Required"
    elif 30 <= severity_score < 60:
        severity_level = "Moderate Severity"
        action = "Activate Load Balancing and Monitoring"
    else:
        severity_level = "High Severity"
        action = "Immediate Isolation and Load Rerouting"

    # Send the results as JSON
    return jsonify({
        "severity_level": severity_level,
        "severity_score": severity_score,
        "suggested_action": action
    })


if __name__ == '__main__':
    app.run(debug=True)
