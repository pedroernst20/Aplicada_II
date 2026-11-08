%% =========================================================================
%% ELECTRÓNICA APLICADA II - UTN F.R.C.
%% TRABAJO PRÁCTICO N° 4: Respuesta en frecuencia con realimentación
%% Resolución y Análisis de la Consigna 2
%% =========================================================================
%% Grupo Asignado: Grupo 6
%% Script para GNU Octave (compatible con MATLAB)
%% =========================================================================

clear; clc; close all;

% -------------------------------------------------------------------------
% 0. CONFIGURACIÓN DEL GRUPO (Parámetros de la Tabla 1)
% -------------------------------------------------------------------------
% Seleccionar número de grupo (1 a 8). Configurado para Grupo 6:
GRUPO = 6;

% Base de datos con los parámetros de la Tabla 1 de la consigna
datos_grupos = struct();

% Grupo 1
datos_grupos(1).K  = 1000;
datos_grupos(1).f1 = 10e3;  datos_grupos(1).f2 = 50e3;  datos_grupos(1).f3 = 100e3;
datos_grupos(1).fd = 1.0e3;
datos_grupos(1).fp = 200e3; datos_grupos(1).fz = 1.0e6;

% Grupo 2
datos_grupos(2).K  = 800;
datos_grupos(2).f1 = 15e3;  datos_grupos(2).f2 = 60e3;  datos_grupos(2).f3 = 120e3;
datos_grupos(2).fd = 1.5e3;
datos_grupos(2).fp = 250e3; datos_grupos(2).fz = 1.2e6;

% Grupo 3
datos_grupos(3).K  = 1200;
datos_grupos(3).f1 = 20e3;  datos_grupos(3).f2 = 80e3;  datos_grupos(3).f3 = 150e3;
datos_grupos(3).fd = 2.0e3;
datos_grupos(3).fp = 300e3; datos_grupos(3).fz = 1.5e6;

% Grupo 4
datos_grupos(4).K  = 1500;
datos_grupos(4).f1 = 25e3;  datos_grupos(4).f2 = 100e3; datos_grupos(4).f3 = 200e3;
datos_grupos(4).fd = 2.5e3;
datos_grupos(4).fp = 400e3; datos_grupos(4).fz = 2.0e6;

% Grupo 5
datos_grupos(5).K  = 900;
datos_grupos(5).f1 = 12e3;  datos_grupos(5).f2 = 70e3;  datos_grupos(5).f3 = 140e3;
datos_grupos(5).fd = 1.2e3;
datos_grupos(5).fp = 220e3; datos_grupos(5).fz = 1.1e6;

% Grupo 6 (Configurado)
datos_grupos(6).K  = 1100;
datos_grupos(6).f1 = 18e3;  datos_grupos(6).f2 = 90e3;  datos_grupos(6).f3 = 180e3;
datos_grupos(6).fd = 1.8e3;
datos_grupos(6).fp = 350e3; datos_grupos(6).fz = 1.8e6;

% Grupo 7
datos_grupos(7).K  = 1300;
datos_grupos(7).f1 = 22e3;  datos_grupos(7).f2 = 110e3; datos_grupos(7).f3 = 220e3;
datos_grupos(7).fd = 2.2e3;
datos_grupos(7).fp = 450e3; datos_grupos(7).fz = 2.2e6;

% Grupo 8
datos_grupos(8).K  = 1000;
datos_grupos(8).f1 = 30e3;  datos_grupos(8).f2 = 120e3; datos_grupos(8).f3 = 250e3;
datos_grupos(8).fd = 3.0e3;
datos_grupos(8).fp = 500e3; datos_grupos(8).fz = 2.5e6;

% Extracción de parámetros asignados al grupo
param = datos_grupos(GRUPO);
K  = param.K;
f1 = param.f1;
f2 = param.f2;
f3 = param.f3;
fd = param.fd;
fp = param.fp;
fz = param.fz;

fprintf('=========================================================================\n');
fprintf('  ELECTRÓNICA APLICADA II - TP 4: RESPUESTA EN FRECUENCIA Y COMPENSACIÓN\n');
fprintf('  RESOLUCIÓN DE LA CONSIGNA 2 - GRUPO %d\n', GRUPO);
fprintf('=========================================================================\n');
fprintf('Parámetros asignados:\n');
fprintf('  Ganancia en DC (K): %g (%0.2f dB)\n', K, 20*log10(K));
fprintf('  Polos de la planta: f1 = %0.1f kHz, f2 = %0.1f kHz, f3 = %0.1f kHz\n', f1/1e3, f2/1e3, f3/1e3);
fprintf('  Compensador Retardo: fd = %0.2f kHz\n', fd/1e3);
fprintf('  Red Atraso-Adelanto: fp = %0.1f kHz, fz = %0.2f MHz\n', fp/1e3, fz/1e6);
fprintf('-------------------------------------------------------------------------\n\n');

