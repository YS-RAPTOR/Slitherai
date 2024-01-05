from stable_baselines3.common.callbacks import (
    CallbackList,
    CheckpointCallback,
    EvalCallback,
)
import torch as th
import wandb
from stable_baselines3 import A2C, PPO, DQN
from stable_baselines3.common.vec_env import VecMonitor
from stable_baselines3.common.vec_env import VecNormalize, VecCheckNan
from wandb.integration.sb3 import WandbCallback
from Slitherai.Environment.Constants import OPTIMAL_RESOLUTION_WIDTH

from Slitherai.AI.AIEnv import AIEnv, AIEnvUI

USE_WANDB = False


class TestRun:
    def __init__(self, id: str):
        self.id = id

    def finish(self):
        pass


# config = {
#     "policy_type": "MlpPolicy",
#     "number_of_agents": 50,
#     "world_size": 25000,
#     "food_to_spawn": 1000,
#     "total_timesteps": 10_000_000,
#     "gamma": 0.99,
#     "normalize_advantage": False,
#     "max_grad_norm": 0.3,
#     "use_rms_prop": True,
#     "gae_lambda": 0.92,
#     "n_steps": 16,
#     "learning_rate": 0.7792897743192193,
#     "ent_coef": 0.08822977162101774,
#     "vf_coef": 0.3742976107431186,
#     "policy_kwargs": {
#         "ortho_init": True,
#         "activation_fn": th.nn.ReLU,
#         "net_arch": {
#             "vf": [1024, 1024],
#             "pi": [1024, 1024],
#         },
#     },
# }

config = {
    # World
    "total_timesteps": 1_000_000,
    "number_of_agents": 25,
    "world_size": 7500,
    "food_to_spawn": 2850,
    "max_resets": 50,
    # Algorithm
    "policy_type": "MlpPolicy",
    "learning_rate": 3e-4,
    "n_steps": 2048,
    "batch_size": 64,
    "n_epochs": 10,
    "gamma": 0.99,
    "gae_lambda": 0.95,
    "clip_range": 0.2,
    "clip_range_vf": None,
    "normalize_advantage": True,
    "ent_coef": 0.0,
    "vf_coef": 0.5,
    "max_grad_norm": 0.5,
    "policy_kwargs": {
        "activation_fn": th.nn.Tanh,
        "net_arch": {
            "vf": [64, 64],
            "pi": [64, 64],
        },
    },
}


def main():
    env = VecMonitor(
        VecCheckNan(
            AIEnvUI(
                config["number_of_agents"],
                config["world_size"],
                24000,
                config["food_to_spawn"],
                config["max_resets"],
                20,
            ),
            warn_once=False,
        )
    )

    eval_env = VecMonitor(
        VecCheckNan(
            AIEnvUI(
                config["number_of_agents"],
                config["world_size"],
                1500,
                config["food_to_spawn"],
                config["max_resets"],
                20,
            ),
            warn_once=False,
        )
    )

    if USE_WANDB:
        run = wandb.init(
            project="Slitherai",
            config=config,
            sync_tensorboard=True,
            save_code=True,
        )
        assert run is not None

    else:
        run = TestRun("test")

    model = PPO(
        config["policy_type"],
        env,
        verbose=1,
        tensorboard_log=f"runs/{run.id}",
        device="cuda",
        learning_rate=config["learning_rate"],
        n_steps=config["n_steps"],
        batch_size=config["batch_size"],
        n_epochs=config["n_epochs"],
        gamma=config["gamma"],
        gae_lambda=config["gae_lambda"],
        clip_range=config["clip_range"],
        clip_range_vf=config["clip_range_vf"],
        normalize_advantage=config["normalize_advantage"],
        ent_coef=config["ent_coef"],
        vf_coef=config["vf_coef"],
        max_grad_norm=config["max_grad_norm"],
        policy_kwargs=config["policy_kwargs"],
    )

    checkpoint_callback = CheckpointCallback(
        save_freq=1000, save_path=f"models/{run.id}"
    )

    import os

    os.makedirs("models/finished", exist_ok=True)

    try:
        if USE_WANDB:
            wandb_callback = WandbCallback(
                gradient_save_freq=500,
                model_save_path=f"models/{run.id}",
                model_save_freq=500,
                verbose=2,
            )
            callbaks = CallbackList([wandb_callback, checkpoint_callback])

            model.learn(
                total_timesteps=config["total_timesteps"],
                progress_bar=True,
                callback=callbaks,
            )
            run.finish()
        else:
            callbaks = CallbackList([checkpoint_callback])
            model.learn(
                total_timesteps=config["total_timesteps"],
                progress_bar=True,
                callback=callbaks,
            )
    except KeyboardInterrupt:
        pass

    model.save(f"models/finished/{run.id}")
    if isinstance(env, VecNormalize):
        env.save(f"models/finished/{run.id}-vec_normalize")


if __name__ == "__main__":
    main()
    main()
    main()
    main()

