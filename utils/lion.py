class Lion(Optimizer):
    # Based on - https://github.com/lucidrains/lion-pytorch/blob/main/lion_pytorch/lion_pytorch.py
    def __init__(self, params, lr=1e-4, betas=(0.9, 0.99), weight_decay=0.0):
        assert lr > 0.
        assert all([0. <= beta <= 1. for beta in betas])
        defaults = dict(lr=lr, betas=betas, weight_decay=weight_decay)

        super().__init__(params, defaults)

    @torch.no_grad()
    def step(self, closure=None):
        loss = None
        if closure is not None:
            with torch.enable_grad():
                loss = closure()

        for group in self.param_groups:
            for p in group['params']:

                grad = p.grad
                if grad is None:
                    continue

                state = self.state[p]
                lr, wd, beta1, beta2 = group['lr'], group['weight_decay'], *group['betas']

                # stepweight decay
                p.data.mul_(1 - lr * wd)

                # init state - exponential moving average of gradient values
                if len(state) == 0:
                    state['exp_avg'] = torch.zeros_like(p)

                exp_avg = state['exp_avg']

                # weight update
                update = exp_avg.clone().lerp_(grad, 1 - beta1)
                p.add_(torch.sign(update), alpha=-lr)

                exp_avg.lerp_(grad, 1 - beta2)

        return loss