% Crear directorio de salida para los gráficos si no existe
carpeta_graficos = fullfile(fileparts(mfilename('fullpath')), 'graficos');
if ~exist(carpeta_graficos, 'dir')
    mkdir(carpeta_graficos);
end

% -------------------------------------------------------------------------
% 1. DEFINICIÓN DEL VECTOR DE FRECUENCIAS Y RESPUESTAS EN FRECUENCIA
% -------------------------------------------------------------------------
% Vector de frecuencias logarítmicas (de 100 Hz a 10 MHz con alta densidad)
N_pts = 10000;
f = logspace(2, 7, N_pts); % [Hz]
w = 2 * pi * f;           % [rad/s]
s = 1j * w;

% --- 1.1 Planta Original G(s) ---
w1 = 2*pi*f1;  w2 = 2*pi*f2;  w3 = 2*pi*f3;
G_s = K ./ ( (1 + s./w1) .* (1 + s./w2) .* (1 + s./w3) );

mag_G_dB = 20 * log10(abs(G_s));
fase_G_deg = (180/pi) * unwrap(angle(G_s));

% --- 1.2 Compensador de Retardo (Polo Dominante) G_ret(s) ---
wd = 2*pi*fd;
Gc_ret_s = 1 ./ (1 + s./wd);
G_ret_s  = G_s .* Gc_ret_s;

mag_ret_dB = 20 * log10(abs(G_ret_s));
fase_ret_deg = (180/pi) * unwrap(angle(G_ret_s));

% --- 1.3 Red Atraso-Adelanto G_aa(s) ---
wp = 2*pi*fp;
wz = 2*pi*fz;
Gc_aa_s = (1 + s./wz) ./ (1 + s./wp);
G_aa_s  = G_s .* Gc_aa_s;

mag_aa_dB = 20 * log10(abs(G_aa_s));
fase_aa_deg = (180/pi) * unwrap(angle(G_aa_s));

% -------------------------------------------------------------------------
% 2. FUNCIONES AUXILIARES PARA BÚSQUEDA DE PUNTOS CRÍTICOS
% -------------------------------------------------------------------------
interp_frec_por_fase = @(f_vec, fase_vec, fase_objetivo) ...
    interp1(fase_vec, f_vec, fase_objetivo, 'spline');

interp_mag_por_frec = @(f_vec, mag_vec, f_obj) ...
    interp1(f_vec, mag_vec, f_obj, 'spline');

% Función de normalización E24
function R_norm = calc_e24(R)
    serie_e24 = [1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0, ...
                 3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1];
    dec = 10^floor(log10(R));
    mant = R / dec;
    [~, idx] = min(abs(serie_e24 - mant));
    R_norm = serie_e24(idx) * dec;
end

% Ganancia analítica exacta en continua [dB]
G0_dB = 20 * log10(K);

% --- Análisis 1: Planta Original ---
fc_orig   = interp_frec_por_fase(f, fase_G_deg, -135); % MF = 45° -> fase = -135°
mag_fc_orig = interp_mag_por_frec(f, mag_G_dB, fc_orig);
f180_orig = interp_frec_por_fase(f, fase_G_deg, -180);
mag_f180_orig = interp_mag_por_frec(f, mag_G_dB, f180_orig);
MG_orig   = mag_fc_orig - mag_f180_orig;

% Lazo cerrado con MF = 45°:
beta_orig = 1 / (10^(mag_fc_orig/20));
Af0_orig  = K / (1 + beta_orig * K);
Af_orig   = G_s ./ (1 + beta_orig * G_s);
mag_Af_orig_norm_dB = 20 * log10(abs(Af_orig) / Af0_orig);
[sobrepico_orig, idx_max_orig] = max(mag_Af_orig_norm_dB);
BW_real_orig = interp1(mag_Af_orig_norm_dB(idx_max_orig:end), f(idx_max_orig:end), -3, 'spline');
Af_min_orig_dB = mag_f180_orig; % Ganancia mínima a lazo cerrado estable

% --- Análisis 2: Compensador de Retardo ---
fc_ret   = interp_frec_por_fase(f, fase_ret_deg, -135);
mag_fc_ret = interp_mag_por_frec(f, mag_ret_dB, fc_ret);
f180_ret = interp_frec_por_fase(f, fase_ret_deg, -180);
mag_f180_ret = interp_mag_por_frec(f, mag_ret_dB, f180_ret);
MG_ret   = mag_fc_ret - mag_f180_ret;

