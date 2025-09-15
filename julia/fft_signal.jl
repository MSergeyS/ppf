function fft_signal(s::Vector{Float64}, t::Vector{Float64})
    # спектр сигнала
    fft_s = fft(s);

    # Функция `fftshift` позволяет представить выход БПФ в привычном виде спектра, в нашем случае симметричного относительно центра - нулевой частоты. Но нам также придётся отложить по оси абсцисс вектор дискретных частот в пределах от -fs/2 до fs/2:
    fft_s = fftshift(fft_s);
    # длина сигнала
    nsamp = length(t);
    # частота дискретизации
    fs = Float64(1/(t[2]-t[1]));
    # частотный шаг
    df = Float64(fs/nsamp);
    fft_s = fft_s/N; # нормировка амплитуды
    println("Частота дискретизации = ", round(fs/1e6), "  МГц")
    println("Разрешение по частоте = ", round(df), "  Гц")

    # fs — частота дискретизации
    # nsamp — длина сигнала (или БПФ)
    freq_vec = -fs/2:fs/(nsamp-1):fs/2

    # print(length(freq_vec), '\n')
    # print(length(fft_s), '\n')
    # plot(freq_vec/1e6, abs.(fft_s), xlabel="f, MHz", ylabel="U,V", title="Спектр сигнала (fft)", legend=false)

    return fft_s, nsamp, fs, df, freq_vec
end
