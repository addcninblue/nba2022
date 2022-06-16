using CSV
using DataFrames
using Dates
using Plots
using StatsPlots.PlotMeasures

function process_home_away(val)
    if val === missing
        :home
    else
        :away
    end
end

function process_time_played(val)
    if !contains(val, ":")
        return missing
    end
    minutes, seconds = split(val, ":")
    minutes = parse(Int, minutes)
    seconds = parse(Int, seconds)
    minutes*60 + seconds
end

invalid_vals = ["Inactive", "Not With Team", "Did Not Play"]

function process_points(val)
    if val in invalid_vals
        return missing
    elseif typeof(val) == Int
        return val
    else
        return parse(Int, val)
    end
end

bos = Dict{String, DataFrame}()
gsw = Dict{String, DataFrame}()

for file in readdir()
    if occursin("_", file)
        # file = readdir()[2]
        println(file)
        df = DataFrame(CSV.File(file))
        df[!, "Where"] = process_home_away.(df[!, "Column6"])
        df[!, "SP"] = process_time_played.(df[!, "MP"])
        df[!, "PTS"] = process_points.(df[!, "PTS"])
        df[!, "PTSNorm30"] = df[!, "PTS"] ./ df[!, "SP"] * 30 * 60
        if df[!, "Tm"][1] == "BOS"
            bos[file] = df
        elseif df[!, "Tm"][1] == "GSW"
            gsw[file] = df
        else
            throw(ErrorException("BAD TEAM"))
        end
    end
end

team = gsw
vals = []
names = []
for (player, df) in team
    push!(vals, collect(skipmissing(df[!, "PTSNorm30"])))
    push!(names, player)
end
boxplot(vals, labels = reshape(names, 1, length(names)), left_margin=15mm, right_margin=15mm, dpi=300)
savefig("gsw.png")

team = bos
vals = []
names = []
for (player, df) in team
    push!(vals, collect(skipmissing(df[!, "PTSNorm30"])))
    push!(names, player)
end
boxplot(vals, labels = reshape(names, 1, length(names)), left_margin=15mm, right_margin=15mm, dpi=300)
savefig("bos.png")



# @df unrate.data plot(:date, :value, label="Unemployment", left_margin=15mm, right_margin=15mm, dpi=300);
# @df unrate.data plot!(:date, :value_smoothed, label="Unemployment Smoothed", left_margin=15mm, right_margin=15mm, dpi=300);
# # @df unrate.data plot(:date, :value_deriv, label="Unemployment Derivative", left_margin=15mm, right_margin=15mm, dpi=300);
# # scatter!(unrate_deriv_zeros_dates, unrate_deriv_zeros_values, label=nothing, markersize=2);
# # @df unrate.data plot!(:date, :value, label="Unemployment");
# for (s, e) in zip(starts, ends)
#     vspan!([recessions.data[!, :date][s], recessions.data[!, :date][e]], color=:gray, alpha=0.5, label=nothing)
# end