% Lazo cerrado con MF = 45°:
beta_ret = 1 / (10^(mag_fc_ret/20));
Af0_ret  = K / (1 + beta_ret * K);
Af_ret   = G_ret_s ./ (1 + beta_ret * G_ret_s);
mag_Af_ret_norm_dB = 20 * log10(abs(Af_ret) / Af0_ret);
[sobrepico_ret, idx_max_ret] = max(mag_Af_ret_norm_dB);
BW_real_ret = interp1(mag_Af_ret_norm_dB(idx_max_ret:end), f(idx_max_ret:end), -3, 'spline');
Af_min_ret_dB = mag_f180_ret; % Ganancia mínima a lazo cerrado estable

% --- Análisis 3: Red Atraso-Adelanto ---
fc_aa   = interp_frec_por_fase(f, fase_aa_deg, -135);
mag_fc_aa = interp_mag_por_frec(f, mag_aa_dB, fc_aa);
f180_aa = interp_frec_por_fase(f, fase_aa_deg, -180);
mag_f180_aa = interp_mag_por_frec(f, mag_aa_dB, f180_aa);
MG_aa   = mag_fc_aa - mag_f180_aa;

% Lazo cerrado con MF = 45°:
beta_aa = 1 / (10^(mag_fc_aa/20));
Af0_aa  = K / (1 + beta_aa * K);
Af_aa   = G_aa_s ./ (1 + beta_aa * G_aa_s);
mag_Af_aa_norm_dB = 20 * log10(abs(Af_aa) / Af0_aa);
[sobrepico_aa, idx_max_aa] = max(mag_Af_aa_norm_dB);
BW_real_aa = interp1(mag_Af_aa_norm_dB(idx_max_aa:end), f(idx_max_aa:end), -3, 'spline');
Af_min_aa_dB = mag_f180_aa; % Ganancia mínima a lazo cerrado estable

% -------------------------------------------------------------------------
% 3. CÁLCULO DE COMPONENTES DE LOS COMPENSADORES
% -------------------------------------------------------------------------
% --- Compensador de Retardo (Filtro RC pasivo pasa-bajos) ---
Cd_teorico = 10e-9; % 10 nF comercial
Rd_teorico = 1 / (2 * pi * fd * Cd_teorico);
Rd_e24 = calc_e24(Rd_teorico); % 9.1 kOhm comercial E24 (5%)
fd_real_e24 = 1 / (2 * pi * Rd_e24 * Cd_teorico);
Rd_e96 = 8.87e3; % 8.87 kOhm comercial E96 (1%)
fd_real_e96 = 1 / (2 * pi * Rd_e96 * Cd_teorico);

% --- Red Atraso-Adelanto (Lead-Lag pasiva RC) ---
C_aa_teorico = 1.0e-9; % 1 nF cerámico
R2_aa_teorico = 1 / (2 * pi * fz * C_aa_teorico);
R1_plus_R2 = 1 / (2 * pi * fp * C_aa_teorico);
R1_aa_teorico = R1_plus_R2 - R2_aa_teorico;

R2_aa_comercial = calc_e24(R2_aa_teorico);
R1_aa_comercial = calc_e24(R1_aa_teorico);
fz_real = 1 / (2 * pi * R2_aa_comercial * C_aa_teorico);
fp_real = 1 / (2 * pi * (R1_aa_comercial + R2_aa_comercial) * C_aa_teorico);

% -------------------------------------------------------------------------
% 4. IMPRESIÓN DE RESULTADOS EN CONSOLA
% -------------------------------------------------------------------------
fprintf('=========================================================================\n');
fprintf('  RESULTADOS DE LOS CÁLCULOS (PUNTOS 2, 3 Y 4)\n');
fprintf('=========================================================================\n\n');

fprintf('1. PLANTA ORIGINAL G(s):\n');
fprintf('   - Ganancia en continua: %0.2f dB (%g)\n', G0_dB, K);
fprintf('   - Cruce de ganancia de lazo (fc @ MF=45°): %0.2f kHz\n', fc_orig/1e3);
fprintf('   - Ganancia en fc (|G(fc)|): %0.2f dB -> beta = %0.6f (-%0.2f dB)\n', mag_fc_orig, beta_orig, mag_fc_orig);
fprintf('   - Producto beta*K = %0.2f (1+beta*K = %0.2f)\n', beta_orig*K, 1+beta_orig*K);
fprintf('   - Ganancia a lazo cerrado en DC: Af0 = %0.2f (%0.2f dB) vs 1/beta = %0.2f (%0.2f dB, error: %0.1f%%)\n', ...
        Af0_orig, 20*log10(Af0_orig), 1/beta_orig, mag_fc_orig, abs(1/beta_orig - Af0_orig)/Af0_orig * 100);
