# структура параметров ЗИ (файл *.dds)
mutable struct ParametersMode
    sig1::UInt32
    sig2::UInt32
    version::UInt16
    rec_type::UInt16
    size_file::UInt32
    Code_ZI::UInt16
    Mode::UInt8
    Mode1::UInt8
    TimeZ::UInt16
    NumPrd::UInt32
    TimeR::UInt16
    TimeI::UInt16
    CRC::UInt16
    Prm0::UInt32
    Prm1::UInt32
    Ver::UInt8
    Type::UInt8
    Name_RU::String
    Name_EN::String
    StartFreq::Float64
    EndFreq::Float64
    TimeZI::Float64
    Fs::Float64
    SampleType::UInt8
    Rzv2::UInt8
    NumCC::UInt16
    Rzv3::UInt16
    s::Vector{Float64}
    t::Vector{Float64}
    CC::Vector{UInt16}
end

function reader_dds(file_name::String, fclk)
    Tclk = 1 / fclk # период дескретизации (тактовая частота ПЛИС)

    mode = ParametersMode(
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "", "", 0.0, 0.0, 0.0, 0.0, 0, 0, 0, 0,
        Float64[], Float64[], UInt16[]
    )

    open(file_name, "r") do io
        # Чтение заголовка (struct DDS_HDR 16 байт)
        mode.sig1      = read(io, UInt32)
        mode.sig2      = read(io, UInt32)
        mode.version   = read(io, UInt16)
        mode.rec_type  = read(io, UInt16) # код типа данных записи в заголовке = 0201h – признак файла DDS
        mode.size_file = read(io, UInt32)

        # Чтение параметров ЗИ (struct gPRM_ZI // Размер структуры = 16+128 = 144 байта)
        mode.Code_ZI   = read(io, UInt16)
        mode.Mode      = read(io, UInt8)
        mode.Mode1     = read(io, UInt8)
        mode.TimeZ     = read(io, UInt16)
        mode.NumPrd    = read(io, UInt32)
        mode.TimeR     = read(io, UInt16)
        mode.TimeI     = read(io, UInt16)
        mode.CRC       = read(io, UInt16)
        mode.Prm0      = read(io, UInt32)
        mode.Prm1      = read(io, UInt32)
        mode.Ver       = read(io, UInt8)
        mode.Type      = read(io, UInt8)

        bytes = Vector{UInt8}(undef, 40) # если строка 20 символов по 2 байта
        read!(io, bytes)
        mode.Name_RU   = String(bytes) # строка UNICODE – до 19 символов
        bytes = Vector{UInt8}(undef, 40)
        read!(io, bytes)
        mode.Name_EN   = String(bytes) # строка UNICODE – до 19 символов

        mode.StartFreq = read(io, Float64)
        mode.EndFreq   = read(io, Float64)
        mode.TimeZI    = read(io, Float64)
        mode.Fs        = read(io, Float64)
        mode.SampleType= read(io, UInt8)
        mode.Rzv2      = read(io, UInt8)
        mode.NumCC     = read(io, UInt16)
        mode.Rzv3      = read(io, UInt16)

        # Чтение КУ (команд управления) - массив из NumCC элементов типа UInt16
        mode.CC = Vector{UInt16}(undef, mode.NumCC)
        read!(io, mode.CC)

        # Инициализация выходных данных
        mode.s = Float64[]
        mode.t = Float64[]

        # Формирование сигнала по КУ (требует отдельной функции)
        mode.s = cc2s_mode5(mode.CC)
        mode.t = collect(0:Tclk:(length(mode.s)-1)*Tclk)
    end

    # Возврат параметров с сигналом
    return mode
end

function print_info(pm::ParametersMode)
    println("sig1: 0x", hex(pm.sig1))
    println("sig2: 0x", hex(pm.sig2))
    println("version: 0x", hex(pm.version))
    println("rec_type: 0x", hex(pm.rec_type))
    println("size_file: ", pm.size_file)
    println("Code_ZI: ", pm.Code_ZI)
    println("Mode: ", pm.Mode)
    println("Mode1: ", pm.Mode1)
    println("TimeZ: ", pm.TimeZ)
    println("NumPrd: ", pm.NumPrd)
    println("TimeR: ", pm.TimeR)
    println("TimeI: ", pm.TimeI)
    println("CRC: ", pm.CRC)
    println("Prm0: ", pm.Prm0)
    println("Prm1: ", pm.Prm1)
    println("Ver: ", pm.Ver)
    println("Type: ", pm.Type)
    # println("Name_RU: ", pm.Name_RU)
    println("Name_EN: ", pm.Name_EN)
    println("StartFreq: ", pm.StartFreq)
    println("EndFreq: ", pm.EndFreq)
    println("TimeZI: ", pm.TimeZI)
    println("Fs: ", pm.Fs)
    println("SampleType: ", pm.SampleType)
    println("Rzv2: ", pm.Rzv2)
    println("NumCC: ", pm.NumCC)
    println("Rzv3: ", pm.Rzv3)
    # println("CC: ", pm.CC)
    # println("s: ", pm.s)
    # println("t: ", pm.t)
end

function hex(value)
    return string(value, base=16)
end

using Plots

function plot_signal(mode::ParametersMode)
    plot(1e6*mode.t, mode.s, xlabel="Время, мкс", ylabel="Амплитуда", title="Сигнал из DDS", legend=false, grid=true)
end

function cc2s_mode5(CC::Vector{UInt16})
    # Преобразование массива команд управления -КУ (CC) в сигнал -signal (s) 
    signal = Float64[]
    try
        for k in 1:length(CC)
            if CC[k] == 511 # если 511, то стоп (конец сигнала) 
                break
            end
            # Переведём КУ в вектор битов
            bits = [parse(Int, c) for c in bitstring(CC[k])]
            # Уровень сигнала в КУ (если нечётные команды то 0, если чётные - фаза (1 или -1))
            s = (k%2 == 1) ? 0.0 : (bits[8] == 0 ? 1.0 : -1.0)
            # Формируем длительность интервала времени T из битов КУ
            if (k%2 != 1) # в КУ фазы зануляем бит типа фазы
                bits[8] = 0
            end
            # длительность интервала времени T из битов КУ (переводит последовательность бит в UInt16)
            bin_str = join(bits)
            T_val = parse(UInt16, bin_str; base=2) + 2
            # Формируем сигнал: добавляем последовательность из T_val бит со значением s
            append!(signal, [s for i in 1:T_val])
        end
        signal = vcat(signal, 0.0 .* ones(Int, 1000)) # добавляем 0 в конец сигннала

    catch err
        rethrow(err)
    end

    return signal

end