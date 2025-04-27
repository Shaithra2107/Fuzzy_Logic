function fuzzifyVoltage(voltage) {
    if (voltage <= 2) return "Very Low";
    else if (voltage <= 5) return "Low";
    else if (voltage <= 10) return "Medium";
    else if (voltage <= 15) return "High";
    else return "Very High";
}

function fuzzifyFrequency(frequency) {
    if (Math.abs(frequency - 50) <= 0.3) return "Stable";
    else if (Math.abs(frequency - 50) <= 1) return "Slightly Unstable";
    else return "Unstable";
}

function fuzzifyLoad(load) {
    if (load <= 5) return "Very Balanced";
    else if (load <= 10) return "Balanced";
    else if (load <= 20) return "Slightly Unbalanced";
    else return "Unbalanced";
}

function inferSeverity(voltage, frequency, load) {
    let v = fuzzifyVoltage(voltage);
    let f = fuzzifyFrequency(frequency);
    let l = fuzzifyLoad(load);

    if (v === "Very High" || (v === "High" && f === "Unstable")) {
        return {level: "Very High Severity", score: 90};
    } else if (v === "High" && (f === "Slightly Unstable" || l === "Unbalanced")) {
        return {level: "High Severity", score: 75};
    } else if (v === "Medium" && (f === "Unstable" || l === "Slightly Unbalanced")) {
        return {level: "Medium Severity", score: 60};
    } else if ((v === "Low" || v === "Very Low") && f === "Stable" && (l === "Balanced" || l === "Very Balanced")) {
        return {level: "Low Severity", score: 20};
    } else {
        return {level: "Moderate Severity", score: 40};
    }
}

function suggestAction(severity) {
    switch(severity) {
        case "Very High Severity":
            return "Immediate Isolation and Load Rerouting";
        case "High Severity":
            return "Activate Load Balancing and Alert Operator";
        case "Medium Severity":
            return "Power Factor Correction and Monitor";
        case "Moderate Severity":
            return "Continuous Monitoring";
        default:
            return "Normal Operation - No Action Needed";
    }
}

function detectAnomaly() {
    let voltage = parseFloat(document.getElementById("voltage").value);
    let frequency = parseFloat(document.getElementById("frequency").value);
    let load = parseFloat(document.getElementById("load").value);

    if (isNaN(voltage) || isNaN(frequency) || isNaN(load)) {
        document.getElementById("result").innerText = "Please enter valid numbers.";
        document.getElementById("severityScore").innerText = "";
        document.getElementById("suggestedAction").innerText = "";
        return;
    }

    let {level, score} = inferSeverity(voltage, frequency, load);
    let action = suggestAction(level);

    document.getElementById("result").innerHTML = `<b>Anomaly Detected:</b> ${level}`;
    document.getElementById("severityScore").innerHTML = `<b>Severity Score:</b> ${score}/100`;
    document.getElementById("suggestedAction").innerHTML = `<b>Suggested Action:</b> ${action}`;

    // Auto-select suggestion
    document.getElementById("actionSelect").value = action;
}

function confirmAction() {
    let selected = document.getElementById("actionSelect").value;
    document.getElementById("confirmation").innerHTML = `<b>Confirmed Action:</b> ${selected}`;
}
