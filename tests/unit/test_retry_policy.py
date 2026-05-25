from packages.echochamber.providers.retry import ProviderRetryPolicy


class Counter:
    def __init__(self):
        self.calls = 0


def test_retry_policy_recovers():
    counter = Counter()
    retry = ProviderRetryPolicy(attempts=3)

    def operation():
        counter.calls += 1

        if counter.calls < 2:
            raise RuntimeError('temporary')

        return 'ok'

    result = retry.run(operation)

    assert result == 'ok'
    assert counter.calls == 2
