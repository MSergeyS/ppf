function load_and_prepare_data(file_name::String, format_ver::Int, inx_start::Int, inx_stop::Int, downsampling_factor::Int)

    meta = Dict{String, String}()
    t = Float64[]
    s = Float64[]
    k_t = 1.0

    open(file_name, "r") do io
        cnt_str = 0
        names = String[]
        for line in eachline(io)
            fields = split(line, ',')
            if format_ver == 0
                if length(fields) >= 5 && (fields[1] != "" || fields[2] != "" || fields[3] != "")
                    meta[fields[1]] = fields[2]
                elseif length(fields) >= 5 && fields[1] == "" && fields[2] == "" && fields[3] == ""
                    push!(t, parse(Float64, fields[4]))
                    push!(s, parse(Float64, fields[5]))
                end
            elseif format_ver == 1
                if cnt_str == 0
                    names = fields
                    cnt_str += 1
                elseif cnt_str == 1
                    for i in 1:length(names)-1
                        meta[names[i]] = fields[i]
                        if (cmp(names[i], "Increment") == 0)
                            k_t = parse(Float64, fields[i])
                        end
                    end
                    cnt_str += 1
                elseif cnt_str > 1
                    push!(t, parse(Float64, fields[1])*k_t)
                    push!(s, parse(Float64, fields[2]))
                end
            end
        end
    end

    println("Считано ", length(t), " отсчётов")
    println("Частота дискретизации = ", round((1/k_t)/1e6), "  МГц")

    if downsampling_factor != 1
        s = s[inx_start:downsampling_factor:inx_stop]
        t = t[inx_start:downsampling_factor:inx_stop] .- t[inx_start]
    end

    s = s .- Statistics.mean(s, dims = 1)

    meta_info = MetaInfo(meta)
    meta_df = DataFrame(Key=collect(keys(meta_info.info)), Value=collect(values(meta_info.info)))
    println(meta_df)

    N = length(s)
    oversampling_factor = 2^16 / N
    N = length(t)
    N_new = floor(oversampling_factor * N) |> Int

    s = vcat(s, zeros(N_new - N))
    dt = t[2] - t[1]
    t = vcat(t, t[end] .+ dt .* (1:(N_new - N)))

    println("Для анализа берём ", length(t), " отсчётов")
    dt = t[2] - t[1]
    println("\nЧастота дискретизации (новая) = ", round((1/dt)/1e6), "  МГц\n")

    return t, s, meta_info, meta_df, dt, oversampling_factor, N
end
