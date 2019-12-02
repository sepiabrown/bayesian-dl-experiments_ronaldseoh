import torch
import numpy as np

from .fcnet import FCNet


class FCNetMCDropout(FCNet):

    def __init__(self, input_dim, output_dim, hidden_dim, n_hidden,
                 dropout_rate, dropout_type):

        super(FCNetMCDropout, self).__init__(
            input_dim=input_dim, output_dim=output_dim, hidden_dim=hidden_dim,
            n_hidden=n_hidden,
            dropout_rate=dropout_rate, dropout_type=dropout_type)

    def predict_dist(self, X_test, n_predictions, **kwargs):
        if 'y_mean' in kwargs:
            y_mean = kwargs['y_mean']
            y_std = kwargs['y_std']
        else:
            y_mean = 0
            y_std = 1

        was_eval = not self.training

        # Temporaily disable eval mode
        if was_eval:
            self.train()

        predictions = torch.stack(
            [self.forward(X_test) for _ in range(n_predictions)])

        predictions = predictions * y_std + y_mean

        if was_eval:
            self.eval()

        # No gradient tracking necessary
        with torch.no_grad():
            mean = torch.mean(predictions, 0)
            var = torch.var(predictions, 0)

            # If y_test is given, calculate RMSE and test log-likelihood
            metrics = {}

            if 'y_test' in kwargs:
                y_test = kwargs['y_test']
                y_test = y_test * y_std + y_mean

                reg_strength = torch.tensor(kwargs['reg_strength'], dtype=torch.float)

                # RMSE
                metrics['rmse_mc'] = torch.sqrt(torch.mean(torch.pow(y_test - mean, 2)))

                # RMSE (Non-MC)
                prediction_non_mc = self.forward(X_test)
                prediction_non_mc = prediction_non_mc * y_std + y_mean
                metrics['rmse_non_mc'] = torch.sqrt(torch.mean(torch.pow(y_test - prediction_non_mc, 2)))

                # test log-likelihood
                metrics['test_ll_mc'] = torch.mean(
                    torch.logsumexp(- torch.tensor(0.5) * reg_strength * torch.pow(y_test[None] - predictions, 2), 0)
                    - torch.log(torch.tensor(n_predictions, dtype=torch.float))
                    - torch.tensor(0.5) * torch.log(torch.tensor(2 * np.pi, dtype=torch.float))
                    + torch.tensor(0.5) * torch.log(reg_strength)
                )

        return predictions, mean, var, metrics
