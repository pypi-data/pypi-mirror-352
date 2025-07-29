import numpy as np
import torch
from tqdm import tqdm

# Add device variable to use gpu (incl mps) if available
device = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "mps" if torch.backends.mps.is_available() else "cpu"
)


def reweight(
    original_weights,
    loss_matrix,
    targets_array,
    dropout_rate=0.1,
    epochs=2_000,
    noise_level=10.0,
    subsample_every=50,
    learning_rate=1e-3,
):
    target_names = np.array(loss_matrix.columns)
    loss_matrix = torch.tensor(
        loss_matrix.values, dtype=torch.float32, device=device
    )
    original_indices = np.arange(loss_matrix.shape[0])

    targets_array = torch.tensor(
        targets_array, dtype=torch.float32, device=device
    )
    random_noise = np.random.random(original_weights.shape) * noise_level
    weights = torch.tensor(
        np.log(original_weights + random_noise),
        requires_grad=True,
        dtype=torch.float32,
        device=device,
    )

    def loss(weights):
        estimate = weights @ loss_matrix
        rel_error = (
            ((estimate - targets_array) + 1) / (targets_array + 1)
        ) ** 2
        return rel_error.mean()

    def dropout_weights(weights, p):
        if p == 0:
            return weights
        total_weight = weights.sum()
        mask = torch.rand_like(weights) < p
        masked_weights = weights.clone()
        masked_weights[mask] = 0
        masked_weights = masked_weights / masked_weights.sum() * total_weight
        return masked_weights

    optimizer = torch.optim.Adam([weights], lr=learning_rate)

    iterator = tqdm(range(epochs), desc="Reweighting progress", unit="epoch")

    for i in iterator:
        optimizer.zero_grad()
        running_loss = None
        for j in range(2):
            weights_ = dropout_weights(weights, dropout_rate)
            l = loss(torch.exp(weights_))
            if running_loss is None:
                running_loss = l
            else:
                running_loss += l
        l = running_loss / 2

        if i % 10 == 0:
            iterator.set_postfix(
                {
                    "loss": l.item(),
                    "count_observations": loss_matrix.shape[0],
                    "weights_mean": torch.exp(weights).mean().item(),
                    "weights_std": torch.exp(weights).std().item(),
                    "weights_min": torch.exp(weights).min().item(),
                }
            )

        l.backward()
        optimizer.step()

        if subsample_every > 0 and i % subsample_every == 0 and i > 0:
            weight_values = np.exp(weights.detach().cpu().numpy())

            k = 100
            # indices = indices of weights with values < 1
            indices = np.where(weight_values >= k)[0]
            loss_matrix = loss_matrix[indices, :]
            weights = weights[indices]

            loss_matrix = torch.tensor(
                loss_matrix.detach().cpu(), dtype=torch.float32, device=device
            )
            weights = torch.tensor(
                weights.detach().cpu(),
                dtype=torch.float32,
                device=device,
                requires_grad=True,
            )

            original_indices = original_indices[indices]
            optimizer = torch.optim.Adam([weights], lr=learning_rate)

    return torch.exp(weights).detach().cpu().numpy(), original_indices
