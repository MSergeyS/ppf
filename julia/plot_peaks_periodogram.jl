"""
    plot_peaks_periodogram(p_test; freq_limit::Real=100_000, height::Real=-120, prominence::Real=2, width::Real=1)

Plots the periodogram of the signal `p_test`, detects peaks in the spectrum, and highlights them.

# Arguments
- `p_test`: Signal or periodogram data (type depends on the context, typically an array or a custom signal type).
- `freq_limit::Real`: Upper frequency limit for peak detection (default: 100_000).
- `height::Real`: Minimum height (in dB) for a peak to be detected (default: -120).
- `prominence::Real`: Minimum prominence for a peak to be detected (default: 2).
- `width::Real`: Minimum width for a peak to be detected (default: 1).

# Description
- Computes the power spectrum in dB.
- Finds peaks in the spectrum below `freq_limit` using the specified criteria.
- Prints indices, frequencies (in kHz), and amplitudes (in dB) of detected peaks.
- Plots the spectrum and highlights detected peaks.

# Returns
- The function does not return a value; it produces a plot and prints peak information.
"""
function plot_peaks_periodogram(p_test; freq_limit=100_000, height=-120, prominence=2, width=1)
    spectrum = pow2db.(power(p_test))
    fvec = freq(p_test)
    inx_limit = findall(x -> x < freq_limit, fvec)
    inx, properties = findpeaks1d(spectrum[inx_limit]; height=height, prominence=prominence, width=width)

    println("Индексы пиков: ", inx)
    println("Частоты пиков: ", fvec[inx]./1e3, " кГц")
    println("Амплитуды пиков: ", spectrum[inx], " дБ")

    max_y = maximum(spectrum[inx_limit]) + 5
    min_y = minimum(spectrum[inx_limit]) - 5

    plot(freq(p_test)/1e3, spectrum, xlabel="f, kHz", ylabel="U,dB", title="Спектр сигнала (fft)",
         legend=false, xlims=(0, freq_limit/1e3), ylims=(min_y, max_y))
    scatter!(fvec[inx]/1e3, spectrum[inx], color=:red, label="Пики")
end