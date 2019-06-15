from rl.algorithm import Algorithm
from rl.models import *
from rl.utils import *

class PG(Algorithm):
    def setup(self):
        self.name = 'PG'

        self.policy = Model(CategoricalPolicy(self.env), 1e-3)

    def interact(self, s):
        a = self.policy(s)
        s2, r, done, _ = self.env.step(a)
        data = (s, a, r, done)
        return s2, r, done, data

    def update(self, storage):
        s, a, r, m = storage.get_all()

        # calculate returns
        returns = [0] * len(r)
        discounted_next = 0
        for i in reversed(range(len(r))):
            returns[i] = r[i] + discounted_next
            discounted_next = 0.99 * returns[i] * m[i - 1]

        # normalize returns
        returns = torch.FloatTensor(returns)
        mean = returns.mean()
        std = returns.std()
        returns = (returns - mean) / (std + 1e-6)

        # calculate log probabilities
        log_p = self.policy.log_prob(s, a)

        # update policy
        loss = -(returns * log_p).mean()
        self.policy.optimize(loss)

        # clear history
        storage.clear()