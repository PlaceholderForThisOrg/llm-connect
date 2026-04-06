class BKTEngine:
    def run(
        p_L: float,
        correct: float,
        p_guess: float,
        p_slip: float,
        p_learn: float,
    ) -> float:
        if correct:
            numerator = p_L * (1 - p_slip)
            denominator = numerator + (1 - p_L) * p_guess
        else:
            numerator = p_L * p_slip
            denominator = numerator + (1 - p_L) * (1 - p_guess)

        p_L_given_obs = numerator / denominator
        p_L_new = p_L_given_obs + (1 - p_L_given_obs) * p_learn

        return p_L_new
