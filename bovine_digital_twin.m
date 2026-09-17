%% PashuRakshak Bovine Digital Twin - Compartmental Disease Simulator
% Smart India Hackathon (SIH) - Govt. of Maharashtra
% Simulates 14-day physiological dynamics for cattle (Bos indicus / crossbreeds)
% Biomarkers: Temperature, Rumination, Feeding, Activity Index

clear; clc; close all;

fprintf('====================================================\n');
fprintf(' PashuRakshak (पशुरक्षक) - Bovine Digital Twin Simulator \n');
fprintf(' Govt. of Maharashtra Livestock Health Surveillance \n');
fprintf('====================================================\n\n');

%% 1. Simulation Parameters
days = 14;
hours = days * 24;
t_hours = 0:(hours - 1);
t_days = t_hours / 24;

onset_day = 7.0;            % Disease onset at Day 7
subclinical_days = 2.5;     % 60 hours of sub-clinical window
onset_hour = onset_day * 24;
clinical_hour = (onset_day + subclinical_days) * 24;

%% 2. Baselines (Healthy Gir / Crossbreed Cow)
base_temp = 38.5;       % deg C
base_rum = 460.0;       % min/day
base_feed = 260.0;      % min/day
base_act = 100.0;       % index

% Circadian diurnal oscillations (lowest 6 AM, peak 6 PM)
circadian_phase = 2 * pi * (mod(t_hours, 24) - 6) / 24;
circ_temp = 0.35 * sin(circadian_phase);
circ_rum  = 30.0 * cos(circadian_phase);
circ_feed = 20.0 * sin(circadian_phase);
circ_act  = 15.0 * sin(circadian_phase);

% Noise / sensor jitter
rng(2026);
noise_temp = 0.08 * randn(1, hours);
noise_rum  = 8.0  * randn(1, hours);
noise_feed = 6.0  * randn(1, hours);
noise_act  = 4.0  * randn(1, hours);

%% 3. Compartmental Disease Progression (Subclinical Mastitis Model)
disease_progress = zeros(1, hours);
for h = 1:hours
    hr_val = t_hours(h);
    if hr_val < onset_hour
        disease_progress(h) = 0.0;
    elseif hr_val < clinical_hour
        % Sub-clinical phase (cytokine release, silent rumination drop)
        disease_progress(h) = (hr_val - onset_hour) / (clinical_hour - onset_hour) * 0.5;
    else
        % Clinical acute phase
        post_hrs = hr_val - clinical_hour;
        disease_progress(h) = 0.5 + 0.5 * (1.0 - exp(-post_hrs / 48.0));
    end
end

% Pathophysiological deltas (Mastitis: cytokine pyrexia + rumination suppression)
delta_temp = disease_progress * 1.8;
delta_rum  = -disease_progress * 220.0;
delta_feed = -disease_progress * 90.0;
delta_act  = -disease_progress * 25.0;

% Total physiological biomarker series
temp = base_temp + circ_temp + delta_temp + noise_temp;
rum  = max(40.0, base_rum + circ_rum + delta_rum + noise_rum);
feed = max(20.0, base_feed + circ_feed + delta_feed + noise_feed);
act  = max(15.0, base_act + circ_act + delta_act + noise_act);

%% 4. Print Summary to MATLAB Console
fprintf('Animal ID:             MAH-PUN-TAG-1042 (Gir Cross)\n');
fprintf('Condition Simulated:   Subclinical to Clinical Mastitis (कासदाह)\n');
fprintf('Simulation Duration:   %d Days (%d Hours)\n', days, hours);
fprintf('Subclinical Window:    Day %.1f to Day %.1f (Early Warning Lead Time: %.1f hours)\n', ...
        onset_day, onset_day + subclinical_days, subclinical_days * 24);
fprintf('Baseline Temperature:  %.1f °C  --> Peak Fever: %.2f °C\n', base_temp, max(temp));
fprintf('Baseline Rumination:   %.0f min/day --> Nadir Rumination: %.0f min/day (-%.1f%%)\n\n', ...
        base_rum, min(rum), ((base_rum - min(rum)) / base_rum) * 100);

%% 5. Visualization
fig = figure('Name', 'PashuRakshak - Bovine Disease Progression Digital Twin', ...
             'Color', [0.1 0.12 0.15], 'Position', [100 100 1100 750]);

colors = struct('temp', [0.94 0.33 0.31], ...
                'rum',  [0.24 0.60 0.94], ...
                'feed', [0.20 0.80 0.55], ...
                'act',  [0.98 0.70 0.18], ...
                'sub',  [0.95 0.77 0.20 0.15], ...
                'clin', [0.90 0.22 0.21 0.15]);

