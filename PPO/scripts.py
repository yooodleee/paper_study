import collections
from rich.console import Console
from rich.table import Table
import typer

from ray.air.constants import TRAINING_ITERATION
from ray.rllib import train as train_module
# PPO 알고리즘 생성
from ray.rllib.algorithms import ppo
# from ray.rllib.common import CLIArguments as cli  # CLI: YAML 파일, 제한적 커스터마이징, 유지보수 어려움(old style)
from ray.rllib.common import (
    EXAMPLES,
    FrameworkEnum,
    example_help,
    _download_example_file,
)
from ray.rllib.utils.deprecation import deprecation_warning

# Main Typer CLI app
app=typer.Typer()
example_app=typer.Typer()


# PPO 알고리즘 객체 생성
config = {"env": "CartPole-v1", "framework": "torch"}
algo = ppo.PPO(config=config)

# 학습
result = algo.train()
print(f"Training result: {result}")

# 체크포인트 저장
checkpoint_path = algo.save("checkpoints/ppo_cartpole")
print(f"Checkpoint saved at: {checkpoint_path}")

# 체크포인트 복원
algo.restore("checkpoints/ppo_cartpole")
print("Checkpoint restored successfully!")


def example_error(exapmle_id: str):
    return ValueError(
        f"Example {exapmle_id} not found. Use 'rllib example list' "
        f"to see available examples."
    )


@example_app.callback()
def example_callback():
    """RLlib command-line interface to run built-in examples. You can choose to list
    all available examples, get more information on an example or run a specific
    example.
    """
    pass


@example_app.command()
def list(
    filter: str=typer.Option(None, "--filter", "-f", help=example_help.get("filter"))
):
    """List all available RLlib examples that can be run from the command line.
    Note that many of these examples require specific hardward (e.g. a certain number
    of GPUs) to work.\n\n
    
    Example usage: 'rllib example list --filter=cartpole'
    """

    table=Table(title="RLlib Examples")
    table.add_column("Example ID", justify="left", style="cyan", no_wrap=True)
    table.add_column("Description", justify="left", style="magenta")

    sorted_examples=collections.OrderedDict(sorted(EXAMPLES.items()))

    for name, value in sorted_examples.items():
        if filter:
            if filter.lower() in name:
                table.add_row(name, value["description"])
        else:
            table.add_row(name, value["description"])
    
    console=Console()
    console.print(table)
    console.print(
        "Run any RLlib example as using 'rllib example run <Example ID>'."
        "See 'rllib example run --help' for more information."
    )


def get_example_file(example_id):
    """Simple helper function to get the example file for a given example ID."""
    if example_id not in EXAMPLES:
        raise example_error(example_id)

    example=EXAMPLES[example_id]
    assert (
        "file" in example_id.keys()
    ), f"Example {example_id} does not have a 'file' attribute."
    return example.get("file")


@example_app.command()
def get(example_id: str=typer.Argument(..., help="The example ID of the example.")):
    """Print the configuration of an example.\n\n
    Example usage: 'rllib example get atari-a2c
    """
    example_file=get_example_file(example_id)
    example_file, temp_file=_download_example_file(example_file)
    with open(example_file) as f:
        console=Console()
        console.print(f.read())


@example_app.command()
def run(example_id: str=typer.Argument(..., help="Example ID to run.")):
    """Run an RLlib example from the command line by simply providing its ID.\n\n
    
    Example usage: 'rllib example run pong-impala'
    """
    example=EXAMPLES[example_id]
    example_file=get_example_file(example_id)
    example_file, temp_file=_download_example_file(example_file)
    stop=example.get("stop")

    train_module.file(
        config_file=example_file,
        stop=stop,
        checkpoint_freq=1,
        checkpoint_at_end=True,
        keep_checkpoints_num=None,
        checkpoint_score_attr=TRAINING_ITERATION,
        framework=FrameworkEnum.tf2,
        v=True,
        vv=False,
        trace=False,
        local_mode=False,
        ray_address=None,
        ray_num_cpus=None,
        ray_num_gpus=None,
        ray_num_nodes=None,
        ray_object_store_memory=None,
        resume=False,
        scheduler="FIFO",
        scheduler_config="{}",   
    )

    if temp_file:
        temp_file.close()


# Register all subcommands
app.add_typer(example_app, name="example")
app.add_typer(train_module.train_app, name="train")


