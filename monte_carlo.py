"""Monte Carlo comparison of simple bankroll staking strategies."""

from __future__ import annotations

import argparse
import csv
import random
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class Strategy(str, Enum):
    FLAT = "flat"
    DALEMBERT = "dalembert"
    MARTINGALE = "martingale"


@dataclass(frozen=True)
class TrialResult:
    final_balance: float
    busted: bool


@dataclass(frozen=True)
class Summary:
    strategy: Strategy
    trials: int
    mean_final_balance: float
    median_final_balance: float
    bust_rate: float
    profit_rate: float


def _validate_inputs(starting_balance, base_bet, rounds, win_probability):
    if starting_balance <= 0 or base_bet <= 0:
        raise ValueError("starting_balance and base_bet must be positive")
    if base_bet > starting_balance:
        raise ValueError("base_bet cannot exceed starting_balance")
    if rounds <= 0:
        raise ValueError("rounds must be positive")
    if not 0.0 <= win_probability <= 1.0:
        raise ValueError("win_probability must lie in [0, 1]")


def simulate_trial(
    strategy: Strategy,
    starting_balance: float,
    base_bet: float,
    rounds: int,
    win_probability: float,
    rng: random.Random,
) -> TrialResult:
    """Simulate one trial of a one-to-one payout game."""

    _validate_inputs(starting_balance, base_bet, rounds, win_probability)
    balance = starting_balance
    bet = base_bet
    for _ in range(rounds):
        bet = min(bet, balance)
        won = rng.random() < win_probability
        if won:
            balance += bet
            if strategy == Strategy.DALEMBERT:
                bet = max(base_bet, bet - base_bet)
            elif strategy == Strategy.MARTINGALE:
                bet = base_bet
        else:
            balance -= bet
            if balance <= 0:
                return TrialResult(final_balance=0.0, busted=True)
            if strategy == Strategy.DALEMBERT:
                bet += base_bet
            elif strategy == Strategy.MARTINGALE:
                bet *= 2.0

    return TrialResult(final_balance=balance, busted=False)


def run_simulation(
    strategy: Strategy,
    trials: int = 10_000,
    starting_balance: float = 10_000.0,
    base_bet: float = 100.0,
    rounds: int = 100,
    win_probability: float = 0.5,
    seed: int | None = 7,
) -> list[TrialResult]:
    """Run independent trials with an optional deterministic seed."""

    if trials <= 0:
        raise ValueError("trials must be positive")
    rng = random.Random(seed)
    return [
        simulate_trial(strategy, starting_balance, base_bet, rounds, win_probability, rng)
        for _ in range(trials)
    ]


def summarise(strategy: Strategy, results: list[TrialResult], starting_balance: float = 10_000.0) -> Summary:
    """Aggregate trial outcomes into review-friendly statistics."""

    if not results:
        raise ValueError("results cannot be empty")
    balances = sorted(result.final_balance for result in results)
    midpoint = len(balances) // 2
    median = balances[midpoint] if len(balances) % 2 else (balances[midpoint - 1] + balances[midpoint]) / 2.0
    return Summary(
        strategy=strategy,
        trials=len(results),
        mean_final_balance=sum(balances) / len(balances),
        median_final_balance=median,
        bust_rate=sum(result.busted for result in results) / len(results),
        profit_rate=sum(result.final_balance > starting_balance for result in results) / len(results),
    )


def write_results(path: Path, summaries: list[Summary]) -> None:
    """Write summary statistics to a CSV file."""

    with path.open("w", newline="") as output:
        writer = csv.writer(output)
        writer.writerow(["strategy", "trials", "mean_final_balance", "median_final_balance", "bust_rate", "profit_rate"])
        for summary in summaries:
            writer.writerow([
                summary.strategy.value,
                summary.trials,
                f"{summary.mean_final_balance:.6f}",
                f"{summary.median_final_balance:.6f}",
                f"{summary.bust_rate:.6f}",
                f"{summary.profit_rate:.6f}",
            ])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trials", type=int, default=10_000)
    parser.add_argument("--rounds", type=int, default=100)
    parser.add_argument("--starting-balance", type=float, default=10_000.0)
    parser.add_argument("--base-bet", type=float, default=100.0)
    parser.add_argument("--win-probability", type=float, default=0.5)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    summaries = []
    for strategy in Strategy:
        results = run_simulation(strategy, args.trials, args.starting_balance, args.base_bet, args.rounds, args.win_probability, args.seed)
        summaries.append(summarise(strategy, results, args.starting_balance))

    print(f"{'strategy':<12} {'mean balance':>15} {'median':>15} {'bust rate':>12} {'profit rate':>13}")
    for summary in summaries:
        print(f"{summary.strategy.value:<12} {summary.mean_final_balance:>15.2f} {summary.median_final_balance:>15.2f} {summary.bust_rate:>11.2%} {summary.profit_rate:>12.2%}")
    if args.output:
        write_results(args.output, summaries)


if __name__ == "__main__":
    main()