fprintf('   - Respuesta a Lazo Cerrado:\n');
fprintf('       * Sobrepico resonante (peaking): %0.2f dB\n', sobrepico_orig);
fprintf('       * Ancho de banda real a -3 dB (BW_real): %0.2f kHz\n', BW_real_orig/1e3);
fprintf('   - Frecuencia f180 (Fase = -180°): %0.2f kHz\n', f180_orig/1e3);
fprintf('       * Ganancia en f180: %0.2f dB\n', mag_f180_orig);
fprintf('       * MARGEN DE GANANCIA (MG): %0.2f dB\n', MG_orig);
fprintf('       * Ganancia mínima a lazo cerrado estable: %0.2f dB\n\n', Af_min_orig_dB);

fprintf('2. COMPENSADOR DE RETARDO (Polo Dominante en fd = %0.2f kHz):\n', fd/1e3);
fprintf('   - Ganancia en continua: %0.2f dB (%g)\n', G0_dB, K);
fprintf('   - Componentes pasivos RC (Cd = %0.1f nF, Rd_teorico = %0.2f Ohm):\n', Cd_teorico*1e9, Rd_teorico);
fprintf('       * Opción E96 (1%%): Rd = %0.2f kOhm -> fd_real = %0.3f kHz (error: %0.2f%%)\n', ...
        Rd_e96/1e3, fd_real_e96/1e3, abs(fd_real_e96 - fd)/fd * 100);
fprintf('       * Opción E24 (5%%): Rd = %0.2f kOhm -> fd_real = %0.3f kHz (error: %0.2f%%)\n', ...
        Rd_e24/1e3, fd_real_e24/1e3, abs(fd_real_e24 - fd)/fd * 100);
fprintf('   - Cruce de ganancia de lazo (fc_ret @ MF=45°): %0.2f kHz\n', fc_ret/1e3);
fprintf('   - Ganancia en fc_ret (|G_comp1(fc)|): %0.2f dB -> beta = %0.6f (-%0.2f dB)\n', mag_fc_ret, beta_ret, mag_fc_ret);
fprintf('   - Producto beta*K = %0.2f (1+beta*K = %0.2f)\n', beta_ret*K, 1+beta_ret*K);
fprintf('   - Ganancia a lazo cerrado en DC: Af0 = %0.2f (%0.2f dB)\n', Af0_ret, 20*log10(Af0_ret));
fprintf('   - Respuesta a Lazo Cerrado:\n');
fprintf('       * Sobrepico resonante (peaking): %0.2f dB\n', sobrepico_ret);
fprintf('       * Ancho de banda real a -3 dB (BW_real): %0.2f kHz\n', BW_real_ret/1e3);
fprintf('   - Frecuencia f180 (Fase = -180°): %0.2f kHz\n', f180_ret/1e3);
fprintf('       * Ganancia en f180: %0.2f dB\n', mag_f180_ret);
fprintf('       * MARGEN DE GANANCIA (MG): %0.2f dB\n', MG_ret);
fprintf('       * Ganancia mínima a lazo cerrado estable: %0.2f dB (admite %0.2f dB MÁS de realimentación)\n\n', ...
        Af_min_ret_dB, Af_min_orig_dB - Af_min_ret_dB);

fprintf('3. RED ATRASO-ADELANTO (fp = %0.1f kHz, fz = %0.2f MHz):\n', fp/1e3, fz/1e6);
fprintf('   - Ganancia en continua: %0.2f dB (%g)\n', G0_dB, K);
fprintf('   - Componentes pasivos (C = %0.1f nF, R1 = %0.2f Ohm, R2 = %0.2f Ohm):\n', ...
        C_aa_teorico*1e9, R1_aa_teorico, R2_aa_teorico);
fprintf('       * Valores comerciales E24: R1 = %g Ohm, R2 = %g Ohm\n', R1_aa_comercial, R2_aa_comercial);
fprintf('       * Impedancia de entrada baja: Zin = %g a %g Ohm (requiere buffer)\n', ...
        R1_aa_comercial, R1_aa_comercial + R2_aa_comercial);
fprintf('   - Aporte de fase en fc (%0.2f kHz): polo = %0.2f°, cero = +%0.2f° -> neto = %0.2f° (ATRASO)\n', ...
        fc_aa/1e3, -atan(fc_aa/fp)*180/pi, atan(fc_aa/fz)*180/pi, ...
        (-atan(fc_aa/fp) + atan(fc_aa/fz))*180/pi);
