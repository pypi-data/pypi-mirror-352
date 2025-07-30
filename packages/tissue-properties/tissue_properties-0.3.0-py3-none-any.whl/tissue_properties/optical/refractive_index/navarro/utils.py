from ....units import Q_

lambda_0_squared = Q_(0.028, "um^2")


def alpha_1(l: Q_) -> Q_:
    """
    alpha_1 used by Navarro, defined immediately after equation 2.

    alpha_1 - alpha_4 all have the same pattern

    alpha_x(lambda) = A + B*lambda**2 + C / (lmabda**2 - lambda_0**2) + D / (lmabda**2 - lambda_0**2)**2
    """
    l = Q_(l)

    # NOTE: there is an error in the Navarro paper, they use the coefficientes from Herzberger,
    # but there is a a typo in B.
    A = Q_(0.66147196, "")
    B = Q_(-0.40352796, "1/um^2")  # <<<< Navarro paper has -0.040352796
    C = Q_(-0.2804679, "um^2")
    D = Q_(0.03385979, "um^4")

    return (
        A
        + B * l**2
        + C / (l**2 - lambda_0_squared)
        + D / (l**2 - lambda_0_squared) ** 2
    ).to("")


def alpha_2(l: Q_) -> Q_:
    l = Q_(l)

    A = Q_(-4.20146383, "")
    B = Q_(2.73508956, "1/um^2")
    C = Q_(1.50543784, "um^2")
    D = Q_(-0.11593235, "um^4")

    return (
        A
        + B * l**2
        + C / (l**2 - lambda_0_squared)
        + D / (l**2 - lambda_0_squared) ** 2
    ).to("")


def alpha_3(l: Q_) -> Q_:
    l = Q_(l)

    A = Q_(6.29834237, "")
    B = Q_(-4.69409935, "1/um^2")
    C = Q_(-1.5750865, "um^2")
    D = Q_(0.10293038, "um^4")

    return (
        A
        + B * l**2
        + C / (l**2 - lambda_0_squared)
        + D / (l**2 - lambda_0_squared) ** 2
    ).to("")


def alpha_4(l: Q_) -> Q_:
    l = Q_(l)

    # NOTE: there is an another error in the Navarro paper, they use the coefficientes from Hrzberger,
    # but there is a a typo in A.
    A = Q_(-1.75835059, "")  # <<<< Navarro paper has +1.75835059
    B = Q_(2.36253794, "1/um^2")
    C = Q_(0.35011657, "um^2")
    D = Q_(-0.02085782, "um^4")

    return (
        A
        + B * l**2
        + C / (l**2 - lambda_0_squared)
        + D / (l**2 - lambda_0_squared) ** 2
    ).to("")


def n(n_double_star: Q_, n_F: Q_, n_c: Q_, n_star: Q_, l: Q_) -> Q_:
    return (
        alpha_1(l) * n_double_star
        + alpha_2(l) * n_F
        + alpha_3(l) * n_c
        + alpha_4(l) * n_star
    )