% --- Subplot 1: Body Temperature ---
subplot(4,1,1); hold on; grid on;
fill([onset_day (onset_day+subclinical_days) (onset_day+subclinical_days) onset_day], ...
     [37.5 37.5 41.5 41.5], [1 0.85 0.4], 'FaceAlpha', 0.2, 'EdgeColor', 'none');
fill([(onset_day+subclinical_days) days days (onset_day+subclinical_days)], ...
     [37.5 37.5 41.5 41.5], [1 0.4 0.4], 'FaceAlpha', 0.2, 'EdgeColor', 'none');
plot(t_days, temp, 'Color', colors.temp, 'LineWidth', 1.8);
yline(39.2, '--r', 'Fever Threshold (39.2°C)', 'Color', [1 0.5 0.5]);
ylabel('Temp (°C)', 'Color', 'w', 'FontSize', 10);
title('PashuRakshak Digital Twin: 14-Day Multi-Biomarker Progression (Cattle ID: MAH-PUN-1042)', ...
      'Color', 'w', 'FontSize', 12, 'FontWeight', 'bold');
set(gca, 'Color', [0.15 0.17 0.22], 'XColor', 'w', 'YColor', 'w', 'GridColor', [0.3 0.3 0.35]);
xlim([0 days]); ylim([37.8 41.2]);

% --- Subplot 2: Rumination Time ---
subplot(4,1,2); hold on; grid on;
fill([onset_day (onset_day+subclinical_days) (onset_day+subclinical_days) onset_day], ...
     [100 100 600 600], [1 0.85 0.4], 'FaceAlpha', 0.2, 'EdgeColor', 'none');
fill([(onset_day+subclinical_days) days days (onset_day+subclinical_days)], ...
     [100 100 600 600], [1 0.4 0.4], 'FaceAlpha', 0.2, 'EdgeColor', 'none');
plot(t_days, rum, 'Color', colors.rum, 'LineWidth', 1.8);
yline(350, '--y', 'Pre-Clinical Drop Threshold (-30%)', 'Color', [1 0.9 0.4]);
ylabel('Rumination (min)', 'Color', 'w', 'FontSize', 10);
set(gca, 'Color', [0.15 0.17 0.22], 'XColor', 'w', 'YColor', 'w', 'GridColor', [0.3 0.3 0.35]);
xlim([0 days]); ylim([180 560]);

% --- Subplot 3: Feeding Time ---
subplot(4,1,3); hold on; grid on;
fill([onset_day (onset_day+subclinical_days) (onset_day+subclinical_days) onset_day], ...
     [50 50 350 350], [1 0.85 0.4], 'FaceAlpha', 0.2, 'EdgeColor', 'none');
fill([(onset_day+subclinical_days) days days (onset_day+subclinical_days)], ...
     [50 50 350 350], [1 0.4 0.4], 'FaceAlpha', 0.2, 'EdgeColor', 'none');
plot(t_days, feed, 'Color', colors.feed, 'LineWidth', 1.8);
ylabel('Feeding (min)', 'Color', 'w', 'FontSize', 10);
set(gca, 'Color', [0.15 0.17 0.22], 'XColor', 'w', 'YColor', 'w', 'GridColor', [0.3 0.3 0.35]);
xlim([0 days]); ylim([80 320]);

% --- Subplot 4: Activity Index ---
subplot(4,1,4); hold on; grid on;
fill([onset_day (onset_day+subclinical_days) (onset_day+subclinical_days) onset_day], ...
     [20 20 150 150], [1 0.85 0.4], 'FaceAlpha', 0.2, 'EdgeColor', 'none');
fill([(onset_day+subclinical_days) days days (onset_day+subclinical_days)], ...
     [20 20 150 150], [1 0.4 0.4], 'FaceAlpha', 0.2, 'EdgeColor', 'none');
plot(t_days, act, 'Color', colors.act, 'LineWidth', 1.8);
xlabel('Timeline (Days)  [Gold = Subclinical Window (Early Warning 60h) | Red = Clinical Clots]', ...
       'Color', [1 0.85 0.4], 'FontSize', 11, 'FontWeight', 'bold');
ylabel('Activity Index', 'Color', 'w', 'FontSize', 10);
set(gca, 'Color', [0.15 0.17 0.22], 'XColor', 'w', 'YColor', 'w', 'GridColor', [0.3 0.3 0.35]);
xlim([0 days]); ylim([40 140]);

fprintf('>> Simulation complete. Figure window opened.\n');