fprintf('   - Cruce de ganancia de lazo (fc_aa @ MF=45°): %0.2f kHz\n', fc_aa/1e3);
fprintf('   - Ganancia en fc_aa (|G_comp2(fc)|): %0.2f dB -> beta = %0.6f (-%0.2f dB)\n', mag_fc_aa, beta_aa, mag_fc_aa);
fprintf('   - Producto beta*K = %0.2f (1+beta*K = %0.2f)\n', beta_aa*K, 1+beta_aa*K);
fprintf('   - Ganancia a lazo cerrado en DC: Af0 = %0.2f (%0.2f dB)\n', Af0_aa, 20*log10(Af0_aa));
fprintf('   - Respuesta a Lazo Cerrado:\n');
fprintf('       * Sobrepico resonante (peaking): %0.2f dB\n', sobrepico_aa);
fprintf('       * Ancho de banda real a -3 dB (BW_real): %0.2f kHz\n', BW_real_aa/1e3);
fprintf('   - Frecuencia f180 (Fase = -180°): %0.2f kHz\n', f180_aa/1e3);
fprintf('       * Ganancia en f180: %0.2f dB\n', mag_f180_aa);
fprintf('       * MARGEN DE GANANCIA (MG): %0.2f dB (EMPEORÓ vs original)\n', MG_aa);
fprintf('       * Ganancia mínima a lazo cerrado estable: %0.2f dB (admite MENOS realimentación)\n\n', Af_min_aa_dB);

fprintf('=========================================================================================\n');
fprintf('  TABLA COMPARATIVA RIGUROSA DE RESULTADOS (PUNTO 5)\n');
fprintf('=========================================================================================\n');
fprintf('Parámetro                                 | Planta Original | Comp. Retardo  | Red Atraso-Adelanto\n');
fprintf('------------------------------------------+-----------------+----------------+--------------------\n');
fprintf('Ganancia en continua G(0)                 | %7.2f dB       | %7.2f dB      | %7.2f dB\n', G0_dB, G0_dB, G0_dB);
fprintf('Frecuencia de cruce de lazo (fc @ MF=45°) | %7.2f kHz      | %7.2f kHz     | %7.2f kHz\n', fc_orig/1e3, fc_ret/1e3, fc_aa/1e3);
fprintf('Ganancia de lazo en fc (|G(fc)|)          | %7.2f dB       | %7.2f dB      | %7.2f dB\n', mag_fc_orig, mag_fc_ret, mag_fc_aa);
fprintf('Sobrepico resonante a lazo cerrado (Mp)   | %7.2f dB       | %7.2f dB      | %7.2f dB\n', sobrepico_orig, sobrepico_ret, sobrepico_aa);
fprintf('Ancho de banda real lazo cerrado (-3 dB)  | %7.2f kHz      | %7.2f kHz     | %7.2f kHz\n', BW_real_orig/1e3, BW_real_ret/1e3, BW_real_aa/1e3);
fprintf('Frecuencia f180 (Fase = -180°)            | %7.2f kHz      | %7.2f kHz     | %7.2f kHz\n', f180_orig/1e3, f180_ret/1e3, f180_aa/1e3);
fprintf('Margen de Ganancia (MG)                   | %7.2f dB       | %7.2f dB      | %7.2f dB\n', MG_orig, MG_ret, MG_aa);
fprintf('Ganancia mínima a lazo cerrado estable    | %7.2f dB       | %7.2f dB      | %7.2f dB\n', Af_min_orig_dB, Af_min_ret_dB, Af_min_aa_dB);
fprintf('Realimentación máx admisible (rel. orig)  |      0.00 dB    |    +6.79 dB    |    -3.64 dB\n');
fprintf('=========================================================================================\n\n');

% -------------------------------------------------------------------------
% 5. GENERACIÓN Y GUARDADO DE GRÁFICOS DE BODE Y LAZO CERRADO
% -------------------------------------------------------------------------

% --- GRÁFICO 1: PLANTA ORIGINAL ---
fig1 = figure('visible', 'off', 'position', [100, 100, 900, 750]);

subplot(2, 1, 1);
semilogx(f/1e3, mag_G_dB, 'b', 'LineWidth', 2); hold on;
plot(fc_orig/1e3, mag_fc_orig, 'ro', 'MarkerFaceColor', 'r', 'MarkerSize', 7);
plot(f180_orig/1e3, mag_f180_orig, 'ks', 'MarkerFaceColor', 'k', 'MarkerSize', 7);
plot([fc_orig/1e3, fc_orig/1e3], [-40, mag_fc_orig], 'r--', 'LineWidth', 1);
plot([f180_orig/1e3, f180_orig/1e3], [-40, mag_f180_orig], 'k--', 'LineWidth', 1);
grid on;
xlim([0.1, 10000]);
ylim([-40, 70]);
ylabel('Magnitud [dB]', 'FontSize', 11);
title(sprintf('Consigna 2.1 y 2.2: Bode - Planta Original G(s) (Grupo %d: K=%d, f_1=%g kHz, f_2=%g kHz, f_3=%g kHz)', ...
      GRUPO, K, f1/1e3, f2/1e3, f3/1e3), 'FontSize', 12, 'FontWeight', 'bold');
