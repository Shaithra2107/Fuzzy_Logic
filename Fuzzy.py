import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt

# --- Define fuzzy variables ---
voltage = ctrl.Antecedent(np.arange(0, 21, 1), 'VoltageDeviation')
frequency = ctrl.Antecedent(np.arange(0, 2.1, 0.1), 'FrequencyVariation')
load = ctrl.Antecedent(np.arange(0, 101, 1), 'LoadImbalance')
severity = ctrl.Consequent(np.arange(0, 101, 1), 'Severity')

# Membership functions
voltage['Low'] = fuzz.trimf(voltage.universe, [0, 0, 6])  # Narrower range for Low
voltage['Medium'] = fuzz.trimf(voltage.universe, [5, 10, 15])  # Keep Medium as is
voltage['High'] = fuzz.trimf(voltage.universe, [13, 20, 20])  # Extend range for High

frequency['Stable'] = fuzz.trimf(frequency.universe, [0, 0, 0.4])  # Narrower range for Stable
frequency['SlightlyUnstable'] = fuzz.trimf(frequency.universe, [0.3, 0.7, 1.5])  # Spread out SlightlyUnstable
frequency['Unstable'] = fuzz.trimf(frequency.universe, [1.4, 2, 2])  # Shift range for Unstable

load['Balanced'] = fuzz.trimf(load.universe, [0, 0, 25])  # Narrow range for Balanced
load['SlightlyUnbalanced'] = fuzz.trimf(load.universe, [20, 50, 80])  # Keep SlightlyUnbalanced as is
load['Unbalanced'] = fuzz.trimf(load.universe, [75, 100, 100])  # Extend range for Unbalanced

severity['Low'] = fuzz.trimf(severity.universe, [0, 0, 30])
severity['Moderate'] = fuzz.trimf(severity.universe, [20, 50, 80])
severity['High'] = fuzz.trimf(severity.universe, [70, 100, 100])

# Fuzzy rules
rule1 = ctrl.Rule(voltage['High'] & frequency['Unstable'] & load['Unbalanced'], severity['High'])
rule2 = ctrl.Rule(voltage['Medium'] & frequency['SlightlyUnstable'], severity['Moderate'])
rule3 = ctrl.Rule(voltage['Low'] & frequency['Stable'] & load['Balanced'], severity['Low'])
rule4 = ctrl.Rule(voltage['High'] | frequency['SlightlyUnstable'] | load['SlightlyUnbalanced'], severity['Moderate'])
rule5 = ctrl.Rule(voltage['Low'] & frequency['Stable'], severity['Low'])

severity_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5])
severity_sim = ctrl.ControlSystemSimulation(severity_ctrl)

# --- Function to take user input ---
def get_user_input():
    try:
        voltage_value = float(input("Enter Voltage (0 to 20): "))
        frequency_value = float(input("Enter Frequency (0 to 2): "))
        load_value = float(input("Enter Load (0 to 100): "))
        return voltage_value, frequency_value, load_value
    except ValueError:
        print("Invalid input! Please enter numerical values within the specified ranges.")
        return get_user_input()

def plot_current_position(voltage_value, frequency_value, load_value):
    """
    This function will plot the current position of voltage, frequency, and load on a graph.
    """
    plt.figure(figsize=(10, 6))

    # Plot Voltage Deviation
    plt.subplot(1, 3, 1)
    plt.plot(voltage.universe, voltage['Low'].mf, label='Low')
    plt.plot(voltage.universe, voltage['Medium'].mf, label='Medium')
    plt.plot(voltage.universe, voltage['High'].mf, label='High')
    plt.axvline(x=voltage_value, color='r', linestyle='--', label='Current Voltage')
    plt.title('Voltage Deviation')
    plt.xlabel('Voltage')
    plt.ylabel('Membership')
    plt.legend()

    # Plot Frequency Variation
    plt.subplot(1, 3, 2)
    plt.plot(frequency.universe, frequency['Stable'].mf, label='Stable')
    plt.plot(frequency.universe, frequency['SlightlyUnstable'].mf, label='Slightly Unstable')
    plt.plot(frequency.universe, frequency['Unstable'].mf, label='Unstable')
    plt.axvline(x=frequency_value, color='r', linestyle='--', label='Current Frequency')
    plt.title('Frequency Variation')
    plt.xlabel('Frequency')
    plt.ylabel('Membership')
    plt.legend()

    # Plot Load Imbalance
    plt.subplot(1, 3, 3)
    plt.plot(load.universe, load['Balanced'].mf, label='Balanced')
    plt.plot(load.universe, load['SlightlyUnbalanced'].mf, label='Slightly Unbalanced')
    plt.plot(load.universe, load['Unbalanced'].mf, label='Unbalanced')
    plt.axvline(x=load_value, color='r', linestyle='--', label='Current Load')
    plt.title('Load Imbalance')
    plt.xlabel('Load')
    plt.ylabel('Membership')
    plt.legend()

    # Show the plot
    plt.tight_layout()
    plt.show()

def test_anomaly_scenarios():
    voltage_value, frequency_value, load_value = get_user_input()

    # Set the inputs to the fuzzy logic controller
    severity_sim.input['VoltageDeviation'] = voltage_value
    severity_sim.input['FrequencyVariation'] = frequency_value
    severity_sim.input['LoadImbalance'] = load_value

    # Compute severity based on fuzzy logic
    severity_sim.compute()

    # Get severity score
    severity_score = severity_sim.output['Severity']
    print(f"Severity Score: {severity_score}")  # Log severity score for debugging

    # Plot current position on the graph
    plot_current_position(voltage_value, frequency_value, load_value)

    # Determine action based on severity
    if severity_score < 30:
        action = "No Action Required"
    elif 30 <= severity_score < 70:
        action = "Activate Load Balancing and Monitoring"
    else:
        action = "Immediate Isolation and Load Rerouting"

    print(f"Suggested Action: {action}")

# Run the test with user input
test_anomaly_scenarios()
