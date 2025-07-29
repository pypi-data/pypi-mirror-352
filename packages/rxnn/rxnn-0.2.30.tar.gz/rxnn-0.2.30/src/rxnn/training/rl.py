import torch
import torch.nn as nn
import torch.nn.functional as F
from abc import ABC, abstractmethod
from typing import TypedDict
from .utils import TokenizedDict


class RlAlgorithm(ABC):
    def __init__(self):
        super(RlAlgorithm, self).__init__()
        self.critic_loss = nn.MSELoss()

    @abstractmethod
    def policy_loss(self, query: TokenizedDict, answer: TokenizedDict, logits: torch.Tensor,
                    old_log_probs: torch.Tensor, advantages: torch.Tensor) -> torch.Tensor:
        pass

    @abstractmethod
    def calculate_advantages(self, rewards: torch.Tensor, values: torch.Tensor, dones: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        pass

    def critic_loss(self, rewards: torch.Tensor, values: torch.Tensor) -> torch.Tensor:
        return self.critic_loss(rewards, values)

class PPOConfig(TypedDict):
    clip_eps: float
    gae_lambda: float
    gae_gamma: float
    entropy_coef: float

class PPOAlgorithm(RlAlgorithm):
    def __init__(self, config: PPOConfig):
        super(PPOAlgorithm, self).__init__()

        # PPO Config
        self.clip_eps = config.get('clip_eps', 0.2)
        self.gae_lambda = config.get('gae_lambda', 0.95)
        self.gae_gamma = config.get('gae_gamma', 0.99)
        self.entropy_coef = config.get('entropy_coef', 0.01)

    def policy_loss(self, query: TokenizedDict, answer: TokenizedDict, logits: torch.Tensor,
                    old_log_probs: torch.Tensor, advantages: torch.Tensor) -> torch.Tensor:
        query_lens = query['attention_mask'].sum(dim=1).long()  # Query lengths per sample
        answer_mask = answer['attention_mask']
        answer_lens = answer_mask.sum(dim=1).long()  # Answer lengths per sample (before padding)

        max_length = query['input_ids'].size(1)

        combined_lens = torch.minimum(
            query_lens + answer_lens,
            torch.full_like(query_lens, max_length)
        )

        def extract_answer_tokens(tensor: torch.Tensor) -> torch.Tensor:
            B, L, *rest = tensor.size()
            result = torch.zeros((B, max_length, *rest), dtype=tensor.dtype, device=tensor.device)

            for i in range(B):
                s = query_lens[i].item()
                e = combined_lens[i].item()
                valid_len = e - s
                if valid_len > 0:
                    result[i, :valid_len] = tensor[i, s:e]
            return result

        new_logits = extract_answer_tokens(logits)

        # a) Get new log probs
        new_probs = F.log_softmax(new_logits, dim=-1)
        new_log_probs = new_probs.gather(-1, answer['input_ids'].unsqueeze(-1)).squeeze(-1)

        new_log_probs = extract_answer_tokens(new_log_probs.unsqueeze(-1)).squeeze(-1)  # Ensure 3D for extraction (add singleton dim)

        # b) Calculate ratio
        ratio = (new_log_probs - old_log_probs).exp()

        advantages = advantages.unsqueeze(-1)

        # c) Clipped surrogate loss
        surr1 = ratio * advantages
        surr2 = torch.clamp(ratio, 1.0 - self.clip_eps, 1.0 + self.clip_eps) * advantages
        policy_loss = -torch.min(surr1, surr2).mean()

        # d) Entropy bonus
        entropy = -torch.sum(new_probs * new_probs.exp(), dim=-1).mean()
        policy_loss -= self.entropy_coef * entropy

        return policy_loss

    def _compute_gae(self, rewards: torch.Tensor, values: torch.Tensor, next_value: torch.Tensor, dones: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        T, B = rewards.shape
        advantages = torch.zeros_like(rewards, device=values.device)
        last_advantage = 0
        last_value = next_value.detach()

        for t in reversed(range(T)):
            if t == T - 1:
                next_values = last_value
            else:
                next_values = values[t + 1]

            # Mask next values if episode ended
            next_values = next_values * (1 - dones[t])
            delta = rewards[t] + self.gae_gamma * next_values - values[t]
            advantages[t] = delta + self.gae_gamma * self.gae_lambda * last_advantage
            last_advantage = advantages[t]

        returns = advantages + values
        return advantages, returns

    def calculate_advantages(self, rewards: torch.Tensor, values: torch.Tensor, dones: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        advantages, ref_values = self._compute_gae(rewards[:-1], values[:-1], values[-1], dones[:-1])
        normalized_advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
        return normalized_advantages, ref_values