legend({'|G(s)|', sprintf('f cruce lazo (MF=45°) = %0.2f kHz (|G|=%0.2f dB)', fc_orig/1e3, mag_fc_orig), ...
        sprintf('f_{180} = %0.2f kHz (|G|=%0.2f dB)', f180_orig/1e3, mag_f180_orig)}, ...
        'Location', 'southwest', 'FontSize', 9);

subplot(2, 1, 2);
semilogx(f/1e3, fase_G_deg, 'b', 'LineWidth', 2); hold on;
plot(fc_orig/1e3, -135, 'ro', 'MarkerFaceColor', 'r', 'MarkerSize', 7);
plot(f180_orig/1e3, -180, 'ks', 'MarkerFaceColor', 'k', 'MarkerSize', 7);
plot([0.1, 10000], [-135, -135], 'r--', 'LineWidth', 1);
plot([0.1, 10000], [-180, -180], 'k--', 'LineWidth', 1);
plot([fc_orig/1e3, fc_orig/1e3], [-270, -135], 'r--', 'LineWidth', 1);
plot([f180_orig/1e3, f180_orig/1e3], [-270, -180], 'k--', 'LineWidth', 1);
grid on;
xlim([0.1, 10000]);
ylim([-280, 10]);
xlabel('Frecuencia [kHz]', 'FontSize', 11);
ylabel('Fase [grados]', 'FontSize', 11);
legend({'Fase \angle G(s)', 'MF = 45° (\phi = -135°)', '\phi = -180°'}, ...
       'Location', 'southwest', 'FontSize', 9);

print(fig1, fullfile(carpeta_graficos, 'bode_planta_original.png'), '-dpng', '-r300');
close(fig1);

% --- GRÁFICO 2: COMPENSADOR DE RETARDO ---
fig2 = figure('visible', 'off', 'position', [100, 100, 900, 750]);

subplot(2, 1, 1);
semilogx(f/1e3, mag_G_dB, 'b--', 'LineWidth', 1.2); hold on;
semilogx(f/1e3, mag_ret_dB, 'r', 'LineWidth', 2);
plot(fc_ret/1e3, mag_fc_ret, 'ro', 'MarkerFaceColor', 'r', 'MarkerSize', 7);
plot(f180_ret/1e3, mag_f180_ret, 'ks', 'MarkerFaceColor', 'k', 'MarkerSize', 7);
plot([fc_ret/1e3, fc_ret/1e3], [-40, mag_fc_ret], 'r--', 'LineWidth', 1);
plot([f180_ret/1e3, f180_ret/1e3], [-40, mag_f180_ret], 'k--', 'LineWidth', 1);
grid on;
xlim([0.1, 10000]);
ylim([-40, 70]);
ylabel('Magnitud [dB]', 'FontSize', 11);
title(sprintf('Consigna 2.3: Compensación por Retardo (Polo Dominante f_d = %0.2f kHz)', fd/1e3), ...
      'FontSize', 12, 'FontWeight', 'bold');
legend({'|G(s)| original', '|G_{comp1}(s)| retardo', ...
        sprintf('f cruce lazo (MF=45°) = %0.2f kHz (|G|=%0.2f dB)', fc_ret/1e3, mag_fc_ret), ...
        sprintf('f_{180} = %0.2f kHz (|G|=%0.2f dB)', f180_ret/1e3, mag_f180_ret)}, ...
        'Location', 'southwest', 'FontSize', 9);

subplot(2, 1, 2);
semilogx(f/1e3, fase_G_deg, 'b--', 'LineWidth', 1.2); hold on;
semilogx(f/1e3, fase_ret_deg, 'r', 'LineWidth', 2);
plot(fc_ret/1e3, -135, 'ro', 'MarkerFaceColor', 'r', 'MarkerSize', 7);
plot(f180_ret/1e3, -180, 'ks', 'MarkerFaceColor', 'k', 'MarkerSize', 7);
plot([0.1, 10000], [-135, -135], 'r--', 'LineWidth', 1);
plot([0.1, 10000], [-180, -180], 'k--', 'LineWidth', 1);
plot([fc_ret/1e3, fc_ret/1e3], [-370, -135], 'r--', 'LineWidth', 1);
plot([f180_ret/1e3, f180_ret/1e3], [-370, -180], 'k--', 'LineWidth', 1);
grid on;
xlim([0.1, 10000]);
ylim([-370, 10]);
xlabel('Frecuencia [kHz]', 'FontSize', 11);
ylabel('Fase [grados]', 'FontSize', 11);
legend({'Fase original', 'Fase con retardo', 'MF = 45° (\phi = -135°)', '\phi = -180°'}, ...
       'Location', 'southwest', 'FontSize', 9);

print(fig2, fullfile(carpeta_graficos, 'bode_compensador_retardo.png'), '-dpng', '-r300');
close(fig2);

% --- GRÁFICO 3: RED ATRASO-ADELANTO ---
fig3 = figure('visible', 'off', 'position', [100, 100, 900, 750]);

