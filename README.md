# Monte Carlo Bankroll Simulation

Reproducible Monte Carlo experiment comparing three staking strategies in a one-to-one Bernoulli game: flat betting, D’Alembert, and Martingale. It reports the distribution of final bankrolls, ruin rates, and the share of trials that finish above the starting balance.

## Why this is a useful quantitative exercise

The simulator separates a stochastic outcome model from a strategy and evaluates the strategies across thousands of independent paths. A fixed seed makes experiments repeatable, while command-line parameters make sensitivity analysis straightforward.

This is deliberately a simple 50/50 game rather than a model of a real roulette wheel. The results illustrate path dependence and risk of ruin; they do not establish a profitable betting system.

## Run it

```bash
python monte_carlo.py --trials 10000 --rounds 100 --seed 7
python monte_carlo.py --win-probability 0.49 --output results.csv
```

The optional CSV contains one row per strategy with mean and median terminal bankroll, bust rate, and profit rate.

## Tests

```bash
python -m unittest test_monte_carlo -v
```

The project uses only the Python standard library.
