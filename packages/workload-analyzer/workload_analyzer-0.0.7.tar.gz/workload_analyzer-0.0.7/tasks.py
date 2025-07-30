from invoke import task, Context
from pathlib import Path


@task
def tests(ctx: Context) -> None:
    """Test and coverage."""
    ctx.run("uv run coverage run -m pytest tests/ -v", echo=True)
    ctx.run("uv run coverage report -i -m", echo=True)


@task
def clone_examples(ctx: Context) -> None:
    """Clone the examples repository."""
    if Path("examples").exists() and Path("examples").is_dir():
        ctx.run("cd examples && git pull", echo=True)
    else:
        ctx.run("git clone https://github.com/pytorch/examples", echo=True)


@task(clone_examples)
def mnist_workload(ctx: Context, epochs: int = 14, batch_size: int = 64) -> None:
    """Run MNIST workload."""
    ctx.run(
        f"uv run workload-analyzer 'uv run examples/mnist/main.py --batch-size {batch_size} --epochs {epochs}'",
        echo=True,
        pty=True,
    )


@task(clone_examples)
def vae_workload(ctx: Context, epochs: int = 10, batch_size: int = 128, clean: bool = True) -> None:
    """Run VAE workload."""
    ctx.run("mkdir -p results", echo=True)
    ctx.run(
        f"uv run workload-analyzer 'uv run examples/vae/main.py --batch-size {batch_size} --epochs {epochs}'",
        echo=True,
        pty=True,
    )
    if clean:
        ctx.run("rm -rf results", echo=True)


@task(clone_examples)
def gat_workload(ctx: Context, epochs: int = 300, clean: bool = True) -> None:
    """Run GAT workload."""
    ctx.run(f"uv run workload-analyzer 'uv run examples/gat/main.py --epochs {epochs}'", echo=True, pty=True)
    if clean:
        ctx.run("rm -rf cora", echo=True)