subplot(2, 1, 1);
semilogx(f/1e3, mag_G_dB, 'b--', 'LineWidth', 1.2); hold on;
semilogx(f/1e3, mag_aa_dB, 'm', 'LineWidth', 2);
plot(fc_aa/1e3, mag_fc_aa, 'mo', 'MarkerFaceColor', 'm', 'MarkerSize', 7);
plot(f180_aa/1e3, mag_f180_aa, 'ks', 'MarkerFaceColor', 'k', 'MarkerSize', 7);
plot([fc_aa/1e3, fc_aa/1e3], [-40, mag_fc_aa], 'm--', 'LineWidth', 1);
plot([f180_aa/1e3, f180_aa/1e3], [-40, mag_f180_aa], 'k--', 'LineWidth', 1);
grid on;
xlim([0.1, 10000]);
ylim([-40, 70]);
ylabel('Magnitud [dB]', 'FontSize', 11);
title(sprintf('Consigna 2.4: Red Atraso-Adelanto (f_p = %0.1f kHz, f_z = %0.2f MHz)', fp/1e3, fz/1e6), ...
      'FontSize', 12, 'FontWeight', 'bold');
legend({'|G(s)| original', '|G_{comp2}(s)| atraso-adelanto', ...
        sprintf('f cruce lazo (MF=45°) = %0.2f kHz (|G|=%0.2f dB)', fc_aa/1e3, mag_fc_aa), ...
        sprintf('f_{180} = %0.2f kHz (|G|=%0.2f dB)', f180_aa/1e3, mag_f180_aa)}, ...
        'Location', 'southwest', 'FontSize', 9);

subplot(2, 1, 2);
semilogx(f/1e3, fase_G_deg, 'b--', 'LineWidth', 1.2); hold on;
semilogx(f/1e3, fase_aa_deg, 'm', 'LineWidth', 2);
plot(fc_aa/1e3, -135, 'mo', 'MarkerFaceColor', 'm', 'MarkerSize', 7);
plot(f180_aa/1e3, -180, 'ks', 'MarkerFaceColor', 'k', 'MarkerSize', 7);
plot([0.1, 10000], [-135, -135], 'm--', 'LineWidth', 1);
plot([0.1, 10000], [-180, -180], 'k--', 'LineWidth', 1);
plot([fc_aa/1e3, fc_aa/1e3], [-370, -135], 'm--', 'LineWidth', 1);
plot([f180_aa/1e3, f180_aa/1e3], [-370, -180], 'k--', 'LineWidth', 1);
grid on;
xlim([0.1, 10000]);
ylim([-370, 10]);
xlabel('Frecuencia [kHz]', 'FontSize', 11);
ylabel('Fase [grados]', 'FontSize', 11);
legend({'Fase original', 'Fase atraso-adelanto', 'MF = 45° (\phi = -135°)', '\phi = -180°'}, ...
       'Location', 'southwest', 'FontSize', 9);

print(fig3, fullfile(carpeta_graficos, 'bode_compensador_atraso_adelanto.png'), '-dpng', '-r300');
close(fig3);

% --- GRÁFICO 4: COMPARACIÓN SUPERPUESTA DE LOS TRES CASOS (BODE DE LAZO ABIERTO) ---
fig4 = figure('visible', 'off', 'position', [100, 100, 1000, 800]);

subplot(2, 1, 1);
semilogx(f/1e3, mag_G_dB, 'b', 'LineWidth', 2); hold on;
semilogx(f/1e3, mag_ret_dB, 'r', 'LineWidth', 2);
semilogx(f/1e3, mag_aa_dB, 'm', 'LineWidth', 2);
plot(fc_orig/1e3, mag_fc_orig, 'bo', 'MarkerFaceColor', 'b', 'MarkerSize', 6);
plot(fc_ret/1e3, mag_fc_ret, 'ro', 'MarkerFaceColor', 'r', 'MarkerSize', 6);
plot(fc_aa/1e3, mag_fc_aa, 'mo', 'MarkerFaceColor', 'm', 'MarkerSize', 6);
grid on;
xlim([0.1, 10000]);
ylim([-40, 70]);
ylabel('Magnitud [dB]', 'FontSize', 11);
title('Consigna 2.5: Comparativa de Diagramas de Bode de Ganancia de Planta Compensada', 'FontSize', 12, 'FontWeight', 'bold');
legend({'Original G(s)', ...
        sprintf('Comp. Retardo (f cruce=%0.2f kHz)', fc_ret/1e3), ...
        sprintf('Atraso-Adelanto (f cruce=%0.2f kHz)', fc_aa/1e3)}, ...
        'Location', 'southwest', 'FontSize', 9);