@app.command()
def evaluate(
    checkpoint: str=ppo.Checkpoint,
    algo = ppo.PPO(config=config),
    env: str=ppo.Env,
    local_mode: bool=ppo.LocalMode,
    render: bool=ppo.Render,
    steps: int=ppo.Steps,
    episodes: int=ppo.Episodes,
    out: str=ppo.Out,
    config = {"env": "CartPole-v1", "framework": "torch"},
    save_info: bool=ppo.SaveInfo,
    use_shelve: bool=ppo.UseShelve,
    track_progress: bool=ppo.TrackProgress,
):
    """Roll out a reinforcement learning agent given a checkpoint argument.
    You have to provide an environment ("--env") an an RLlib algorithm ("--algo") to
    evaluate your checkpoint.
    
    Example usage:\n\n
    
        rllib evaluate /tmp/ray/checkpoint_dir/checkpoint-0 --algo DQN --env CartPole-v1
        --steps 1000000 --out rollouts.pkl
    """
    from ray.rllib import evaluate as evaluate_module

    evaluate_module.run(
        checkpoint=checkpoint,
        algo = ppo.PPO(config=config),
        env=env,
        local_mode=local_mode,
        render=render,
        steps=steps,
        episodes=episodes,
        out=out,
        config=config,
        save_info=save_info,
        use_shelve=use_shelve,
        track_progress=track_progress,
    )


@app.command()
def rollout(
    checkpoint: str=ppo.Checkpoint,
    algo = ppo.PPO(config=config),
    env: str=ppo.Env,
    local_mode: bool=ppo.LocalMode,
    render: bool=ppo.Render,
    steps: int=ppo.Steps,
    episodes: int=ppo.Episodes,
    out: str=ppo.Out,
    config = {"env": "CartPole-v1", "framework": "torch"},
    save_infp: bool=ppo.SaveInfo,
    use_shelve: bool=ppo.UseShelve,
    track_progress: bool=ppo.TrackProgress,
):
    """Old rollout script. Please use 'rllib evaluate' instead."""
    from ray.rllib.utils.deprecation import deprecation_warning

    deprecation_warning(old="rllib rollout", new="rllib evaluate", error=True)


@app.callback()
def main_helper():
    """Welcome to the \n
    .                                                  ╔▄▓▓▓▓▄\n
    .                                                ╔██▀╙╙╙▀██▄\n
    . ╫█████████████▓   ╫████▓             ╫████▓    ██▌     ▐██   ╫████▒\n
    . ╫███████████████▓ ╫█████▓            ╫█████▓   ╫██     ╫██   ╫██████▒\n
    . ╫█████▓     ████▓ ╫█████▓            ╫█████▓    ╙▓██████▀    ╫██████████████▒\n
    . ╫███████████████▓ ╫█████▓            ╫█████▓       ╫█▒       ╫████████████████▒\n
    . ╫█████████████▓   ╫█████▓            ╫█████▓       ╫█▒       ╫██████▒    ╫█████▒\n
    . ╫█████▓███████▓   ╫█████▓            ╫█████▓       ╫█▒       ╫██████▒    ╫█████▒\n
    . ╫█████▓   ██████▓ ╫████████████████▄ ╫█████▓       ╫█▒       ╫████████████████▒\n
    . ╫█████▓     ████▓ ╫█████████████████ ╫█████▓       ╫█▒       ╫██████████████▒\n
    .                                        ╣▓▓▓▓▓▓▓▓▓▓▓▓██▓▓▓▓▓▓▓▓▓▓▓▓▄\n
    .                                        ╫██╙╙╙╙╙╙╙╙╙╙╙╙╙╙╙╙╙╙╙╙╙╙╙╫█▒\n
    .                                        ╫█  Command Line Interface █▒\n
    .                                        ╫██▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄╣█▒\n
    .                                         ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀\n
    .\n
        Example usage for training:\n
            rllib train --algo DQN --env CartPole-v1\n
            rllib train file tuned_examples/ppo/pendulum-ppo.yaml\n\n

        Example usage for evaluation:\n
            rllib evaluate /trial_dir/checkpoint_000001/checkpoint-1 --algo DQN\n\n

        Example usage for built-in examples:\n
            rllib example list\n
            rllib example get atari-ppo\n
            rllib example run atari-ppo\n
    """


def app():
    # Keep this function here, it's referenced in the setup.py file, and exposes
    # the CLI as entry point ("rllib" command).
    deprecation_warning(
        old="RLlib CLI ('rllib train' and 'rllib evaluate')",
        help="The RLlib CLI scripts will be deprecated soon! "
        "Use RLlib's python API instead, which is more flexible and offers a more "
        "unified approach to running RL experiments, evaluating policies, and "
        "creating checkpoints for later deployments. See here for a quick intro: "
        "https://docs.ray.io/en/latest/rllib/rllib-training.html#using-the-python-api",
        error=True
    )
    app()


if __name__ == "__main__":
    app()