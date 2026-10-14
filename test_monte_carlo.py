import unittest

from monte_carlo import Strategy, run_simulation, simulate_trial, summarise


class MonteCarloTests(unittest.TestCase):
    def test_zero_win_probability_eventually_busts(self):
        result = simulate_trial(Strategy.FLAT, 100.0, 10.0, 20, 0.0, __import__("random").Random(1))
        self.assertTrue(result.busted)
        self.assertEqual(result.final_balance, 0.0)

    def test_one_win_probability_never_loses_money(self):
        results = run_simulation(Strategy.MARTINGALE, trials=20, starting_balance=100.0, base_bet=10.0, rounds=10, win_probability=1.0, seed=1)
        self.assertTrue(all(not result.busted for result in results))
        self.assertTrue(all(result.final_balance > 100.0 for result in results))

    def test_seed_makes_runs_reproducible(self):
        first = run_simulation(Strategy.DALEMBERT, trials=20, seed=42)
        second = run_simulation(Strategy.DALEMBERT, trials=20, seed=42)
        self.assertEqual(first, second)

    def test_summary_contains_rates_between_zero_and_one(self):
        summary = summarise(Strategy.FLAT, run_simulation(Strategy.FLAT, trials=100, seed=42))
        self.assertGreaterEqual(summary.bust_rate, 0.0)
        self.assertLessEqual(summary.bust_rate, 1.0)
        self.assertGreaterEqual(summary.profit_rate, 0.0)
        self.assertLessEqual(summary.profit_rate, 1.0)


if __name__ == "__main__":
    unittest.main()