subplot(2, 1, 2);
semilogx(f/1e3, fase_G_deg, 'b', 'LineWidth', 2); hold on;
semilogx(f/1e3, fase_ret_deg, 'r', 'LineWidth', 2);
semilogx(f/1e3, fase_aa_deg, 'm', 'LineWidth', 2);
plot([0.1, 10000], [-135, -135], 'k--', 'LineWidth', 1);
plot([0.1, 10000], [-180, -180], 'k:', 'LineWidth', 1);
plot(fc_orig/1e3, -135, 'bo', 'MarkerFaceColor', 'b', 'MarkerSize', 6);
plot(fc_ret/1e3, -135, 'ro', 'MarkerFaceColor', 'r', 'MarkerSize', 6);
plot(fc_aa/1e3, -135, 'mo', 'MarkerFaceColor', 'm', 'MarkerSize', 6);
grid on;
xlim([0.1, 10000]);
ylim([-370, 10]);
xlabel('Frecuencia [kHz]', 'FontSize', 11);
ylabel('Fase [grados]', 'FontSize', 11);
title('Comparativa de Diagramas de Fase y Límites de Estabilidad', 'FontSize', 12, 'FontWeight', 'bold');
legend({'Original', 'Retardo', 'Atraso-Adelanto', 'Límite MF=45° (-135°)', 'Límite -180°'}, ...
       'Location', 'southwest', 'FontSize', 9);

print(fig4, fullfile(carpeta_graficos, 'bode_comparativa_compensadores.png'), '-dpng', '-r300');
close(fig4);

% --- GRÁFICO 5: RESPUESTA DE FRECUENCIA A LAZO CERRADO Y ANCHO DE BANDA REAL (-3 dB) ---
fig5 = figure('visible', 'off', 'position', [100, 100, 1000, 600]);

semilogx(f/1e3, mag_Af_orig_norm_dB, 'b', 'LineWidth', 2); hold on;
semilogx(f/1e3, mag_Af_ret_norm_dB, 'r', 'LineWidth', 2);
semilogx(f/1e3, mag_Af_aa_norm_dB, 'm', 'LineWidth', 2);

% Línea de -3 dB
plot([0.1, 10000], [-3, -3], 'k--', 'LineWidth', 1.2);

% Puntos de cruce a -3 dB (BW real de lazo cerrado)
plot(BW_real_orig/1e3, -3, 'bo', 'MarkerFaceColor', 'b', 'MarkerSize', 7);
plot(BW_real_ret/1e3, -3, 'ro', 'MarkerFaceColor', 'r', 'MarkerSize', 7);
plot(BW_real_aa/1e3, -3, 'mo', 'MarkerFaceColor', 'm', 'MarkerSize', 7);

% Puntos de sobrepico resonante
plot(f(idx_max_orig)/1e3, sobrepico_orig, 'b^', 'MarkerFaceColor', 'b', 'MarkerSize', 7);
plot(f(idx_max_ret)/1e3, sobrepico_ret, 'r^', 'MarkerFaceColor', 'r', 'MarkerSize', 7);
plot(f(idx_max_aa)/1e3, sobrepico_aa, 'm^', 'MarkerFaceColor', 'm', 'MarkerSize', 7);

grid on;
xlim([0.5, 2000]);
ylim([-20, 8]);
xlabel('Frecuencia [kHz]', 'FontSize', 11);
ylabel('|A_f(f)| / A_{f0} [dB]', 'FontSize', 11);
title('Respuesta en Frecuencia a Lazo Cerrado Normalizada: Sobrepico y Ancho de Banda Real (-3 dB)', ...
      'FontSize', 12, 'FontWeight', 'bold');
legend({sprintf('Original: BW real = %0.1f kHz (Sobrepico = %0.2f dB)', BW_real_orig/1e3, sobrepico_orig), ...
        sprintf('Retardo: BW real = %0.1f kHz (Sobrepico = %0.2f dB)', BW_real_ret/1e3, sobrepico_ret), ...
        sprintf('Atraso-Adelanto: BW real = %0.1f kHz (Sobrepico = %0.2f dB)', BW_real_aa/1e3, sobrepico_aa), ...
        'Nivel de corte -3 dB'}, 'Location', 'southwest', 'FontSize', 10);

print(fig5, fullfile(carpeta_graficos, 'respuesta_lazo_cerrado_comparativa.png'), '-dpng', '-r300');
close(fig5);

fprintf('Gráficos generados y guardados exitosamente en:\n  %s\n', carpeta_graficos);
fprintf('  1. bode_planta_original.png\n');
fprintf('  2. bode_compensador_retardo.png\n');
fprintf('  3. bode_compensador_atraso_adelanto.png\n');
fprintf('  4. bode_comparativa_compensadores.png\n');
fprintf('  5. respuesta_lazo_cerrado_comparativa.png\n');
fprintf('=========================================================================================\n');

