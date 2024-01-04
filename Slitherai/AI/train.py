from stable_baselines3.common.callbacks import (
    CallbackList,
    CheckpointCallback,
    EvalCallback,
)
import torch as th
import wandb
from stable_baselines3 import A2C
from stable_baselines3.common.vec_env.vec_monitor import VecMonitor
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
    "food_to_spawn": 50,
    "total_timesteps": 1_000_000,
    "learning_rate": 7e-4,
    "n_steps": 5,
    "gamma": 0.99,
    "gae_lambda": 1.0,
    "ent_coef": 0.0,
    "vf_coef": 0.5,
    "max_grad_norm": 0.5,
    "rms_prop_eps": 1e-5,
    "use_rms_prop": True,
    "policy_kwargs": {
        "activation_fn": th.nn.ReLU,
        "net_arch": {
            "vf": [256, 256],
            "pi": [256, 256],
        },
    },
}


def main():
    env = VecMonitor(
        AIEnv(
            config["number_of_agents"],
            config["world_size"],
            6000,
            config["food_to_spawn"],
        )
    )
    eval_env = VecMonitor(
        AIEnv(
            config["number_of_agents"] // 2,
            config["world_size"] // 2,
            1500,
            config["food_to_spawn"] // 2,
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

    model = A2C(
        config["policy_type"],
        env,
        verbose=1,
        learning_rate=config["learning_rate"],
        n_steps=config["n_steps"],
        gamma=config["gamma"],
        gae_lambda=config["gae_lambda"],
        ent_coef=config["ent_coef"],
        vf_coef=config["vf_coef"],
        max_grad_norm=config["max_grad_norm"],
        rms_prop_eps=config["rms_prop_eps"],
        use_rms_prop=config["use_rms_prop"],
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
