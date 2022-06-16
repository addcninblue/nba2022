using DataFrames
using Turing
using ReverseDiff
using LinearAlgebra
using CSV
using Plots
using Memoization

Turing.setadbackend(:reversediff)
Turing.setrdcache(true)
gr()

df = DataFrame(CSV.File("all_processed_mid.csv"))
players = unique(vcat([df[:,i] for i in 1:10]...))

# θ_home ~ home + sum(att_home) - sum(def_away)
# θ_away ~ sum(att_away) - sum(def_home)
# where att_home = sum(att_i) for each player i
#       def_home = sum(def_i) for each player i
# att_i ~ N(μ_att, σ_att)
# def_i ~ N(μ_def, σ_def)
# μ_att, μ_def ~ N(0, 0.1)
# σ_att, σ_def ~ Exp(1)
# home ~ N(0, 1)
# subject to ∑att_i = 0, ∑def_i = 0

@model function basketball_segments(
    player1_home, player2_home, player3_home, player4_home, player5_home,
    player1_away, player2_away, player3_away, player4_away, player5_away,
    score_home, score_away, players)
    # hyper priors
    μ_att ~ Normal(0, 0.1)
    μ_def ~ Normal(0, 0.1)
    σ_att ~ Exponential(1)
    σ_def ~ Exponential(1)

    home ~ Normal(0, 1)

    # player-specific
    att ~ filldist(Normal(μ_att, σ_att), length(players))
    def ~ filldist(Normal(μ_def, σ_def), length(players))

    # back-map
    dict = Dict{String, Int64}()
    for (i, player) in enumerate(players)
        dict[player] = i
    end

    # zero-sum
    offset = mean(att) + mean(def)

    log_θ_home = Vector{Real}(undef, length(player1_home))
    log_θ_away = Vector{Real}(undef, length(player1_home))

    for i in 1:length(score_home)
        log_θ_home[i] = home
                + att[dict[player1_home[i]]] + att[dict[player2_home[i]]] + att[dict[player3_home[i]]] + att[dict[player4_home[i]]] + att[dict[player5_home[i]]]
                - def[dict[player1_away[i]]] - def[dict[player2_away[i]]] - def[dict[player3_away[i]]] - def[dict[player4_away[i]]] - def[dict[player5_away[i]]]
                - offset

        log_θ_away[i] =
                  att[dict[player1_away[i]]] + att[dict[player2_away[i]]] + att[dict[player3_away[i]]] + att[dict[player4_away[i]]] + att[dict[player5_away[i]]]
                - def[dict[player1_home[i]]] - def[dict[player2_home[i]]] - def[dict[player3_home[i]]] - def[dict[player4_home[i]]] - def[dict[player5_home[i]]]
                - offset

        score_home[i] ~ LogPoisson(log_θ_home[i])
        score_away[i] ~ LogPoisson(log_θ_away[i])
    end
end

model = basketball_segments(
    df[:,1],
    df[:,2],
    df[:,3],
    df[:,4],
    df[:,5],
    df[:,6],
    df[:,7],
    df[:,8],
    df[:,9],
    df[:,10],
    df[:,11],
    df[:,12],
    players
)

posterior = sample(model, NUTS(), 3000)

# post_att = collect(get(posterior, :att)[1])
# post_def = collect(get(posterior, :def)[1])
# post_home = collect(get(posterior, :home)[1])
# # players
# hcat(post_att)
# histogram(post_home, legend=false, title="Posterior Distribution of home parameter.")

write("player_analysis_mid.jls", posterior)
