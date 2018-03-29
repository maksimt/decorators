
from decorators import rate_limited, RateLimitException, cost_per_tx_s, \
    max_cost_tx_s


def test_rate_limit():

    @rate_limited()
    def f():
        return None

    for i in range(11):
        try:
            f()
        except RateLimitException as e:
            assert e.args[0]['min_wait']>=cost_per_tx_s - 0.01
            assert e.args[0]['max_wait']>=max_cost_tx_s - 0.01
