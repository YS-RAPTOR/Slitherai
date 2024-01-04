from stable_baselines3.common.callbacks import (
    CallbackList,
    CheckpointCallback,
    EvalCallback,
)
import torch as th
from Slitherai.Environment.Constants import OPTIMAL_RESOLUTION_WIDTH
import wandb
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env.vec_monitor import VecMonitor
from stable_baselines3.common.vec_env.vec_normalize import VecNormalize
from wandb.integration.sb3 import WandbCallback

from Slitherai.AI.AIEnv import AIEnv

USE_WANDB = True


class TestRun:
    def __init__(self, id: str):
        self.id = id

    def finish(self):
        pass


config = {
    "policy_type": "MlpPolicy",
    "number_of_agents": 10,
    "world_size": 7500,
    "food_to_spawn": 100,
    "total_timesteps": 10_000_000,
    "learning_rate": 3e-3,
    "n_steps": 2048,
    "batch_size": 64,
    "n_epochs": 10,
    "gamma": 0.99,
    "gae_lambda": 0.95,
    "clip_range": 0.2,
    "ent_coef": 0.0,
    "vf_coef": 0.5,
    "max_grad_norm": 0.5,
    "policy_kwargs": {
        "activation_fn": th.nn.ReLU,
        "net_arch": {
            "vf": [256, 256],
            "pi": [256, 256],
        },
    },
}


def main():
    env = VecNormalize(
        VecMonitor(
            AIEnv(
                config["number_of_agents"],
                config["world_size"],
                6000,
                config["food_to_spawn"],
            )
        ),
        clip_obs=OPTIMAL_RESOLUTION_WIDTH,
    )
    eval_env = VecNormalize(
        VecMonitor(
            AIEnv(
                config["number_of_agents"] // 2,
                config["world_size"] // 2,
                1500,
                config["food_to_spawn"] // 2,
            )
        ),
        clip_obs=OPTIMAL_RESOLUTION_WIDTH,
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
        learning_rate=config["learning_rate"],
        n_steps=config["n_steps"],
        batch_size=config["batch_size"],
        n_epochs=config["n_epochs"],
        gamma=config["gamma"],
        gae_lambda=config["gae_lambda"],
        clip_range=config["clip_range"],
        ent_coef=config["ent_coef"],
        vf_coef=config["vf_coef"],
        max_grad_norm=config["max_grad_norm"],
        tensorboard_log=f"runs/{run.id}",
        device="cuda",
        policy_kwargs=config["policy_kwargs"],
    )

    eval_callback = EvalCallback(eval_env, eval_freq=10000)
    checkpoint_callback = CheckpointCallback(
        save_freq=5000, save_path=f"models/{run.id}"
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
            callbaks = CallbackList(
                [eval_callback, wandb_callback, checkpoint_callback]
            )

            model.learn(
                total_timesteps=config["total_timesteps"],
                progress_bar=True,
                callback=callbaks,
            )
            run.finish()
        else:
            callbaks = CallbackList([eval_callback, checkpoint_callback])
            model.learn(
                total_timesteps=config["total_timesteps"],
                progress_bar=True,
                callback=callbaks,
            )
    except KeyboardInterrupt:
        pass

    model.save(f"models/finished/{run.id}")
    env.save(f"models/finished/{run.id}-vec_normalize")


if __name__ == "__main__":
    main()
